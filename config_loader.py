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

# config_loader.py
# Load settings from the config file

import structures

def load():
    params = structures.IRC_Parameters()

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
        # if this line starts with "#", it's a comment, skip line
        if line[0] == "#":
            print("Comment line, skip")
            continue

        # Split the line into segments and make sure there's no gunk at the end
        split_values = line.partition("=")
        command = split_values[0]
        value = split_values[2].rstrip("\n")

        print("File value: #" + value + "#")

        # sure wish python had switches that handled strings
        if command == "server":
            params.server = value
        elif command == "port":
            if value.isdigit() == True:
                params.port = int(value)
            else:
                print("Port not recognized, gonna die nao")
                exit()
        elif command == "use_ssl":
            if value == "True":
                params.use_ssl = True

                if params.port == 6667:
                    print("SSL doesn't usually run on this port")
        elif command == "nick":
            params.nick = value
        elif command == "ident":
            params.ident = value
        elif command == "realname":
            params.realname = value
        elif command == "version":
            params.version = value
        elif command == "channels":
            params.channels = value.split(",")
        elif command == "owner":
            params.owner = value
        elif command == "password":
            params.password = value
        elif command == "connect_command":
            params.connect_command = value
        else:
            # modify this to only require most essential needs
            print("Something's missing, please fill out config.txt")
            print(line)
            exit()

    return params

    # close this puppy out
    file.close()