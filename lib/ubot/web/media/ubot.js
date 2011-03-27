(function(window) {

var Ubot = function() {
}

Ubot.fn = Ubot.prototype;

Ubot.fn.initialize = function(botname) {
    this.botname = botname;
    var bot = this;
    bot.active_channel = false;
    /* Set up error handling */
    $('html').ajaxSend(function(event, xhr, options) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
    });
    $('html').ajaxError(function(event, xhr, option, error) {
        clearInterval(bot.interval_info);
        clearInterval(bot.interval_channels);
        var dialog = $('<div id="dialog-confirm" title="System error">' +
            '<p><span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 20px 0;"></span>' +
            xhr.responseText +
            '</p></div>');
        dialog.dialog({
            resizable: false,
            height: 170,
            width: 400,
            modal: true,
            buttons: {
                "Retry": function() {
                    document.location.href = './';
                },
            }
        });
    });
    $(document).ready(function() {
        /* Initialize gui */
        $('button, .button').button();
        $("#robot").bind({
            'mouseenter': function(){
                $("#robot").animate({'bottom': '5'}, 500);
            },
            'mouseleave': function(){
                $("#robot").animate({'bottom': '-70'}, 500);
            }
        });
        if (window.console && window.console.firebug) {
            bot.alert("Firebug is active, this can make ubotweb slow", 30000);
        }

        /* Join */
        $('#join_channel_input').bind({
            focus: function() {
                if($(this).hasClass('input-hint')) {
                    $(this).removeClass('input-hint');
                    this.value = '#';
                }
            },
            blur: function() {
                if(this.value == '' || this.value == '#') {
                    this.value = '#channel';
                    $(this).addClass('input-hint');
                }
            }
        });
        $('#join_channel_button').click(function(){
            var channel = $("#join_channel_input").attr('value');
            if(channel != '#channel') {
                bot.join(channel);
            }
        });

        /* Nick change */
        $('#nick_input').bind({
            focus: function() {
                if($(this).hasClass('input-hint')) {
                    $(this).removeClass('input-hint');
                    this.value = bot.nickname;
                    this.select();
                }
            },
            blur: function() {
                if(this.value == '' || this.value == bot.nickname) {
                    this.value = 'Nickname';
                    $(this).addClass('input-hint');
                }
            }
        });
        $('#nick_button').click(function(){
            var nick = $("#nick_input").attr('value');
            if(nick != 'Nickname' && nick != bot.nickname) {
                bot.nick(nick);
            }
        });

        /* Quit */
        $('#quit_input').bind({
            focus: function() {
                if($(this).hasClass('input-hint')) {
                    $(this).removeClass('input-hint');
                    this.value = '';
                }
            },
            blur: function() {
                if(this.value == '') {
                    this.value = 'Quit message';
                    $(this).addClass('input-hint');
                }
            }
        });
        $('#quit_button').click(function(){
            var message = $("#quit_input").attr('value');
            if(message == '' || message == 'Quit message') {
                message = 'So long and thanks for all the fish';
            }
            var dialog = $('<div id="dialog-confirm" title="Quit IRC?">' +
                '<p><span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 20px 0;"></span>' +
                'Are you sure you want to quit IRC and stop the bot?' +
                '</p></div>');
            dialog.dialog({
                resizable: false,
                height: 170,
                modal: true,
                buttons: {
                    "Quit": function() {
                        $(this).dialog("close");
                        $(this).dialog("destroy");
                        bot.quit(message);
                    },
                    "Cancel": function() {
                        $(this).dialog("close");
                        $(this).dialog("destroy");
                    }
                }
            });
        });

        /* Messages */
        $('#say_input').bind({
            focus: function() {
                if($(this).hasClass('input-hint')) {
                    $(this).removeClass('input-hint');
                    this.value = '';
                }
            },
            blur: function() {
                if(this.value == '') {
                    this.value = 'Message';
                    $(this).addClass('input-hint');
                }
            }
        });
        $('#to_input').bind({
            focus: function() {
                if($(this).hasClass('input-hint')) {
                    $(this).removeClass('input-hint');
                    this.value = '';
                }
            },
            blur: function() {
                if(this.value == '') {
                    this.value = 'Recipient';
                    $(this).addClass('input-hint');
                }
            }
        });
        $('#say_button').click(function() {
            if($('#to_input').hasClass('input-hint') || $('#say_input').hasClass('input-hint')) {
                return;
            }
            var recipient = $('#to_input').attr('value');
            var message = $('#say_input').attr('value');
            bot.say(recipient, message);
        });

        /* Request current state of the bot */
        bot.get_info();
        bot.get_channels();
    });
    bot.interval_info = setInterval(function() { bot.get_info() }, 10000);
    bot.interval_channels = setInterval(function() { bot.get_channels() }, 10000);
};

Ubot.fn.get_info = function() {
    var bot = this;
    $.ajax({
        type: 'GET',
        url: './rest/' + ubot.botname + '/info/',
        dataType: 'json',
        success: function(info) {
            if(info.status == 'error') {
                bot.alert('get_info failed: ' + info.error);
                return;
            }
            $('#version').html(info.version);
            bot.nickname = info.nickname;
            $('#nickname').html(info.nickname);
            if(info.connected) {
                $('#connection_info').html(info.server + ':' + info.port);
            }
            else {
                $('#connection_info').html('Not connected');
            }
        }
    });
};

Ubot.fn.get_channels = function() {
    var bot = this;
    $.ajax({
        type: 'GET',
        url: './rest/' + this.botname + '/channels/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('get_channels failed: ' + result.error);
                return;
            }
            var changed = false;
            $('#channels').children('h3').each(function(index, elt) {
                if($.inArray(elt.id.substr(8), result.channels) == -1) {
                    $(elt).next().remove()
                    $(elt).remove();
                    changed = true;
                }
            });
            $.each(result.channels, function(idx, name) {
                var inserted = false;
                $('#channels').children('h3').each(function(index, elt) {
                    if(inserted) {
                        return;
                    }
                    if(elt.id.substr(8) == name) {
                        inserted = true;
                    }
                    if(elt.id.substr(8) > name) {
                        $(elt).before(bot.channel_widgets(name));
                        inserted = changed = true;
                    }
                });
                if(!inserted) {
                    $('#channels').append(bot.channel_widgets(name));
                    changed = true;
                }
            });
            if(changed) {
                $('#channels').accordion("destroy").accordion({
                    collapsible: true, 
                    active: bot.active_channel,
                    change: function(event, ui) {
                        bot.active_channel = ui.newHeader;
                    },
                });
            }
        }
    });
};

