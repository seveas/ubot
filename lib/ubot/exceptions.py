import dbus

class ConfigError(Exception): pass

class UbotException(dbus.DBusException):
    _dbus_error_name = 'net.seveas.ubot.UbotException'

class InvalidTargetException(dbus.DBusException):
    _dbus_error_name = 'net.seveas.ubot.InvalidTargetException'
