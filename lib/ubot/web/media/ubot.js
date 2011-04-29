(function(window) {

var Ubot = function() {
}

Ubot.fn = Ubot.prototype;

Ubot.fn.initialize = function(botname) {
    this.botname = botname;
    var bot = this;
    bot.active_channel = false;
    bot.active_helper = false;
    /* Set up error handling */
    $('html').ajaxSend(function(event, xhr, options) {
        xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
    });
    $('html').ajaxError(function(event, xhr, option, error) {
        clearInterval(bot.interval_info);
        clearInterval(bot.interval_channels);
        clearInterval(bot.interval_helpers);
        clearInterval(bot.interval_topic);
        clearInterval(bot.interval_mode);
        clearInterval(bot.interval_helper);
        var dialog = $('<div id="dialog-confirm" title="System error">' +
            '<p><span class="ui-icon ui-icon-alert" style="float:left; margin:0 7px 20px 0;"></span>' +
            xhr.responseText +
            '</p></div>');
        dialog.dialog({
            resizable: false,
            height: 170,
            width: 400,
            modal: true,
            buttons: xhr.status == 503 ?
            {
                "Start bot": function() {
                    $.ajax({
                        type: 'GET',
                        url: './rest/' + ubot.botname + '/start/',
                        dataType: 'json',
                        success: function(data) {
                            document.location.href = './';
                        }
                    });
                },
                "Retry": function() {
                    document.location.href = './';
                },
            }
            :
            {
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
                $("#robot").animate(
                    {'bottom': '15'},
                    {
                        'duration': 500,
                        'complete': function() {
                            $("#robot").css('z-index', 4).animate({'bottom': '0'}, 200);
                        }
                    });
            },
            'mouseleave': function(){
                $("#robot").animate(
                    {'bottom': '-100'},
                    {
                        'duration': 600,
                        'complete': function() {
                            $("#robot").css('z-index', 6).animate({'bottom': '-70'}, 300);
                        }
                    });
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
        bot.get_helpers();
    });
    bot.interval_info = setInterval(function() { bot.get_info() }, 10000);
    bot.interval_channels = setInterval(function() { bot.get_channels() }, 10000);
    bot.interval_helpers = setInterval(function() { bot.get_helpers() }, 10000);
    bot.interval_topic = null;
    bot.interval_mode = null;
    bot.interval_helper = null;
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
    if(header && header.attr('id')) {
        name = header.attr('id').substr(8);
        bot.get_topic(name);
        bot.get_mode(name);
        bot.get_nicks(name);
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
        '<p><b>Users:</b> <span class="clickable" id="nicks_%NAME%"></span></p>' +
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
    $('#nicks_' + escape_selector(name)).click(function() {
        var nicks = $(this).data('nicks');
        var count = $(this).data('count');
        var dt = '<table>';
        var i = 0;
        cols = Math.min(10, Math.floor(count/10));
        $.each(nicks, function(nick, mode) {
            if(i%cols == 0) { dt += '<tr>'; }
            dt += '<td class="' + (/@/.test(mode) ? 'op ' : '') + (/\+/.test(mode) ? 'voice' : '') + '">' + nick + '</td>';
            if(i%cols == (cols-1)) { dt += '</tr>'; }
            i++;
        });
        dt += '</table>';
        $('<div></div>').html(dt).dialog({
            height: 'auto',
            maxHeight: 100,
            width: 'auto',
            title: 'People in ' + name,
            resizable: false,
            buttons: [{text: 'Close', click: function(){ $(this).dialog('destroy');}}]
        });
    });
    $('#input_topic_' + escape_selector(name)).bind({
        focus: function() {
            if($(this).hasClass('input-hint')) {
                $(this).removeClass('input-hint');
                this.value = unescape_html($('#topic_' + escape_selector(name)).html());
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
            clearInterval(bot.interval_helpers);
            clearInterval(bot.interval_topic);
            clearInterval(bot.interval_mode);
            clearInterval(bot.interval_helper);
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
            $("#topic_" + escape_selector(name)).html(escape_html(result.topic));
            $("#channels").accordion("resize");
        }
    });
}

Ubot.fn.helper_info = function(name) {
    $.ajax({
        type: 'GET',
        url: './rest/' + this.botname + '/helper/' + escape(name) + '/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('Can\'t fetch topic: ' + result.error);
                return;
            }
            $("#status_button_" + escape_selector(name)).find('.sliderswitch').animate({backgroundPosition: result.running ? 0 : -27});
            if(!result.running) {
                return;
            }
            $("#name_" + escape_selector(name)).html(escape_html(result.info.name) + ' v' + escape_html(result.info.version));
            $("#desc_" + escape_selector(name)).html(escape_html(result.info.description));
            $("#author_" + escape_selector(name)).html(escape_html(result.info.author_name));
            $("#helpers").accordion("resize");
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

Ubot.fn.get_nicks = function(name) {
    $.ajax({
        type: 'GET',
        url: './rest/' + this.botname + '/channel/' + escape(name) + '/nicks/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('Can\'t fetch nicks: ' + result.error);
                return;
            }
            var nc = 0;
            $("#nicks_" + escape_selector(name)).data('nicks', result.nicks);
            $("#nicks_" + escape_selector(name)).data('count', result.count);
            $.each(result.nicks, function(key, val) { nc++; });
            $("#nicks_" + escape_selector(name)).html(nc);
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

Ubot.fn.get_helpers = function() {
    var bot = this;
    $.ajax({
        type: 'GET',
        url: './rest/' + this.botname + '/helpers/',
        dataType: 'json',
        success: function(result) {
            if(result.status == 'error') {
                bot.alert('get_helpers failed: ' + result.error);
                return;
            }
            var changed = false;
            $('#helpers').children('h3').each(function(index, elt) {
                var seen = false;
                $.each(result.helpers, function(idx, name) {
                    if (seen) { return; }
                    if(name[0] == elt.id.substr(7)) {
                        seen = true;
                    }
                });
                if(!seen) {
                    $(elt).next().remove();
                    $(elt).remove();
                    changed = true;
                }
            });
            $.each(result.helpers, function(idx, name) {
                var inserted = false;
                var objname =name[1];
                name = name[0]
                $('#helpers').children('h3').each(function(index, elt) {
                    if(inserted) {
                        return;
                    }
                    if(elt.id.substr(7) == name) {
                        inserted = true;
                    }
                    if(elt.id.substr(7) > name) {
                        $(elt).before(bot.helper_widgets(name, objname));
                        bot.helper_scripts(name, objname);
                        inserted = changed = true;
                    }
                });
                if(!inserted) {
                    $('#helpers').append(bot.helper_widgets(name, objname));
                    bot.helper_scripts(name, objname);
                    changed = true;
                }
            });
            if(changed) {
                $('#helpers').accordion("destroy").accordion({
                    collapsible: true,
                    active: bot.active_helper,
                    change: function(event, ui) {
                        bot.activate_helper(ui.newHeader);
                    },
                });
                bot.activate_helper(bot.active_helper);
            }
        }
    });
};

Ubot.fn.activate_helper = function(header) {
    var bot = this;
    this.active_helper = header;
    clearInterval(bot.interval_helper);
    bot.interval_helper = null;
    bot.interval_
    if(header && header.attr('id')) {
        name = header.attr('id').substr(7);
        this.helper_info(name);
        bot.interval_helper = setInterval(function() { bot.helper_info(name) }, 10000);
    }
}

Ubot.fn.helper_widgets = function(name, objname) {
    var bot = this;
    var S = function(html) { return $(html.replace(/%NAME%/g, name)); };
    var widgets = S('<h3 id="helper_%NAME%"><a href="#">%NAME%</a></h3><div></div>');
    var helper_div = widgets.last();
    var html = S('<p><b>Helper:</b> <span id="name_%NAME%">&nbsp;</span></p>' +
                 '<p><b>Status:</b> <span id="status_button_%NAME%">&nbsp;</span></p>' +
                 '<p><b>Description:</b> <span id="desc_%NAME%">&nbsp;</span></p>' +
                 '<p><b>Author:</b> <span id="author_%NAME%">&nbsp;</span></p>'
                );
    helper_div.append(html);
    return widgets;
};

Ubot.fn.helper_scripts = function(name, objname) {
    var bot = this;
    $('#status_button_' + escape_selector(name)).sliderSwitch(bot, name, objname ? 'on' : 'off');
};

Ubot.fn.alert = function(message, timeout) {
    if(!timeout) { timeout = 5000; }
    var msg = '<div class="ui-widget" "alarm">' +
              '<div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">' +
              '<p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span>' +
               '<strong>Alert:</strong> ' + escape_html(message) + '</p></div></div>';
    $('body').prepend(msg);
    msg = $('body').children('div').first();
    setTimeout(function() { msg.remove(); }, timeout);
};

window.ubot = new Ubot();
})(window);

function escape_selector(text) {
    return text.replace(/([!"#$%&'()*+,.:;<=>?@\[\]^`{|}~\/\\])/g,'\\$1')
}
function escape_html(text) {
    return text.replace(/&/g,'&amp;').replace(/>/g, '&gt;').replace(/</g,'&lt;');
}
function unescape_html(text) {
    return text.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g, '&');
}

jQuery.fn.sliderSwitch = function(bot, name, start_state) {

    var state = start_state == 'on' ? start_state : 'off';

    return this.each(function() {
        var container;
        var image;

        container = jQuery('<span class="sliderswitch_container"></span>');
        image = jQuery('<img class="sliderswitch" src="" />');
        var src = image.css('background-image');
        src = src.replace(/url\("(.*)switch.png"\)/, '$1switch_container_'+state+'.png');
        image.attr('src',src);
        if(state == 'off') {
            image.css('background-position', '-27px')
        }
        jQuery(this).html(jQuery(container).html(jQuery(image)));

        jQuery(this).click(function() {
            var slider = jQuery(this).find('.sliderswitch');
            var state = (slider.css('background-position').substr(0,1) == '0') ? 'on' : 'off';
            if(state == 'on') {
                jQuery.ajax({
                    type: 'GET',
                    url: './rest/' + bot.botname + '/helper/' + name + '/stop/',
                    dataType: 'json',
                    success: function(result) {
                        if(result.status == 'error') {
                            bot.alert('Stopping ' + name + ' failed: ' + result.error);
                            return;
                        }
                        slider.animate(
                            {backgroundPosition: -27},
                            function() {
                                jQuery(this).attr('src', jQuery(this).attr('src').replace('on.png','off.png'));
                                setTimeout(function() { bot.get_helper(name) }, 500);
                            }
                        );
                    }
                });
            }
            else {
                jQuery.ajax({
                    type: 'GET',
                    url: './rest/' + bot.botname + '/helper/' + name + '/start/',
                    dataType: 'json',
                    success: function(result) {
                        if(result.status == 'error') {
                            bot.alert('Starting ' + name + ' failed: ' + result.error);
                            return;
                        }
                        slider.animate(
                            {backgroundPosition: 0},
                            function() {
                                jQuery(this).attr('src', jQuery(this).attr('src').replace('off.png','on.png'));
                                setTimeout(function() { bot.get_helper(name) }, 500);
                            }
                        );
                    }
                });
            }
        });
    });
};
