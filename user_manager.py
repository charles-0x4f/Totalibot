'''
	Copyright 2014, Charles 0x4f
	https://github.com/charles-0x4f
	
    This file is part of IRC bot, Schmibersee bot.

    IRC bot, Schmibersee bot is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    IRC bot, Schmibersee bot is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty
    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with IRC bot, Schmibersee bot.

    If not, see <http://www.gnu.org/licenses/>.
'''

# user_manager.py
# handles all join/part/quit/etc. messages and user/chan lists

import irc
import util
import users_db

class UserManager:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["response", "join", "part", "mode"]

		# used for the index of channels
		self.index = None

	def message_handler(self, message):

		if message.type == "response":
			channel = message.message[0]
			self.index = self.irc.channels.get_index(channel)

			# handle the user lists on joining channels
			# 332 is the code for a channel's topic
			if message.code == "332":
				if self.index != -1:
					# join topic message into a string
					topic = " "
					topic.join(message.message[1:])
					# remove leading :
					topic = topic[1:]
					print("USERMANAGER TOPIC: " + topic)

					self.irc.channels.channel_list[self.index].topic = topic
			# 353 is a message that lists all users of a channel
			elif message.code == "353":
				# 353 has a different structure than the typical
				# response message
				channel = message.message[1]
				self.index = self.irc.channels.get_index(channel)

				if self.index != -1:
					userlist = message.message[2:]
					# remove : from first element
					userlist[0] = userlist[0][1:]
					self.irc.channels.add_user(channel, userlist)
			# 366 is the /end of names for said channel response
			elif message.code == "366":
				# can probably remove this at this point
				userlist = ""
			
				for user_obj in self.irc.channels.channel_list[self.index].user_list:
					userlist += user_obj.status + user_obj.user + ","

		elif message.type == "join":
			# if this channel doesn't exist on our list, add it
			self.index = self.irc.channels.get_index(message.channel)
			if self.index == -1:
				temp = users_db.ChannelList.Channel()
				temp.name = message.channel
				self.irc.channels.add_channel(temp)
				print("Joined channel: " + message.channel)
				return

			# if this user is not already in this channel, try to add them
			# add users function expects a list of strings, python will force
			# coersion if we just pass the sender string and will mutilate it
			joiner = [message.sender]
			self.irc.channels.add_user(message.channel, joiner)

		elif message.type == "part":
			if message.code == "PART":
				self.irc.channels.part(message.channel, message.sender)
			elif message.code == "QUIT":
				self.irc.channels.quit(message.sender)