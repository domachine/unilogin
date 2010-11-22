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

import re
from urllib.request import urlopen
from urllib.parse import urlencode


__all__ = ["Agent"]

class LoginManager(object):
    """
    Cares about the final login process to the network.
    An object of this class is usually created through the Agent.
    """

    def __init__(self, parent, url, data):
        """
        Initializes the Manager with the form data and the
        url to call.
        """

        self._parent = parent
        self._url = url
        self._post_data = data

    def login(self, username, password):
        """
        Logs into the network using ``username`` and ``password``.
        An IOError is raised if something goes wrong.

        Parameters:
        * ``username`` (str): The username used to login.
        * ``password`` (str): The password used to login.
        """

        post_data = self._post_data.copy()
        post_data.update({"user": username, "pass": password})

        data_encoded = urlencode(post_data)

        fd = urlopen(self._url, data_encoded)

        logged_in = True

        # Search for login form. If it exists, the login failed.
        for line in fd:
            # Decode byte-array to string.
            line = line.decode("utf-8")
            m = self._parent.form_regex.match(line)

            if m is not None:
                # Verify form url.
                if m.group(1) == self._url:
                    logged_in = False
                    #break

        fd.close()

        return logged_in

    def logout(self):
        """
        Logs the LoginManager out.

        Returns: True if everything was successful and False if something went
                 wrong.
        """

        fd = urlopen("http://welcome.uni-ulm.de/logout.html")
        logged_out = False

        for line in fd:
            line = line.decode("utf-8")

            if self._parent.logout_regex.match(line):
                logged_out = True
                break

        fd.close()

        return logged_out


class Agent(object):
    """
    An example session could look like this:

    >>> from unilogin import Agent
    >>> a = Agent()
    >>> log = None
    >>> log = a.login_manager()
    >>> log.login("s_dburgd", "<password>")
    True
    >>> log.logout()
    True
    """

    def __init__(self):
        """
        Initializes the Agent object.
        """

        self._form_regex = None
        self._data_regex = None
        self._end_form_regex = None
        self._logout_regex = None

    def login_manager(self, register_url="http://uni-ulm.de"):
        """
        Retrieves form data from the ``register_url``
        and initializes a suitable LoginManager that can then
        be used for login.

        Parameters:
        ``register_url`` (str): The url to get the form data from.
        """

        fd = urlopen(register_url)

        # The dictionary to output the post-data to.
        post_data = dict()
        url = None

        num_of_lines = 0

        for line in fd:
            line = line.decode("utf-8")
            m = self.data_regex.match(line)

            if m is not None:
                post_data[m.group(1)] = \
                    m.group(2)
            else:
                m = self.form_regex.match(line)

                if m is not None:
                    url = m.group(1)
                else:
                    m = self.end_form_regex.match(line)

                    if m is not None:
                        break

        num_of_lines += 1

        fd.close()

        if url is not None and post_data:
            return LoginManager(self, url, post_data)
        else:
            if(num_of_lines):
                raise IOError("Already logged in.")
            else:
                raise RuntimeError("Unknown error. No data received. " +
                                   "This might be a bug.")

    @property
    def form_regex(self):
        if self._form_regex is None:
            self._compile_regex("_form_regex",
                                r'.*form *method="post" *action="([^"]+)".*')

        return self._form_regex

    @property
    def data_regex(self):
        if self._data_regex is None:
            self._compile_regex("_data_regex",
                                r'.*type="hidden" *name="([^"]+)" *value="([^"]*)".*')

        return self._data_regex

    @property
    def end_form_regex(self):
        if self._end_form_regex is None:
            self._compile_regex("_end_form_regex",
                                r"[ \t]*<\/ *form *>[ \t]*")

        return self._end_form_regex

    @property
    def logout_regex(self):
        if self._logout_regex is None:
            self._compile_regex("_logout_regex",
                                r".*<h1>Logout OK<\/h1>.*")

        return self._logout_regex

    def _compile_regex(self, name, pattern):
        self.__dict__[name] = re.compile(pattern,
                                         re.IGNORECASE)
