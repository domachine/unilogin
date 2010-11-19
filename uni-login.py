#!/usr/bin/python
# Author: Dominik Burgdoerfer <dominik.burgdoerfer@uni-ulm.de>
# Script to login automatically to the wireless lan of the university of ulm.
#
# Changelog:
#     Version 0.1.1 (Rewrite in Python)
#       - Replaced crappy perl error handling with clear python-exceptions
#       - Replaced wget call with urllib.
#
#       - TODO:
#         Make this whole thing pythonic object oriented.
#
#     Version 0.1.0
#       - pretty quick and dirty.
#       - needs to do logging of potential errors.

import sys
from urllib.request import urlopen
import re
from os import environ


form_regex = re.compile(r'.*form *method="post" *action="([^"]+)".*',
                        re.IGNORECASE)

def retrieve_form_data():
    fd = urlopen("http://uni-ulm.de")

    data_regex = re.compile(r'.*type="hidden" *name="([^"]+)" *value="([^"]*)".*',
                            re.IGNORECASE)
    end_form_regex = re.compile(r"[ \t]*<\/ *form *>[ \t]*",
                                re.IGNORECASE)

    # The dictionary to output the post-data to.
    post_data = dict()
    url = None

    num_of_lines = 0

    for line in fd:
        line = line.decode("utf-8")
        m = data_regex.match(line)

        if m is not None:
            post_data[m.group(1)] = m.group(2)
        else:
            m = form_regex.match(line)

            if m is not None:
                url = m.group(1)
            else:
                m = end_form_regex.match(line)

                if m is not None:
                    break

        num_of_lines += 1

    fd.close()

    if url is not None and post_data:
        return (url, post_data)
    else:
        if(num_of_lines):
            raise IOError("Already logged in.")
        else:
            raise RuntimeError("Unknown error. No data received. " +
                               "This might be a bug.")


def login(url, post_data):
    fd = urlopen(url, post_data)

    logged_in = True
    

    # Search for login form. If it exists, the login failed.
    for line in fd:
        # Decode byte-array to string.
        line = line.decode("utf-8")
        m = form_regex.match(line)

        if m is not None:
            # Verify form url.
            if m.group(1) == url:
                logged_in = False
                break

    fd.close()

    return logged_in

def logout():
    logout_regex = re.compile(r".*<h1>Logout OK<\/h1>.*",
                              re.IGNORECASE)

    fd = urlopen("http://welcome.uni-ulm.de/logout.html")
    logged_out = False

    for line in fd:
        if logout_regex.match(line):
            logged_out = True
            break

    fd.close()

    return logged_out

def main(argv):
    user = str()
    password = str()

    print("Retrieving login data ...", end="")
    sys.stdout.flush()

    data = None

    try:
        data = retrieve_form_data()
        print(" [OK]")
    except IOError as e:
        print("\r[FAILED]: " + str(e))

        return 1

    print("Loggin in ...", end="")
    sys.stdout.flush()

    if login(*data):
        print(" [OK]")
    else:
        print("\rLogin failed!")
        return 1

    return 0

if __name__ == "__main__":
    ret = main(sys.argv)

    sys.exit(ret)
