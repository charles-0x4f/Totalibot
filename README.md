Totalibot
=========

Totalibot - A python IRC bot and framework

This is chat bot for the IRC chat protocol.

If you want to make a plugin for the bot, just make a new file in the scripts directory and make a class:

class [classname]:
  def __init__(self, IRC):
    # this is how we'll access all of the IRC elements
    self.irc = IRC
    # this is declaring what types of messages we'd like to receive (see Message class in irc.py)
    self.types = [list of strings containing types of messages we want to repond to]
    
  def message_handler(message):
    # Do stuff here, this will be the main() of the plugin
    pass
