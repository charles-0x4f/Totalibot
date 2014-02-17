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

# schmibersee.py
# IRC bot, Schmibersee bot
# Cause the original name was taken.

'''
Add our scripts directory to the Python path
sys.path[0] is the current directory this .py is in
//scripts should work on both Windows and *Nix style
directories
'''
import sys
sys.path.append(sys.path[0] + "//scripts")

import time

import irc
import util
import user_manager
import automated
import pm_commands
import war
import daemon

# pull this from a file
server = ""
port = None
use_ssl = False
nick = ""
ident = ""
realname = ""
version = ""
channels = []
owner = ""
password = ""
connect_command = ""
debug = 0

# move file stuff to a different file?
# try to open config.txt
try:
	file = open("config.txt", "r")
except(OSError, IOError) as ex:
	# do something with ex
	print("No config.txt or serious error")

	print("Creating empty config.txt")
	config_string = "# comma separate channels or where there's multiples" + \
		"\nserver=\nport=\nuse_ssl=\nnick=\nident=\n" + \
		"realname=\nversion=\nchannels=\nowner=\npassword=\nconnect_command="
	file = open("config.txt", "w")
	file.write(config_string)
	file.close()
	exit()

# start reading values from config.txt
# TODO: test to make sure this works with UNIX-style newlines
for line in file:
	# Split the line into segments and make sure there's no gunk at the end
	split_values = line.partition("=")
	command = split_values[0]
	value = split_values[2].rstrip("\n")

	print("File value: #" + value + "#")

	# sure wish python had switches that handled strings
	if command == "server":
		server = value
	elif command == "port":
		if value.isdigit() == True:
			port = int(value)
		else:
			print("Port not recognized, gonna die nao")
			exit()
	elif command == "use_ssl":
		if value == "True":
			use_ssl = True

			if port == 6667:
				print("SSL doesn't usually run on this port")
	elif command == "nick":
		nick = value
	elif command == "ident":
		ident = value
	elif command == "realname":
		realname = value
	elif command == "version":
		version = value
	elif command == "channels":
		channels = value.split(",")
	elif command == "owner":
		owner = value
	elif command == "password":
		password = value
	elif command == "connect_command":
		connect_command = value
	else:
		# modify this to only require most essential needs
		print("Something's missing, please fill out config.txt")
		print(line)
		exit()

# close this puppy out
file.close()

# Check our command line arguments for debug level, default to 0 (don't print)
if len(sys.argv) > 1:
	if sys.argv[1].isdigit() == True:
		debug = int(sys.argv[1])
		print("Debug level: " + str(debug))

# initialize IRC client
irc = irc.IRC(server, port, use_ssl, nick, ident, realname, debug)

# do some setup with the utility module
irc.util.auto_join(channels)
irc.util.set_connect_command(connect_command)
irc.util.set_password(password)
irc.util.set_version(version)

# TODO: Make this completely dynamic
# initialize list of handler classes/modules
user_mngr = user_manager.UserManager(irc)
auto = automated.Automated(irc)
commands_pm = pm_commands.PM_Commands(irc)
cmd_war = war.War(irc)
cmd_daemon = daemon.Daemon(irc)

# add handlers to the handlers list
handlers = []
handlers.append(user_mngr)
handlers.append(auto)
handlers.append(commands_pm)
handlers.append(cmd_war)
handlers.append(cmd_daemon)

# connect to the IRC server
irc.connect()

while 1:
	if irc.has_messages() == True:
		#print("queue length: " + str(len(irc.message_queue)))
		message = irc.message_queue.pop(0)
		
		# loop through our handlers
		for handler in handlers:
			# if this handler handles this type of message, pass it
			if message.type in handler.types:
				handler.message_handler(message)
	else:
		time.sleep(1)
				