#!/usr/bin/env python
# This program makes it easy to login to the wireless network of the
# university of Ulm.
# Copyright (C) 2010  Dominik Burgdörfer <dominik.burgdoerfer@googlemail.com>

# This file is part of unilogin.

# unilogin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# unilogin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with unilogin.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os.path
import termios
from optparse import OptionParser

import unilogin


def error(msg):
    print(os.path.basename(sys.argv[0]) +
          ": " + msg, file=sys.stderr)


def prompt_for_username(msg="Username: "):
    username = ""

    while not username:
        username = input(msg)

    return username


def prompt_for_password(msg="Password: "):
    default = termios.tcgetattr(sys.stdout)
    noecho = termios.tcgetattr(sys.stdout)

    noecho[3] &= ~termios.ECHO

    try:
        termios.tcsetattr(sys.stdout, termios.TCSADRAIN, noecho)
        pwd = input(msg)
        print()
    finally:
        termios.tcsetattr(sys.stdout, termios.TCSADRAIN, default)

    return pwd


def main(argv):
    username = str()
    password = str()

    parser = OptionParser()

    parser.add_option("-u", "--user",
                      action="store", dest="username")
    parser.add_option("-p", "--password",
                      action="store", dest="password")

    options, args = parser.parse_args()

    agent = unilogin.Agent()

    if len(args) > 0:
        if args[0] == "logout":
            print("Logging out ...", end="")
            sys.stdout.flush()

            if agent.logout():
                # Ultra Hack.
                print("\r               \rLogout ok")
                return 0
            else:
                print("\r               \rLogout failed")
                return 1
        elif args[0] != "login":
            error("Invalid additional argument: " + args[0])
            return 1

    if options.username is None:
        username = prompt_for_username()
        # error("No user specified.")
        # sys.exit(1)
    else:
        username = options.username

    if options.password is None:
        password = prompt_for_password()
    else:
        password = options.password

    print("Logging in ...", end="")
    sys.stdout.flush()

    try:
        ret = agent.login(username, password)
    except IOError as e:
        print("\r", file=sys.stderr, end="")
        sys.stderr.flush()

        error(str(e))
        return 1

    if ret:
        print("\rSuccessfully logged in!")
        return 0
    else:
        print("\rLogin failed! ")
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
