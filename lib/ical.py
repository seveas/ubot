#!/usr/bin/python
# Slightly modified version of the iCal module found at
# http://www.random-ideas.net/Software/iCal_Module
# Original file doesn't come with a license but is public domain according to
# above website

import os
import os.path
import re
import datetime
import time
import pytz # pytz can be found on http://pytz.sourceforge.net

SECONDS_PER_DAY=24*60*60
def seconds(timediff):
    return SECONDS_PER_DAY * timediff.days + timediff.seconds

class ICalReader:

    def __init__(self, data):
        self.events = []
        self.raw_data = data
        self.readEvents()

    def readEvents(self):
        self.events = []
        lines = self.raw_data.split('\n')
        inEvent = False
        eventLines = []
        stRegex = re.compile("^BEGIN:VEVENT")
        enRegex = re.compile("^END:VEVENT")
        for line in lines:
            if stRegex.match(line):
                inEvent = True
                eventLines = []
            if inEvent:
                eventLines.append(line)
                if enRegex.match(line):
                    self.events.append(self.parseEvent(eventLines))

        return self.events

    def parseEvent(self, lines):
        event = ICalEvent()
        event.raw_data = "\n".join(lines)
        startDate = None
        rule = None
        endDate = None
        
        for line in lines:
            if re.compile("^SUMMARY:(.*)").match(line):
                event.summary = re.compile("^SUMMARY:(.*)").match(line).group(1)
            elif re.compile("^DTSTART;.*:(.*).*").match(line):
                startDate = self.parseDate(re.compile("^DTSTART;.*:(.*).*").match(line).group(1))
            elif re.compile("^DTEND;.*:(.*).*").match(line):
                endDate = self.parseDate(re.compile("^DTEND;.*:(.*).*").match(line).group(1))
            elif re.compile("^EXDATE.*:(.*)").match(line):
                event.addExceptionDate(parseDate(re.compile("^EXDATE.*:(.*)").match(line).group(1)))
            elif re.compile("^RRULE:(.*)").match(line):
                rule = re.compile("^RRULE:(.*)").match(line).group(1)

        event.startDate = startDate
        event.endDate = endDate
        if rule:
            event.addRecurrenceRule(rule)
        return event

    def parseDate(self, dateStr):
        year = int(dateStr[0:4])
        if year < 1970:
            year = 1970

        month = int(dateStr[4:4+2])
        day = int(dateStr[6:6+2])
        try:
            hour = int(dateStr[9:9+2])
            minute = int(dateStr[11:11+2])
        except:
            hour = 0
            minute = 0

        return datetime.datetime(year, month, day, hour, minute, tzinfo=pytz.UTC)

    def selectEvents(self, selectFunction):
        note = datetime.datetime.today()
        self.events.sort()
        events = filter(selectFunction, self.events)
        return events

    def todaysEvents(self, event):
        return event.startsToday()

    def tomorrowsEvents(self, event):
        return event.startsTomorrow()

    def eventsFor(self, date):
        note = datetime.datetime.today()
        self.events.sort()
        ret = []
        for event in self.events:
            if event.startsOn(date):
                ret.append(event)
        return ret


