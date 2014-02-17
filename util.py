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

# util.py

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
	
	def say_action(self, string, channel):
		action = '\x01'
		say = action + string + action
		self.say(say, channel)