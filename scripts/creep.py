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

# creep.py
# State user information publicly

import irc

class Creep:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["command"]
		self.public_commands = ["creep"]

	def message_handler(self, message):
		if message.command != "creep":
			return

		# is there a nick supplied?
		if len(message.message) == 0:
			self.irc.util.say("You didn't give me a name..", message.channel)
			return
		else:
			nick = message.message[0]

		if nick.isdigit() == False:
			usr_id = self.irc.sql.get_user_id_from_nick_if_its_at_all_possible(nick)

			if usr_id == -1:
				self.irc.util.say("I don't know them.", message.channel)
				return
		else:
			usr_id = int(nick)

		usr = self.irc.sql.get_user_from_id(usr_id)

		string = ""
		string += "User: " + usr + " ID: " + str(usr_id) + "; Last seen: "

		last = self.irc.sql.get_last_seen(usr)

		# if it failed
		if nick == self.irc.nick:
			# easter egg!
			string += self.irc.nick + " IS FOREVER; "
		elif last == -1:
			string += "?; "
		else:
			string += last + "; "

		nicks = []
		hosts = []

		nicks = self.irc.sql.get_known_nicks(usr_id)
		hosts = self.irc.sql.get_known_hostnames(usr_id)

		string += "Known nicknames: "

		for nick in nicks:
			string += nick + ", "

		# remove the last ", "
		string = string[:-2]

		string += "; Known hostnames: "

		for host in hosts:
			string += host + ", "

		string = string[:-2]

		self.irc.util.say(string, message.channel)