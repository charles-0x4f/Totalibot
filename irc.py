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

# irc.py
# This class handles all of the most essential IRC protocol stuff

import sys
import socket
import ssl
import string
import time
from threading import Thread

import util
import structures
import users_sqlite

# Main IRC class, handles all the protocol details
class IRC:
	def __init__(self, parameters, debug):
		self.server = parameters.server
		self.port = parameters.port
		self.use_ssl = parameters.use_ssl
		self.nick = parameters.nick
		self.ident = parameters.ident
		self.realname = parameters.realname
		self.debug_level = debug
		
		# reserve empty lists
		#self.channels = users_db.ChannelList()
		self.sql = users_sqlite.Database(self, self.server)
		self.message_queue = []
		
		# values that the bot may need in the future
		self.buffer = ""
		self.server_host = ""
		self.is_connected = False
		self.is_ready = False
		self.receive_thread = None
		self.initiated_plugins = []
		self.reload_plugins = False
		
		# create a Util object
		self.util = util.Util(self)
		# load our plugins
		self.util.load_plugins("scripts")
		
		self.sock = None
		
	def __receive(self):
		while self.is_connected == True:
			'''
			this method of receiving data may cut off messages, splitting
			them into different buffers, which causes partial messages
			and strange behavior from the parser
			'''
			data = self.sock.recv(1024)
			# convert bytes to unicode string, ignore unicode errors or it'll
			# die on weird unicode IRC art
			self.buffer += data.decode('utf-8', 'ignore')

			# we're going to make sure the messages aren't cutoff
			# partition buffer by the last \r\n
			partition = self.buffer.rpartition("\r\n")
			raw = partition[0] + "\r\n"
			self.buffer = partition[2]

			# call parser
			self.__parser(raw)
		
	def connect(self):
		s = socket.socket()
		s.connect((self.server, self.port))

		if self.use_ssl == True:
			self.sock = ssl.wrap_socket(s)
		else:
			self.sock = s
		self.is_connected = True
		self.receive_thread = Thread(target=self.__receive).start()

		print("Connected to: " + self.server + ":" + str(self.port))
		
		# send user information
		# wait a second
		#time.sleep(1)
		self.send_raw_command("PASS mypass")
		self.send_raw_command("NICK " + self.nick)
		self.send_raw_command("USER " + self.ident + " " + self.server +
			" narf " + ":" + self.realname)
		
	def send_raw_command(self, string):
		# Python 3.3 string literals are stupid
		#utf = bytes((string + "\r\n"), 'utf-8')
		
		# Printing Unicode characters on Windows = exception
		try:
			print("Send: " + string)
		except:
			print("Send: Unicode error(?)")

		string += "\r\n"
		self.sock.send(string.encode("utf-8"))
		
	def join_channels(self, string):
		if len(string) > 0:
			for index in range(len(string)):
				self.send_raw_command("JOIN " + string[index])
	
	def has_messages(self):
		if len(self.message_queue) > 0:
			return True
		
		return False

	# Send QUIT message and stop child threads
	def quit(self, string):
		self.send_raw_command("QUIT :" + string)
		self.is_connected = False
		#self.receive_thread.stop()
		#exit()

	def __parser(self, raw):
		# multiple messages can come at once so split them up
		messages = raw.split("\r\n")
		# delete garbage message at the end
		messages.pop()
		
		# loop through all messages
		for line in messages:
			line_length = len(line)

			# if line is empty, skip
			if line_length == 0:
				#print("null")
				continue
		
			# Note: Windows command line will crash on unicode errors
			# cause it's 1998
			try:
				# if debug level > 0 print the line; expand this
				if self.debug_level > 0:
					print("line: " + line)
			except:
				print("Unicode Error(?)")
		
			# split line into whitespace separated list
			line = line.split()
			# redefine line length to mean number of words in split line
			line_length = len(line)
			
			# hack; this shouldn't run anymore
			if line_length < 2:
				print("HACK!")
				continue

			# check for PING messages and respond immediately
			if line[0] == "PING":
				self.send_raw_command("PONG " + line[1])
				print("PONG!")
				continue
			
			# if we aren't fully ready, save our host string
			if self.is_ready == False:
				# 002 is the "Your host is x" response code
				if line[1] == "002":
					# host will be the sixth word of the line, remove
					# trailing comma
					self.server_host = line[6].rstrip(',')
					continue
				
				# 376 is the response code for the end of the MOTD, signaling
				# that we are free to join channels, set is_ready
				if line[1] == "376":
					print("IS READY")
					self.is_ready = True
				
			# temporary message object to be added to message queue
			message = structures.Message()
			
			# see if this is a response code message
			if (len(line[1]) == 3) and (line[1].isdigit() == True):
				message.type = "response"
				message.code = line[1]
				
				# fill the message part of the Message object
				message.message = line[3:]
			
			# set sender_full to the sender's full nick and host
			message.sender_full = line[0][1:]
			# get sender (username!host)
			message.sender = line[0][1:].split('!')[0]
			
			# core message parsing
			if line[1] == "PRIVMSG":

				# if this message is to me, it's a PM
				if line[2] == self.nick:
					# ctcp messages always start and end with a 0x01 byte
					if line[3][1] == '\x01':
						print("type: ctcp")
						message.type = "ctcp"
					else:
						message.type = "pm"
					
					message.channel = message.sender
					message.message = line[3:]

				else:
					# if this say message starts with >, it's a command
					if line[3][:2] == ":>":
						message.type = "command"
						message.channel = line[2]
						message.command = line[3][2:].lower()
						message.message = line[4:]
					# otherwise this is a normal chat
					else:
						message.type = "message"
						message.channel = line[2]
						message.message = line[3:]

			elif line[1] == "NOTICE":
				message.type = "notice"
				message.message = line[3:]

			elif line[1] == "JOIN":
				message.type = "join"

				if line[2][0] == ":":
					# strip the leading ':'
					message.channel = line[2][1:]
				else:
					message.channel = line[2]
				
			elif line[1] == "PART" or line[1] == "QUIT":
				message.type = "part"
				# definitive way to tell part/quit apart is by the code
				message.code = line[1]
				
				if line[1] == "PART":
					message.channel = line[2]
					
					# if there's a part message
					if line_length > 3:
						message.message = line[3:]
				else:
					# This is a quit message
					message.message = line[2:]

			elif line[1] == "NICK":
				message.type = "nick"

				# if there's a NICK command, message.sender will be the new
				# nick and sender_full will have the old one in it
				message.sender = line[2]

			elif line[1] == "MODE":
				# we only care about modes that change user statuses for now
				# (+o -v, etc.)
				if line_length < 5:
					return

				message.type = "mode"
				message.channel = line[2]
				# the action (+o) will be in the code
				message.code = line[3]
				# the message is the user on the receiving end
				message.message = line[4]

			elif line[1] == "KICK":
				message.type = "kick"
				message.channel = line[2]
				# code will be the one getting kicked
				message.code = line[3]

				if line_length >= 5:
					message.message = line[4:]

			elif len(message.type) == 0:
				message.type = "unknown"
				message.channel = line[1]
				message.message = line[3:]
			
			# mark that we have a new message
			self.message_queue.append(message)
		