Ubot.fn.channel_widgets = function(name) {
    var bot = this;
    var S = function(html) { return $(html.replace(/%NAME%/g, name)); };
    var widgets = S('<h3 id="channel_%NAME%"><a href="#">%NAME%</a></h3><div></div>');
    var channel_div = widgets.last();
    var topic = S('<p><b>Topic:</b> <span id="topic_%NAME%">&nbsp;</span> <span class="ui-icon ui-icon-pencil" style="float:right"></span></p>');
    channel_div.append(topic);
    bot.get_topic(name);
    return widgets;
};

Ubot.fn.join = function(name) {
    var bot = this;
    $.ajax({
        type: 'POST',
        data: 'channel=' + escape(name),
        url: './rest/' + this.botname + '/join/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('join failed: ' + result.error);
                return;
            }
            $("#join_channel_input").attr('value', '#channel');
            $("#join_channel_input").addClass('input-hint');
            setTimeout(function() { bot.get_channels() }, 500);
        }
    });
};

Ubot.fn.nick = function(nick) {
    var bot = this;
    $.ajax({
        type: 'POST',
        data: 'nick=' + escape(nick),
        url: './rest/' + this.botname + '/nick/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('nick change failed: ' + result.error);
                return;
            }
            $("#nick_input").attr('value', 'Nickname');
            $("#nick_input").addClass('input-hint');
            setTimeout(function() { bot.get_info() }, 500);
        }
    });
};

Ubot.fn.quit = function(message) {
    var bot = this;
    $.ajax({
        type: 'POST',
        data: 'message=' + escape(message),
        url: './rest/' + this.botname + '/quit/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('quit failed: ' + result.error);
                return;
            }
            clearInterval(bot.interval_info);
            clearInterval(bot.interval_channels);
        }
    });
};

Ubot.fn.say = function(recipient, message) {
    var bot = this;
    var is_action = /^\/me /i.test(message);
    if(is_action) {
        message = message.substr(4);
    }
    $.ajax({
        type: 'POST',
        url: './rest/' + this.botname + '/' + (is_action ? 'do' : 'say') + '/',
        data: 'target=' + escape(recipient) + '&message=' + escape(message),
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('message failed: ' + result.error);
                return;
            }
            $("#say_input").attr('value', 'Message sent!');
            $("#say_input").addClass('input-hint');
        }
    });
}

Ubot.fn.get_topic = function(name) {
    $.ajax({
        type: 'GET',
        url: './rest/' + this.botname + '/channel/' + escape(name) + '/topic/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('Can\'t fetch topic: ' + result.error);
                return;
            }
            $("#topic_" + escape_selector(name)).html(result.topic);
        }
    });
}

Ubot.fn.alert = function(message, timeout) {
    console.log(timeout);
    if(!timeout) { timeout = 5000; }
    console.log(timeout);
    message = message.replace('&','&amp;').replace('<','&lt;').replace('>', '&gt;');
    var msg = '<div class="ui-widget" "alarm">' + 
              '<div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">' +
              '<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>' +
               '<strong>Alert:</strong> ' + message + '</p></div></div>';
    $('body').prepend(msg);
    msg = $('body').children('div').first();
    setTimeout(function() { msg.remove(); }, timeout);
};

window.ubot = new Ubot();
})(window);

function escape_selector(text) {
    return text.replace(/([!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\/\\])/g,'\\$1')
}
