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

# chatlog.py
# Record all chat, assign messages to users

import irc

class ChatLog:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["message"]

		self.db = self.irc.sql.db

		# Define the table
		# user_id channel_id timestamp message
		self.db.execute("CREATE TABLE IF NOT EXISTS ChatLog("
			+ "user_id INTEGER, channel_id INTEGER,"
			+ "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,"
			+ "message TEXT);")

	def message_handler(self, message):
		fields = self.irc.util.get_sender_fields(message.sender_full)
		user = fields[1]

		usr_id = self.irc.sql.get_user_id(user)
		chan_id = self.irc.sql.get_channel_id(message.channel)

		if usr_id == -1 or chan_id == -1:
			print("ERROR: CHATLOG: USER OR CHAN ID DOESN'T EXIST")
			return

		# convert message list into a string
		message = " ".join(message.message)
		# remove leading ':'
		message = message[1:]

		self.db.execute("INSERT INTO ChatLog Values(?, ?, CURRENT_TIMESTAMP,"
			+ " ?)", (usr_id, chan_id, message,))