class ICalEvent:
    def __init__(self):
        self.exceptionDates = []
        self.dateSet = None

    def __str__(self):
        return self.summary

    def __eq__(self, otherEvent):
        return self.startDate == otherEvent.startDate

    def addExceptionDate(self, date):
        self.exceptionDates.append(date)

    def addRecurrenceRule(self, rule):
        self.dateSet = DateSet(self.startDate, self.endDate, rule)

    def startsToday(self):
        return self.startsOn(datetime.datetime.today())

    def startsTomorrow(self):
        tomorrow = datetime.datetime.fromtimestamp(time.time() + SECONDS_PER_DAY)
        return self.startsOn(tomorrow)

    def startsOn(self, date):
        return (self.startDate.year == date.year and
                self.startDate.month == date.month and
                self.startDate.day == date.day or
                (self.dateSet and self.dateSet.includes(date)))

    def startTime(self):
        return self.startDate

    def schedule(self, timezone=None):
        if not timezone:
            return "%s UTC: %s" % (self.startDate.strftime("%d %b %H:%M"), self.summary.replace('Meeting','').strip())
        return "%s: %s" % (self.startDate.astimezone(timezone).strftime("%d %b %H:%M"), self.summary.replace('Meeting','').strip())

    def is_on(self):
        return self.startDate < datetime.datetime.now(pytz.UTC) and self.endDate > datetime.datetime.now(pytz.UTC)

    def has_passed(self):
        return self.endDate < datetime.datetime.now(pytz.UTC)

    def seconds_to_go(self):
        return seconds(self.startDate - datetime.datetime.now(pytz.UTC))

    def seconds_ago(self):
        return seconds(datetime.datetime.now(pytz.UTC) - self.endDate)

    def time_to_go(self):
        if self.endDate < datetime.datetime.now(pytz.UTC):
            return False
        delta = self.startDate - datetime.datetime.now(pytz.UTC)
        s = ''
        if delta.days:
            if delta.days != 1:
                s = 's'
            return '%d day%s' % (delta.days, s)
        h = ''
        if delta.seconds > 7200:
            s = 's'
        if delta.seconds > 3600:
            h = '%d hour%s ' % (int(delta.seconds/3600),s)
        s = ''
        minutes = (delta.seconds % 3600) / 60
        if minutes != 1:
            s = 's'
        return '%s%d minute%s' % (h,minutes,s)

class DateSet:
    def __init__(self, startDate, endDate, rule):
        self.startDate = startDate
        self.endDate = endDate
        self.frequency = None
        self.count = None
        self.untilDate = None
        self.byMonth = None
        self.byDate = None
        self.parseRecurrenceRule(rule)
    
    def parseRecurrenceRule(self, rule):
        if re.compile("FREQ=(.*?);").match(rule) :
            self.frequency = re.compile("FREQ=(.*?);").match(rule).group(1)
        
        if re.compile("COUNT=(\d*)").match(rule) :
            self.count = int(re.compile("COUNT=(\d*)").match(rule).group(1))
        
        if re.compile("UNTIL=(.*?);").match(rule) :
            self.untilDate = DateParser.parse(re.compile("UNTIL=(.*?);").match(rule).group(1))
        
        if re.compile("INTERVAL=(\d*)").match(rule) :
            self.interval = int(re.compile("INTERVAL=(\d*)").match(rule).group(1))

        if re.compile("BYMONTH=(.*?);").match(rule) :
            self.byMonth = re.compile("BYMONTH=(.*?);").match(rule).group(1)

        if re.compile("BYDAY=(.*?);").match(rule) :
            self.byDay = re.compile("BYDAY=(.*?);").match(rule).group(1)

        
    def includes(self, date):
        if date == self.startDate:
            return True

        if self.untilDate and date > self.untilDate:
            return False

        if self.frequency == 'DAILY':
            increment = 1
            if self.interval:
                increment = self.interval
            d = self.startDate
            counter = 0
            while(d < date):
                if self.count:
                    counter += 1
                    if counter >= self.count:
                        return False

                d = d.replace(day=d.day+1)

                if (d.day == date.day and
                    d.year == date.year and
                    d.month == date.month):
                    return True
            
        elif self.frequency == 'WEEKLY':
            if self.startDate.weekday() == date.weekday():
                return True
            else:
                if self.endDate:
                    for n in range(0, self.endDate.day - self.startDate.day):
                        newDate = self.startDate.replace(day=self.startDate.day+n)
                        if newDate.weekday() == date.weekday():
                            return True

        elif self.frequency == 'MONTHLY':
            pass

        elif self.frequency == 'YEARLY':
            pass

        return False

