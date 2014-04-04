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

# Add our script directories to the Python path
sys.path.append(sys.path[0] + os.sep + "core")
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
else:
	debug = 0

# initialize IRC client
irc = irc.IRC(irc_params, debug)

# do some setup with the utility module
irc.util.auto_join(irc_params.channels)
irc.util.set_connect_command(irc_params.connect_command)
irc.util.set_password(irc_params.password)
irc.util.set_version(irc_params.version)

# connect to the IRC server
irc.connect()

while 1:
	irc.dispatch_message()
	time.sleep(1)
				