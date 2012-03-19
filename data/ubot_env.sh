if [ -z "$PYTHONPATH" ]; then
    PYTHONPATH="/home/dennis/ubot_inst/lib/python2.7/site-packages"
else
    PYTHONPATH="/home/dennis/ubot_inst/lib/python2.7/site-packages:$PYTHONPATH"
fi
if [ -z "$PERL5LIB" ]; then
    PERL5LIB="/home/dennis/ubot_inst/lib/perl5"
else
    PERL5LIB="/home/dennis/ubot_inst/lib/perl5:$PERL5LIB"
fi
if [ -z "$RUBYLIB" ]; then
    RUBYLIB="/home/dennis/ubot_inst/lib/site_ruby"
else
    RUBYLIB="/home/dennis/ubot_inst/lib/site_ruby:$RUBYLIB"
fi
if [ -z "$PATH" ]; then
    PATH="/home/dennis/ubot_inst/bin"
else
    PATH="/home/dennis/ubot_inst/bin:$PATH"
fi
export PYTHONPATH PERL5LIB RUBYLIB PATH
