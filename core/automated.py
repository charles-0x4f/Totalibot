'''
	Copyright 2014, Charles 0x4f
	https://github.com/charles-0x4f
	
    This file is part of Totalibot.

    Totalibot is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Totalibot is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty
    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Totalibot.

    If not, see <http://www.gnu.org/licenses/>.
'''

# automated.py
# Used for auto-joining, ctcp replies, etc.

import irc

class Automated:
	def __init__(self, IRC):
		self.irc = IRC
		self.joined = False
		self.types = ["response", "ctcp", "kick"]
	
	def message_handler(self, message):
	
		# auto-join channels + send connect command if they're set
		if message.code == "376" or self.irc.is_ready == True:
			if self.irc.util.autojoin == True and self.joined == False:
				self.irc.join_channels(self.irc.util._channels)
				self.joined = True
			
			if self.irc.util.send_connect_command == True:
				self.irc.send_raw_command(self.irc.util.connect_command)
				self.irc.util.send_connect_command = False
				
		# respond to CTCP VERSION
		if self.irc.util.version_set == True and message.type == "ctcp":
			print(message.message)
			if "version" in message.message[0].lower():
				self.irc.util.say_action("VERSION " +
					self.irc.util.version, message.sender)

		# auto re-join on kick
		if message.type == "kick":
			# if the one getting kicked is us
			if message.code == self.irc.nick:
				print("KICK: REJOINING")
				self.irc.send_raw_command("JOIN " + message.channel)