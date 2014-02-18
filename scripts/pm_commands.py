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

# pm_commands.py
# Handles commands sent through private messages

import irc

class PM_Commands:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["pm"]
		
		self.commands = ["login", "say", "action", "raw", "printusers", "quit"]
		self.error = "Not enough paramaters"
		
	def message_handler(self, message):
		length = len(message.message)
		root = self.irc.util.is_root(message.sender_full)
		
		if length < 2:
			if root == True:
				self.irc.util.say("PMCOMMAND: " + self.error,
					message.sender)
			return
	
		# get command by removing the leading ':' character
		command = message.message[0][1:].lower()
		
		if command in self.commands:

			''' PUBLIC COMMANDS '''

			# try to log in
			if command == "login":
				result = self.irc.util.login(message.sender_full,
					message.message[1])
				
				if result == False:
					self.irc.util.say("LOGIN: " + self.error, message.sender)
				else:
					self.irc.util.say("You are now root. Be evil.",
						message.sender)
			
				return
			
			if root == False:
				self.irc.util.say("LOGIN: You are not root", message.sender)
				return

			''' ROOTED COMMANDS '''

			# merge message list into a string
			string = " ".join(message.message[2:])

			# send raw commands to the bot
			if command == "raw":
				self.irc.send_raw_command(" ".join(message.message[1:]))
			
			# make the bot say stuff like a normal person
			if command == "say":
				self.irc.util.say(string, message.message[1])

			# make the bot do a /me action
			if command == "action":
				self.irc.util.say_action("ACTION " + string,
					message.message[1])

			# send the user the userlist of a channel
			if command == "printusers":
				channel = message.message[1]

				index = self.irc.channels.get_index(channel)
				print("PRINTUSERS INDEX: " + str(index))
				print("PRINTUSERS CHANNAME: " + self.irc.channels.channel_list[index].name)
				print("PRINTUSERS NUMUSERS: " + str(len(self.irc.channels.channel_list[index].user_list)))

				if index == -1:
					return

				userlist = ""
				segments = []

				for user_obj in self.irc.channels.channel_list[index].user_list:
					userlist += user_obj.status + user_obj.user + ","

				# if this list is too long for a single irc message
				# TODO: modify the say functions to limit character length
				for count in range(0, len(userlist), 475):
					segments.append(userlist[count:count + 475])

				for line in segments:
					self.irc.util.say(line, message.sender)

			if command == "quit":
				self.irc.quit("bye bye :(")