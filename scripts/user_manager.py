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

# user_manager.py
# handles all join/part/quit/etc. messages and user/chan lists

import irc
import util
#import users_db

class UserManager:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["response", "join", "part", "message", "command", \
			"nick", "mode", "kick"]

		# used for the index of channels
		self.index = None

	def message_handler(self, message):

		if message.type == "response":
			channel = message.message[0]

			# handle the user lists on joining channels
			# 332 is the code for a channel's topic
			if message.code == "332":
				topic = " "
				topic.join(message.message[1:])
				print("TOPIC: " + topic)
				print("USERMANAGER TOPIC: " + topic)

				self.irc.sql.set_topic(message.channel, topic)

			# 353 is a message that lists all users of a channel
			elif message.code == "353":
				# 353 has a different structure than the typical
				# response message
				channel = message.message[1]
				chan_id = self.irc.sql.get_channel_id(channel)
				print("DB: 353 CHAN ID: %s" % chan_id)
				#self.index = self.irc.channels.get_index(channel)

				#if self.index != -1:
				userlist = message.message[2:]
				# remove : from first element
				userlist[0] = userlist[0][1:]
				
				#self.irc.channels.add_user(channel, userlist)
				for user in userlist:
					# create nick entry (id, nick, host, rate)
					self.irc.sql.add_nick(None, user, None, None)
					# join this nick to this channel
					self.irc.sql.join_channel(chan_id, None, user)

			# 366 is the /end of names for said channel response
			elif message.code == "366":
				# can probably remove this at this point
				#userlist = ""
			
				#for user_obj in self.irc.channels.channel_list[self.index].user_list:
					#userlist += user_obj.status + user_obj.user + ","
				pass

		elif message.type == "join":
			# if it's us joining a channel
			if message.sender == self.irc.nick:
				print("DB: JOIN TEST: " + message.channel)
				# Try to add this channel to the channel_list table
				if self.irc.sql.add_channel(message.channel) == False:
					print("DB: ERROR! COULD NOT ADD CHANNEL")
					return

			# if this channel is already known, try to add this user
			# to the channel_contents table for this channel. Since join_user
			# expects a list of strings, sending just one string will cause
			# Python to force coercion and mutilate the string. Thus sender
			# needs to be in a list, otherwise it'd be more work.
			print("DB: SENDER_FULL: " + message.sender_full)
			# fields = tuple(nick, user, host)
			fields = self.irc.util.get_sender_fields(message.sender_full)
			nick = fields[0]
			user_field = fields[1]
			hostname = fields[2]
			print("DB: USER_FIELD: " + user_field)

			# Try to add a user entry for this user
			self.irc.sql.add_user(user_field)
			id = self.irc.sql.get_user_id(user_field)
			# Add a full nick entry assigned to this user
			self.irc.sql.add_nick(id, nick, hostname, 0.0)
			chan = self.irc.sql.get_channel_id(message.channel)
			# Add this nick to the contents of this channel
			self.irc.sql.join_channel(chan, id, nick)

			print("DB: PRINT Channel_Contents:")
			#self.irc.sql.print_rows("Channel_Contents")

		elif message.type == "message" or message.type == "command":
			self.irc.sql.update_user_info(message.sender_full)

		elif message.type == "nick":
			fields = self.irc.util.get_sender_fields(message.sender_full)

			# fields[0] is the old nickname, message.sender is the new one
			self.irc.sql.change_nick(fields[0], message.sender)

			# Change sender_full, this will be used to register the nick
			# to its proper user
			message.sender_full = message.sender + "!" + fields[1] + "@" + \
				fields[2]

			print("DB: CHANGE NICK TEST:")
			print(fields)

			self.irc.sql.add_nick(None, message.sender, None, None)
			self.irc.sql.update_user_info(message.sender_full)

		elif message.type == "mode":
			self.irc.sql.change_user_status(message.code, message.channel,
				message.message)

		elif message.type == "kick":
			print("KICKING: " + message.code)
			# same as part
			self.irc.sql.update_user_info(message.sender_full)
			self.irc.sql.part(message.channel, message.code)

		elif message.type == "part":
			if message.code == "PART":
				self.irc.sql.update_user_info(message.sender_full)
				self.irc.sql.part(message.channel, message.sender)

			elif message.code == "QUIT":
				self.irc.sql.update_user_info(message.sender_full)
				self.irc.sql.quit(message.sender)