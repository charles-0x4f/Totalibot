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

# quote.py
# implementation of a quote system

import irc

class Quote:
	def __init__(self, IRC):
		self.irc = IRC
		self.types = ["command"]
		self.public_commands = ["quote", "addquote", "delquote", "vote"]

		# variables
		self.fields = None
		self.usr_id = None
		self.length = None

		# that's way too much to type every time
		self.db = self.irc.sql.db

		# Quote_Credentials
		# user_id quote_id vote
		self.db.execute("CREATE TABLE IF NOT EXISTS Quote_Credentials("
			+ "user_id INTEGER, quote_id INTEGER, vote INTEGER);")

		# Quote_Entry
		# quote_id user_id quote
		self.db.execute("CREATE TABLE IF NOT EXISTS Quote_Entry"
			+ "(quote_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER,"
				+ " quote TEXT);")

	def message_handler(self, message):
		self.fields = self.irc.util.get_sender_fields(message.sender_full)
		print("DEBUG: QUOTE: FIELDS:")
		print(repr(self.fields))
		self.usr_id = self.irc.sql.get_user_id(self.fields[1])
		self.length = len(message.message)

		if message.command == "addquote":
			self.add_quote(message)
			return

		if message.command == "quote":
			self.quote(message)
			return

		if message.command == "delquote":
			self.delquote(message)
			return

		if message.command == "vote":
			self.vote(message)
			return

	def get_vote_stats(self, quote_id):
		upvotes = 0
		downvotes = 0
		total = 0

		self.db.execute("SELECT vote FROM Quote_Credentials WHERE"
			+ " quote_id = ?;", (quote_id,))

		print("QUOTE: VOTE:")
		for row in self.db.fetchall():
			vote = row[0]

			# if this is an upvote
			if vote == 1:
				upvotes += 1
			elif vote == -1:
				downvotes += 1

			total += vote

		return (upvotes, downvotes, total)

	def add_quote(self, message):
		if self.usr_id == -1:
			print("QUOTE: USER ID NOT FOUND")
			self.irc.util.say("User unknown; try again", message.channel)
			return

		if self.length == 0:
			self.irc.util.say("Need something to quote, dummy",
				message.channel)
			return

		quote = " ".join(message.message)
		print("QUOTE: " + quote)
		self.db.execute("INSERT INTO Quote_Entry VALUES(?, ?, ?);",
			(None, self.usr_id, quote))

		self.db.execute("SELECT last_insert_rowid();")
		quote_id = self.db.fetchall()

		quote_id = quote_id[0][0]
		self.irc.util.say("Added quote: " + str(quote_id), message.channel)

	def quote(self, message):
		if self.length == 1:
			if message.message[0].isdigit():
				quote_id = int(message.message[0])
			else:
				self.irc.util.say("Unknown quote format, use: >quote id",
					message.channel)
				return

			# Make sure the ID isn't ridiculously large, causes traceback
			if len(str(message.message[0])) > 15:
				self.irc.util.say("That's a preposterous number, bro",
					message.channel)
				return
		else:
			quote_id = 0

		if quote_id == 0:
			self.db.execute("SELECT * FROM Quote_Entry ORDER BY RANDOM()"
				+ " LIMIT 1;")
		else:
			self.db.execute("SELECT * FROM Quote_Entry WHERE quote_id = "
				+ "?;", (quote_id,))

		rows = self.db.fetchall()
		print("rows length: " + str(len(rows)))
		print(rows)

		if len(rows) == 0:
			self.irc.util.say("No quote by this ID found", message.channel)
			return

		print(rows[0])
		quote_id = rows[0][0]
		usr_id = rows[0][1]
		quote = rows[0][2]

		output = "Quote " + str(quote_id) + ": \"" + quote + "\"; by: "
		output += str(usr_id)

		vote_stats = self.get_vote_stats(quote_id)

		output += "; Votes: " + str(vote_stats[0]) + "/"
		output += str(vote_stats[1]) + " = " + str(vote_stats[2])

		self.irc.util.say(output, message.channel)

	def delquote(self, message):
		if self.length == 0 or message.message[0].isdigit() == False:
			self.irc.util.say("FALSE! Do this: >delquote [quote id]",
				message.channel)
			return

		quote_id = message.message[0]
		print(quote_id)

		# See if this quote belongs to this user
		self.db.execute("SELECT user_id FROM Quote_Entry WHERE quote_id"
			+ " = ?;", (quote_id,))

		rows = self.db.fetchall()

		if len(rows) == 0:
			self.irc.util.say("Quote doesn't exist", message.channel)
			return

		quote_user = rows[0][0]

		# if the quote belongs to this user, delete
		if self.usr_id == quote_user:
			self.db.execute("DELETE FROM Quote_Entry WHERE quote_id"
				+ " = ?;", (quote_id,))
			self.db.execute("DELETE FROM Quote_Credentials WHERE quote_id"
				+ " = ?;", (quote_id,))
			self.irc.util.say("Deleted.", message.channel)
		else:
			self.irc.util.say("This quote doesn't belong to you.",
				message.channel)

	def vote(self, message):
		proper_parameters = "NO! Like this: >vote [quote id] " \
			+ "[\"up\"/\"down\"]"

		# check synatx
		if self.length == 0:
			self.irc.util.say(proper_parameters, message.channel)
			return
		elif self.length >= 2:
			if message.message[1].lower() == "up":
				vote = 1
			elif message.message[1].lower() == "down":
				vote = -1
			else:
				self.irc.util.say(proper_parameters, message.channel)
				return
		else:
			self.irc.util.say(proper_parameters, message.channel)
			return

		# see if this user exists
		if self.usr_id == -1:
			self.irc.util.say("User unknown, try again.", message.channel)

		# see if this quote is valid
		if message.message[0].isdigit() == False:
			self.irc.util.say(proper_parameters, message.channel)
			return

		quote_id = message.message[0]

		self.db.execute("SELECT quote FROM Quote_Entry WHERE quote_id"
			+ " = ?;", (quote_id,))
		rows = self.db.fetchall()

		if len(rows) == 0:
			self.irc.util.say("This quote doesn't exist.", message.channel)
			return

		# see if this user has already voted for this quote
		self.db.execute("SELECT vote FROM Quote_Credentials WHERE user_id"
			+ " = ? AND quote_id = ?", (self.usr_id, quote_id,))
		rows = self.db.fetchall()

		# if this user hasn't before voted on this quote, create one
		if len(rows) == 0:
			self.db.execute("INSERT INTO Quote_Credentials "
				+ "VALUES(?, ?, ?)", (self.usr_id, quote_id, vote))
			self.irc.util.say("Updated quote stats: " + str(quote_id),
				message.channel)
		# if they have, change their vote; show previous
		else:
			prev_vote = rows[0][0]

			if prev_vote == 1:
				prev_vote = "up"
			else:
				prev_vote = "down"

			self.db.execute("UPDATE Quote_Credentials SET vote = ?"
				+ " WHERE user_id = ? AND quote_id = ?;",
					(vote, self.usr_id, quote_id))
			self.irc.util.say("Updated quote: " + str(quote_id)
				+ " Previous record: " + prev_vote, message.channel)

		# show this quote's upvote/downvote ratio and total
		vote_stats = self.get_vote_stats(quote_id)
		self.irc.util.say("This quote's upvotes: " + str(vote_stats[0])
			+ "; downvotes: " + str(vote_stats[1]) + "; total: "
			+ str(vote_stats[2]), message.channel)