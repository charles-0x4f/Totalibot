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

# totalibot.py
# Totalibot
# Cause the original name was taken.

import sys
import os
import time
# Add our scripts directory to the Python path
sys.path.append(sys.path[0] + os.sep + "scripts")

import irc
import util
import structures
import config_loader

# Load IRC parameters from a file
irc_params = config_loader.load()

# Check our command line arguments for debug level, default to 0 (don't print)
if len(sys.argv) > 1:
	if sys.argv[1].isdigit() == True:
		debug = int(sys.argv[1])
		print("Debug level: " + str(debug))

# initialize IRC client
irc = irc.IRC(irc_params, debug)

# dynamically import and instantiate all plugins/.py files in the scripts dir:
scripts_dir = []
plugins = []

# Get a list of all .py files in the scripts directory, minus ".py"
for file in os.listdir(sys.path[0] + os.sep + "scripts"):
	if file.endswith(".py"):
		scripts_dir.append(file[:-3])

# for each file we found
for mod in scripts_dir:
	try:
		# try to import it
		modules = __import__(mod, globals(), locals(), fromlist=["*"])

		for obj in dir(modules):
			try:
				print("Loading plugin: " + repr(obj))
				new_plugin = getattr(modules, obj)(irc)
				plugins.append(new_plugin)
				break
			except:
				print("Failed to load plugin")
				traceback.print_exc()
				break
				pass
	except:
		print("Failed to import plugin")
		pass

# do some setup with the utility module
irc.util.auto_join(irc_params.channels)
irc.util.set_connect_command(irc_params.connect_command)
irc.util.set_password(irc_params.password)
irc.util.set_version(irc_params.version)

# connect to the IRC server
irc.connect()

while 1:
	if irc.has_messages() == True:
		#print("queue length: " + str(len(irc.message_queue)))
		message = irc.message_queue.pop(0)
		
		# loop through our handlers
		for handler in plugins:
			try:
				# if this handler handles this type of message, pass it
				if message.type in handler.types:
					handler.message_handler(message)
			except:
				print("FAILURE: Plugin damaged or not written correctly," +
					" removing it from plugin pool")
				plugins.remove(handler)

				# when a plugin is removed, the message stops getting handled
				# re-insert this message to the top of the queue
				irc.message_queue = [message] + irc.message_queue
				
				# continue or some plugins may process the same message twice
				continue
	else:
		time.sleep(1)
				