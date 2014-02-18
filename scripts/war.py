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

# war.py
# will kick/ban all users in a channel except itself and the person issuing the
# command

# TODO: check if user getting ban is in the root list (don't ban rooted users)

import irc

class War:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["command"]
		self.commands = ["war"]

		self.commander = None
		self.kick_list = []

	def message_handler(self, message):
		if message.command == "war":
			if self.irc.util.is_root(message.sender_full) == True:
				print("Going to war: " + message.channel)
				self.commander = message.sender

				self.irc.util.say("THIS CHANNEL HAS BEEN FOUND GUILTY OF " +
					"TREASON, YOU SHALL ALL HANG", message.channel)

				# run through all users in this channel
				index = self.irc.channels.get_index(message.channel)
				for user_obj in self.irc.channels.channel_list[index].user_list:
					# make sure this isn't the best person ever
					if user_obj.user == self.commander or user_obj.user == \
						self.irc.nick:
						continue

					# add this nick to the kick list
					self.kick_list.append(user_obj.user)

					# do our banning
					self.irc.send_raw_command("MODE " + message.channel + " +b"
						+ " *" + user_obj.user + "*!*@*")

				# now we need to kick these rapscallions
				kick_string = "KICK " + message.channel + " "
				for nick in self.kick_list:
					self.irc.send_raw_command(kick_string + nick + " :WAR")

				# clear the kick list
				self.kick_list = []
			else:
				self.irc.util.say("You are not rooted", message.channel)
