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

# util.py

import sys
import os
import imp
import traceback

import irc

class Util:
	def __init__(self, IRC):
		self.irc = IRC
		
		# initialization
		self.autojoin = False
		self.send_connect_command = False
		self.version_set = False
		
		self._channels = []
		self.connect_command = ""
		self.version = ""
		
		self.master_hostname = []
		self.master_password = ""
	
	def auto_join(self, channels):
		self._channels = channels
		self.autojoin = True
	
	def set_version(self, version):
		self.version = version
		self.version_set = True
		
	def set_connect_command(self, command):
		self.send_connect_command = True
		self.connect_command = command
		
	def set_password(self, password):
		self.master_password = password
	
	def login(self, user, password):
		if password == self.master_password:
			if user not in self.master_hostname:
				self.master_hostname.append(user)
				return True
		
		return False
	
	def is_root(self, user):
		if user in self.master_hostname:
			return True
		
		return False
	
	def say(self, string, channel):
		self.irc.send_raw_command("PRIVMSG " + channel + " :" + string)
	
	# /me chat
	def say_action(self, string, channel):
		action = '\x01'
		say = action + string + action
		self.say(say, channel)

	# Chop the full sender field into usable segments
	# example: nick!user@hostname = tuple(nick, user, host)
	def get_sender_fields(self, senderfull):
		# if this isn't a correct full sender, return False
		if '@' not in senderfull or '!' not in senderfull:
			return False

		buff = senderfull.split('@')
		host = buff[1]
		buff = buff[0]
		buff = buff.split('!')
		nick = buff[0]
		user = buff[1]

		return (nick, user, host)

	# dynamically import and instantiate all plugins/.py files in the specified
	# directory
	def load_plugins(self, directory):
		scripts_dir = []
		plugins = []

		# reset IRC object's list of plugins
		self.irc.initiated_plugins = []

		# Get a list of all .py files in the directory, minus ".py"
		for file in os.listdir(sys.path[0] + os.sep + directory):
			if file.endswith(".py"):
				scripts_dir.append(file[:-3])

		# for each file we found
		for mod in scripts_dir:
			try:
				# if trying to reload a module that was already imported
				if mod in sys.modules:
					imp.reload(sys.modules[mod])
					obj = dir(sys.modules[mod])[0]
					# create a new instance of this module because the
					# previous instance was probably from the old module,
					# it was also destroyed.
					plug = getattr(sys.modules[mod], obj)(self.irc)
					self.irc.initiated_plugins.append(plug)
					continue
				else:
					# try to import it
					modules = __import__(mod, globals(), locals(), fromlist=["*"])

				for obj in dir(modules):
					try:
						print("Loading plugin: " + repr(obj))
						new_plugin = getattr(modules, obj)(self.irc)
						self.irc.initiated_plugins.append(new_plugin)
						break
					except:
						print("Failed to load plugin")
						traceback.print_exc()
						break
						pass
			except:
				print("Failed to import plugin")
				traceback.print_exc()
				pass

		self.irc.reload_plugins = True