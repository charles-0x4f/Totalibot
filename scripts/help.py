# help.py
# publicly list available commands

import irc

class Help:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["command"]
		self.public_commands = ["help"]
		self.plugins = []

		# string to output our plugin list
		self.plugin_list = ""

	def message_handler(self, message):
		if message.command == "help":
			# Get the IRC object's initiated plugins list
			self.plugins = self.irc.initiated_plugins

			if len(self.plugins) != 0:
				# iterate through all of our plugins and see if they have
				# public_commands defined
				for plug in self.plugins:
					try:
						for command in plug.public_commands:
							self.plugin_list += command
							self.plugin_list += ", "
					except:
						continue

				# remove the trailing ", "
				self.plugin_list = self.plugin_list[:-2]
				self.irc.util.say("Commands: " + self.plugin_list, message.channel)