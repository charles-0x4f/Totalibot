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

# users_db.py

# This all needs to be redone using some sort of relational database, methinks
# Expanded channel information
class ChannelList:
	class User:
		def __init__(self):
			self.status = ""
			self.user = ""
	
	class Channel:
		def __init__(self):
			self.name = ""
			self.topic = ""
			self.user_list = []
	
	def __init__(self):
		self.channel_list = []
		self.specials = ["@", "+"]
	
	def get_index(self, channel_string):
		for chan in self.channel_list:
			if chan.name == channel_string:
				return self.channel_list.index(chan)
		
		return -1
	
	def add_user(self, channel_string, user_names):
		for user in user_names:
			if self.is_user_in(channel_string, user) == False:
				temp_user = ChannelList.User()
				index = self.get_index(channel_string)
				
				# if this user has a status (op, voice, etc.)
				if user[0] in self.specials:
					temp_user.status = user[0]
					temp_user.user = user[1:]
				else:
					# set username if it has no status
					temp_user.user = user
				
				#print("!!!ADDING USER: " + user)
				self.channel_list[index].user_list.append(temp_user)
	
	def add_channel(self, channel_obj):
		# if this channel doesn't exist, add
		if self.get_index(channel_obj.name) == -1:
			self.channel_list.append(channel_obj)
	
	def part(self, channel_string, user_string):
		if self.is_user_in(channel_string, user_string) == True:
			index = self.get_index(channel_string)
			
			# if this channel exists
			if index > -1:
				# iterate over all User objects belonging to this channel
				for user_obj in self.channel_list[index].user_list:
					# find User object and remove
					if user_obj.user == user_string:
						self.channel_list[index].user_list.remove(user_obj)
				
	def quit(self, user_string):
		for chan_obj in self.channel_list:
			self.part(chan_obj.name, user_string)
	
	def is_user_in(self, channel_string, user_string):
		numchannels = len(self.channel_list)
		#print("!!!numchannels: " + str(numchannels))
		for chan_obj in self.channel_list:
			#print("!!!userin chan: " + chan.name)
			if chan_obj.name == channel_string:
				for user_obj in chan_obj.user_list:
					if user_obj.user == user_string:
						return True
		
		#print("!!!" + user + " NOT IN " + channel)
		return False