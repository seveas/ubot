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
        clearInterval(bot.interval_topic);
        clearInterval(bot.interval_mode);
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
    bot.interval_topic = null;
    bot.interval_mode = null;
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
                        bot.channel_scripts(name);
                        inserted = changed = true;
                    }
                });
                if(!inserted) {
                    $('#channels').append(bot.channel_widgets(name));
                    bot.channel_scripts(name);
                    changed = true;
                }
            });
            if(changed) {
                $('#channels').accordion("destroy").accordion({
                    collapsible: true, 
                    active: bot.active_channel,
                    change: function(event, ui) {
                        bot.activate_channel(ui.newHeader);
                    },
                });
                bot.activate_channel(bot.active_channel);
            }
        }
    });
};

Ubot.fn.activate_channel = function(header) {
    var bot = this;
    this.active_channel = header;
    clearInterval(bot.interval_topic);
    clearInterval(bot.interval_mode);
    bot.interval_topic = null;
    bot.interval_mode = null;
    if(header) {
        name = header.attr('id').substr(8);
        bot.get_topic(name);
        bot.get_mode(name);
        bot.interval_topic = setInterval(function() { bot.get_topic(name) }, 10000);
        bot.interval_mode = setInterval(function() { bot.get_mode(name) }, 10000);
    }
}

Ubot.fn.channel_widgets = function(name) {
    var bot = this;
    var S = function(html) { return $(html.replace(/%NAME%/g, name)); };
    var widgets = S('<h3 id="channel_%NAME%"><a href="#">%NAME%</a></h3><div></div>');
    var channel_div = widgets.last();
    var html = S('<p><b>Topic:</b> <span id="topic_%NAME%">&nbsp;</span></p>' +
        '<p><b>Mode:</b> <span id="mode_%NAME%">&nbsp;</span></p>' +
        '<table width="100%">' +
          '<tr>' +
            '<td width="75%"><input type="text" id="input_topic_%NAME%" class="input-hint" value="Topic" /></td>' +
            '<td width="5%">&nbsp;</td>' +
            '<td width="20%"><button id="button_topic_%NAME%"">Change</button></td>' +
          '</tr><tr>' +
              '<td width="75%"><input id="input_part_%NAME%" class="input-hint" type="text" value="Part message" /></td>' +
            '<td width="5%">&nbsp;</td>' +
            '<td width="20%"><button id="button_part_%NAME%"">Leave</button></td>' +
          '</tr>' +
        '</table>');
    channel_div.append(html);
    return widgets;
};

Ubot.fn.channel_scripts = function(name) {
    var bot = this;
    $('#input_topic_' + escape_selector(name)).bind({
        focus: function() {
            if($(this).hasClass('input-hint')) {
                $(this).removeClass('input-hint');
                this.value = $('#topic_' + escape_selector(name)).html();
            }
        },
        blur: function() {
            if(this.value == '' || this.value == $('#topic_' + escape_selector(name)).html()) {
                this.value = 'Topic'
                $(this).addClass('input-hint');
            }
        }
    });
    $('#button_topic_' + escape_selector(name)).click(function() {
        var topic = $("#input_topic_" + escape_selector(name)).attr('value');
        if(topic != "Topic") {
            bot.save_topic(name, topic);
        }
    });
    $('#button_topic_' + escape_selector(name)).button();

    $('#input_part_' + escape_selector(name)).bind({
        focus: function() {
            if($(this).hasClass('input-hint')) {
                $(this).removeClass('input-hint');
                this.value = '';
            }
        },
        blur: function() {
            if(this.value == '') {
                this.value = 'Part message';
                $(this).addClass('input-hint');
            }
        }
    });
    $('#button_part_' + escape_selector(name)).click(function() {
        var message = $("#input_part_" + escape_selector(name)).attr('value');
        if(message == '' || message == 'Part message') {
            message = 'So long and thanks for all the fish';
        }
        bot.part(name, message);
    });
    $('#button_part_' + escape_selector(name)).button();
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

Ubot.fn.get_mode = function(name) {
    $.ajax({
        type: 'GET',
        url: './rest/' + this.botname + '/channel/' + escape(name) + '/mode/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('Can\'t fetch channel mode: ' + result.error);
                return;
            }
            $("#mode_" + escape_selector(name)).html(result.mode.join(' '));
        }
    });
}

Ubot.fn.save_topic = function(name, topic) {
    var bot = this;
    $.ajax({
        type: 'POST',
        url: './rest/' + this.botname + '/channel/' + escape(name) + '/topic/',
        data: 'topic=' + escape(topic),
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('Can\'t save topic: ' + result.error);
                return;
            }
            var topic = $("#input_topic_" + escape_selector(name));
            topic.attr('value', 'Topic');
            topic.addClass('input-hint');
            setTimeout(function() { bot.get_topic(name) }, 500);
        }
    });
}

Ubot.fn.part = function(name, message) {
    var bot = this;
    $.ajax({
        type: 'POST',
        url: './rest/' + this.botname + '/channel/' + escape(name) + '/part/',
        data: 'message=' + escape(message),
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('Leaving channel ' + name + ' failed: ' + result.error);
                return;
            }
            setTimeout(function() { bot.get_channels() }, 500);
        }
    });
}

Ubot.fn.alert = function(message, timeout) {
    if(!timeout) { timeout = 5000; }
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
