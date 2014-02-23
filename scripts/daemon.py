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

# daemon.py
# Spawn a new IRC instance with a semi-randomized nick and user/ident name, join
# a specific channel, execute a specific command, and quit. Lots of potential
# misuse.

# TODO: this will leave threads running in infinite loops in the background
# eating CPU, get all of those hammered out

import random
import time
from threading import Thread

import irc
import structures

class Daemon:
    def __init__(self, IRC):
        self.IRC = IRC
        self.types = ["pm"]
        self.timer_length = None
        self.iterations = None
        self.target_channel = ""
        self.action = ""
        self.cancel = False

        self.daemon_thread = None

    def message_handler (self, message):
        # make sure this is the daemon command
        if message.message[0].lower() != ":daemon":
            return

        # check root
        if self.IRC.util.is_root(message.sender_full) == False:
            self.IRC.util.say("You are not rooted", message.sender)
            return

        if message.message[0].lower() == ":cancel":
            self.cancel = True
            return

        # check length > 4
        if len(message.message) < 4:
            self.IRC.util.say("Not enough paramaters: sleep_time iterations" +
                " channel raw_command", message.sender)
            return

        if message.message[0].lower() == ":daemon":
            # Get timer length and iterations from message paramaters
            # TODO: add error messages to these
            if message.message[1].isdigit() == True:
                self.timer_length = int(message.message[1])
            if message.message[2].isdigit() == True:
                self.iterations = int(message.message[2])

            self.target_channel = message.message[3]
            self.action = " ". join(message.message[4:])
       
            # check channel validity
            if len(self.target_channel) == 0:
                return

            # run daemon() in thread
            print("Starting daemon thread")
            self.daemon_thread = Thread(target=self.daemon).start()
            print("Daemon: TESTING")

    def daemon(self):
        for i in range (0, (self.iterations)):
            print("Daemon: New Daemon iteration")

            # See if we've canceled
            if self.cancel == True:
                return

            # get server information needed for connecting
            irc_params = structures.IRC_Parameters()
            irc_params.server = self.IRC.server
            irc_params.port = self.IRC.port
            irc_params.use_ssl = self.IRC.use_ssl
            irc_params.nick = ""
            irc_params.ident = ""
            irc_params.realname = "Daemon"

            # many IRC bots unly use "user" name for identification
            # making these random should trick them
            irc_params.nick = "u" + str(random.randint(10000, 1000000))
            irc_params.ident = "u" + str(random.randint(10000, 1000000))

            irc_obj = irc.IRC(irc_params, 0)
            channel = [self.target_channel]
            #irc_obj.util.auto_join(channel)

            # Yay everything's-public-python
            if self.IRC.util.send_connect_command == True:
                irc_obj.util.set_connect_command(self.IRC.util.connect_command)
            irc_obj.connect()

            # can't join a channel until the user is registered
            for i in range(0, 20):
                if irc_obj.is_ready == False:
                    print("Daemon: NOT READY")
                    time.sleep(1)
                else:
                    break

                if i == 19:
                    print("Daemon: FAILED?")
                    irc_obj.quit("I HAS FAILED YOU, MASTER!")
                    return

            irc_obj.join_channels(channel)
            time.sleep(2)

            irc_obj.send_raw_command(self.action)
            irc_obj.quit(self.IRC.nick + " CONQUERS ALL")
            #del irc_obj
            #irc_obj.sock.close()

            print("Gonna sleep now")
            print("I :" + str(i))
            time.sleep(self.timer_length)

        print("Done now")
        #self.daemon_thread.stop()
        return