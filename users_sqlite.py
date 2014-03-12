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

# users_sqlite.py
# Direct access to user SQLite database

import os
import sys
import sqlite3

import irc

class Database:
	def __init__(self, IRC, db_name):
		self.irc = IRC
		self.database = db_name + ".db"
		self.db_connection = None
		self.db = None
		self.is_empty = False

		self.specials = ["@", "+", "%"]
		self.specials_plain = ["o", "v", "h"]

		# check to see if the db directory exists
		if not os.path.exists("db"):
			print("DB: DIR DOES NOT EXIST; CREATING")
			self.is_empty = True

			try:
				# try to make the directory
				os.makedirs("db")
			except:
				print("DB: FAILED TO CREATE DIRECTORY")

		# see if our actual database file for this IRC server exists
		if not os.path.exists("db" + os.sep + self.database):
			print("DB: DATABASE DOES NOT EXIST; CREATING")
			self.db_connection = sqlite3.connect("db" + os.sep + self.database)
			self.db = self.db_connection.cursor()

			# set SQLite to auto-commit
			self.db_connection.isolation_level = None

			# create our tables
			self.db.execute("CREATE TABLE Users(user_id INTEGER PRIMARY KEY "
				" AUTOINCREMENT, user_string TEXT, last_seen TIMESTAMP DEFAULT "
				+ "CURRENT_TIMESTAMP NOT NULL);")
			# List of known channels that we'll keep
			self.db.execute("CREATE TABLE Channel_List(channel_id INTEGER PRIMARY KEY"
				+ " AUTOINCREMENT, channel_name TEXT, topic TEXT, modes TEXT);")
			# List of all users in said channels, gets wiped on restart
			self.db.execute("CREATE TABLE Channel_Contents(channel_id INTEGER,"
				+ " user_id INT, nick TEXT, status TEXT);")
			# Used to associate nicknames to users
			self.db.execute("CREATE TABLE Nicks(user_id INTEGER, nick TEXT,"
				+ " hostname TEXT, use_rate REAL);")
			#self.db.commit()
		else:
			# If this file does exist, try to use it
			self.db_connection = sqlite3.connect("db" + os.sep + self.database)
			self.db = self.db_connection.cursor()

			# remove all entries in Channel_Contents, our channels should
			# be empty
			self.db.execute("DELETE FROM Channel_Contents;")
			self.db_connection.commit()

			# set SQLite to auto-commit
			self.db_connection.isolation_level = None

	def get_tables(self):
		table_list = []

		for row in self.db.execute("SELECT * FROM sqlite_master WHERE type='table';"):
				print("DB GET TABLES RAW: " + row[1])

				table_list.append(row[1])

		return table_list

	def add_user(self, user_string):
		self.db.execute("SELECT * FROM Users WHERE user_string = ?;", (user_string,))

		if len(self.db.fetchall()) > 0:
			return False
		else:
			self.db.execute("INSERT INTO Users(user_string) VALUES(?);", (user_string,))
			return True

	def get_user_id(self, user_string):
		self.db.execute("SELECT user_id FROM Users WHERE user_string = ?;", (user_string,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			print("DB: ERROR! COULD NOT FIND USER ID")
			return -1
		elif len(rows) > 1:
			print("DB: ERROR! MORE THAN 1 USER WITH THIS USER_STRING")
			return -1
		else:
			# row[0] is a tuple, so we need to get just the data
			return rows[0][0]

	def get_user_id_from_nick_if_its_at_all_possible(self, nick):
		self.db.execute("SELECT user_id FROM Nicks WHERE nick = ?"
			+ " AND user_id NOT NULL;", (nick,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			return -1
		else:
			print("DB: GET ID FROM NICK:")
			print(rows[0][0])
			return rows[0][0]

	def get_user_from_id(self, id):
		self.db.execute("SELECT user_string FROM Users WHERE user_id = ?;",
			(id,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			return -1

		print("DB: GET USER FROM ID: " + rows[0][0])
		return rows[0][0]

	def get_channel_id(self, channel):
		self.db.execute("SELECT channel_id FROM Channel_List WHERE channel_name = ?;",
			(channel,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			print("DB: ERROR! COULD NOT FIND CHANNEL ID: " + channel)
			return -1
		elif len(rows) > 1:
			print("DB: ERROR! MORE THAN 1 CHANNEL WITH THIS NAME")
			return -1
		else:
			# row[0] is a tuple, so we need to get just the data
			return rows[0][0]

	def get_last_seen(self, usr):
		self.db.execute("SELECT last_seen FROM Users WHERE user_string = ?;",
			(usr,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			print("DB: ERROR LAST_SEEN: NO ROWS: " + usr)
			return -1
		else:
			return rows[0][0]

	def get_known_nicks(self, usr_id):
		self.db.execute("SELECT DISTINCT nick FROM Nicks WHERE user_id = ?;",
			(usr_id,))

		rows = self.db.fetchall()
		# TODO: Add length checking and error handling to this and known_hosts
		nick_list = []

		print("DB: GET KNOWN NICKS:")
		print(rows)

		for nick in rows:
			nick_list.append(nick[0])

		print(nick_list)
		return nick_list

	def get_known_hostnames(self, usr_id):
		self.db.execute("SELECT DISTINCT hostname FROM Nicks WHERE user_id = ?;",
			(usr_id,))

		rows = self.db.fetchall()
		host_list = []
		length = len(rows)

		print("DB: GET KNOWN HOSTS:")
		print(rows)

		for host in rows:
			host_list.append(host[0])

		print(host_list)
		return host_list

	def get_all_nicks_from_channel_id(self, chan_id):
		nick_list = []

		self.db.execute("SELECT nick FROM Channel_Contents WHERE"
			+ " channel_id = ?;", (chan_id,))

		rows = self.db.fetchall()
		print("DB: GET ALL NICKS:")
		print(rows)
		print(rows[0])

		for nick in rows:
			print(nick[0])
			# fetchall returns a list of tuples
			nick_list.append(nick[0])

		return nick_list

	def add_nick(self, user_id, nick, user_hostname, rate):
		# TODO: do duplicate checking

		id = None
		host = None

		if user_id != None:
			id = user_id
		if user_hostname != None:
			host = user_hostname

		# Strip any statuses from the nick if they exist
		if nick[0] in self.specials:
			nick = nick[1:]

		# this should reject most duplicates we don't want:
		# if we've already stored this nickname
		if self.is_duplicate_nick(nick):
			# if our adding hostname is blank
			if host == None:
				#print("DB: ADD NICK: DUPLICATE NICK WITH NO HOST:" + nick)
				# then don't bother trying to add this useless junk
				return
			# if we have the same nick and we have a hostname
			else:
				# if the hostname is also a duplicate for this name
				if self.is_duplicate_hostname(nick, host):
					#print("DB: ADD NICK: DUPLICATE HOST")
					return

		self.db.execute("INSERT INTO Nicks VALUES(?, ?, ?, ?);",
			(id, nick, host, rate,))

	def add_channel(self, channel):
		print("DB: ADD CHANNEL: " + channel)

		# See if this channel exists
		self.db.execute("SELECT * FROM Channel_List WHERE channel_name = ?;", (channel,))

		# if this channel is already known, return false
		if len(self.db.fetchall()) > 0:
			return False
		else:
			# Create new channel entry with unique ID and set the name
			# last two NULLs are for topic and modes, which will be set later
			self.db.execute("INSERT INTO Channel_List VALUES (NULL, ?, NULL,"
				+ " NULL);", (channel,))

			return True

	def join_channel(self, channel_id, user_id, nick):
		status = None

		# if we don't have a proper channel, just leave
		if channel_id == None:
			print("DB: ERROR! CHANNEL_ID NULL ON JOIN")
			return False

		# handle the status, this'll be the first character
		if nick[0] in self.specials:
			status = nick[0]
			nick = nick[1:]

		self.db.execute("INSERT INTO Channel_Contents VALUES(?, ?, ?, ?);",
			(channel_id, user_id, nick, status,))

	def set_topic(self, channel, topic):
		# TODO: check if channel exists

		print("DB: SET TOPIC: " + topic)

		self.db.execute("UPDATE Channel_List SET topic = ? WHERE "
			+ "channel_name = ?;", (topic, channel,))

	def set_channel_mode(self, channel, mode):
		# TODO: check if channel exists

		self.db.execute("UPDATE Channel_List SET mode = '?' WHERE "
			+ "channel_name = '?';", (mode, channel,))

	# Function to determine if a nick is already enter in the Nicks table
	def is_duplicate_nick(self, nick):
		self.db.execute("SELECT * FROM Nicks WHERE nick = ?;", (nick,))

		results = len(self.db.fetchall())

		if results == 0:
			return False
		else:
			return True

	# check to see if a nick has a known hostname
	def is_duplicate_hostname(self, nick, hostname):
		self.db.execute("SELECT * FROM Nicks WHERE hostname = ? AND nick"
			+ " = ?;", (hostname, nick,))

		results = len(self.db.fetchall())

		if results == 0:
			return False
		else:
			return True

	# see if this user is in the Users table(registered)
	def is_user_registered(self, user):
		index = self.get_user_id(user)

		if index > 0:
			return True
		else:
			return False

	def is_nick_registered_full(self, nick, host):
		self.db.execute("SELECT user_id FROM Nicks WHERE nick = ?"
			+ " AND hostname = ? AND user_id NOT NULL;",(nick, host,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			return False
		else:
			return True

	def register_nick(self, user_field, nick_field, host_field):
		usr_id = self.get_user_id(user_field)

		if usr_id == -1:
			print("DB: REGISTER NICK ERROR ID")
			return

		# if this nick is already registerd, then return
		if self.is_nick_registered_full(nick_field, host_field):
			return

		print("DB: REGISTER NICK: REGISTERING " + nick_field + " TO "
			+ user_field)

		# update Nicks table
		self.db.execute("UPDATE Nicks SET user_id = ?, hostname = ? WHERE"
			+ " nick = ?;", (usr_id, host_field, nick_field,))

		# update Channel_Contents table
		self.db.execute("UPDATE Channel_Contents SET user_id = ? WHERE"
			+ " nick = ?;", (usr_id, nick_field,))

	#def is_duplicate_nick_entry(self, chan_id, usr_id, nick):
		#SELECT channel_id, user_id, nick, COUNT(*) FROM Channel_Contents GROUP BY channel_id, user_id, nick HAVING COUNT(*) > 1

	def part(self, channel, nick):
		# This is so channel can either be an ID or the actual channel name
		if type(channel) is int:
			chan_id = channel
		else:
			chan_id = self.get_channel_id(channel)

		if chan_id < 1:
			print("DB: CAN'T PART, CHANNEL ID ERROR")
			return

		# Remove this nick entry for this channel
		self.db.execute("DELETE FROM Channel_Contents WHERE channel_id = ?"
			+ " AND nick = ?;", (chan_id, nick,))

		# if this is us, we need to wipe this channel's contents
		if nick == self.irc.nick:
			print("DB: WARNING: DELETE CONTENTS OF CHAN " + str(chan_id))
			self.db.execute("DELETE FROM Channel_Contents WHERE "
				+ "channel_id = ?;", (chan_id,))

	def quit(self, nick):
		self.db.execute("SELECT channel_id FROM Channel_Contents WHERE nick"
			+ " = ?;", (nick,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			print("DB: QUIT ERROR")
			return

		usr_id = self.get_user_id_from_nick_if_its_at_all_possible(nick)

		if usr_id == -1:
			print("DB: QUIT: NO USER ID")
			return

		# update timestamp
		self.touch_timestamp(usr_id)

		print("DB: QUIT: " + nick)
		for entry in rows:
			print("DB: QUIT: ENTRY:")
			print(entry[0])
			self.part(entry[0], nick)

	def update_user_info(self, user_full):
		# fields = (nick, user, host)
		fields = self.irc.util.get_sender_fields(user_full)

		# if this username is not in Users, add it
		if self.is_user_registered(fields[1]) == False:
			self.add_user(fields[1])
		else:
			# update this user's last_seen timestamp
			usr_id = self.get_user_id(fields[1])
			self.touch_timestamp(usr_id)

		# if this nick is not registered to this user, do it
		# (and update Channel_Contents)
		if self.is_nick_registered_full(fields[0], fields[2]) == False:
			self.register_nick(fields[1], fields[0], fields[2])

	def change_nick(self, current_nick, new_nick):
		# update channel_contents with the new nick
		# Note: update_user_info should be ran after this function
		# to register new nicknames and update timestamps
		self.db.execute("UPDATE Channel_Contents SET nick = ? WHERE nick"
			+ " = ?;", (current_nick, new_nick,))

	def change_user_status(self, code, channel, nick):
		chan_id = self.get_channel_id(channel)

		# if this channel doesn't exist, don't bother with this nonsense
		if chan_id == -1:
			print("DB: CHANGE STATUS CHAN FAIL")
			return

		# operation = '+' for adding status or '-' for removing
		operation = code[0]

		# if this person is getting opped, mode will be 'o'
		mode = code[1]

		# used to look up the fancy status in specials list
		if mode in self.specials_plain:
			mode_index = self.specials_plain.index(mode)
		else:
			# if this is something it shouldn't be, stop
			# this shouldn't get called
			return

		# o mode will be @ in this varible
		mode_special_char = self.specials[mode_index]

		self.db.execute("SELECT status FROM Channel_Contents"
			+ " WHERE channel_id = ? AND nick = ?;", (chan_id, nick,))

		current_status = self.db.fetchall()
		print(current_status)
		# fetchall returns a tuple of a list, we just want the raw string
		current_status = current_status[0][0]

		print("DB: CHANGE STATUS BEFORE:")
		print(current_status)

		if current_status == None:
			if operation == "+":
				current_status = mode_special_char
		elif operation == "+":
			# if this status is already applied, we're good
			if mode_special_char in current_status:
				return True
			else:
				current_status += mode_special_char
		elif operation == "-":
			if mode_special_char not in current_status:
				return True
			else:
				# replace this special character with nothing
				current_status = current_status.replace(mode_special_char, "")

				# should help the SQLite DB out by using None on blank string
				if len(current_status) == 0:
					current_status = None
		else:
			return False

		print("DB: CHANGE STATUS AFTER:")
		print(current_status)

		self.db.execute("UPDATE Channel_Contents SET status = ? WHERE"
			+ " channel_id = ? AND nick = ?;", (current_status, chan_id, nick,))

		return True

	# Update the timestamp for this 'registered' user
	def touch_timestamp(self, usr_id):
		#TODO make sure this user_id exists

		self.db.execute("UPDATE Users SET last_seen = CURRENT_TIMESTAMP WHERE"
			+ " user_id = ?;", (usr_id,))

	def get_all_nicks_by_user(self, user):
		usr_id = self.get_user_id(user)
		self.db.execute("SELECT nicks FROM Nicks WHERE user_id = ?;", (usr_id,))

	def print_rows(self, table):
		# SQLite does not allow for parameterized table/column names
		for row in self.db.execute("SELECT * FROM {0};".format(table)):
			#print("DB PRINT ROW:")
			print(row)