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

# structures.py
# Define empty structures for use in the bot

# Used as a way to pass message details around the bot
class Message:
    types = ["response", "message", "notice", "pm", "ctcp", "command",
        "join", "part", "kick", "mode", "nick"]
    type = ""
    code = ""
    sender = ""
    sender_full = ""
    channel = ""
    command = ""
    message = []

# Used as a container for the many variables required to start an IRC session
class IRC_Parameters:
    def __init__(self):
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