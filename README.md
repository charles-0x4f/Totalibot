Totalibot
=========

Totalibot - A python IRC bot and framework

This is chat bot for the IRC chat protocol.

If you want to make a plugin for the bot, just make a new file in the scripts directory and make a class:

'''
class [classname]:
  def __init__(self, IRC):
    # this is how we'll access all of the IRC elements
    self.irc = IRC
    # this is declaring what types of messages we'd like to receive (see Message class in structures.py)
    self.types = ["message", "kick", "command"]
	# if you want this plugin to be listed in the help command declare your
	# commands as strings in a list in public_commands like this:
	self.public_commands = ["command1", "command2"]
    
  def message_handler(message):
    # Do stuff here, this will be the main() of the plugin
	# Everytime a message with the type you declared in types comes
	# into the queue, this function will be called
    pass
'''
