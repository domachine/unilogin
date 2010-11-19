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

from urllib.request import urlopen


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
        self._data = data

    def login(username, password):
        """
        Logs into the network using ``username`` and ``password``.
        An IOError is raised if something goes wrong.

        Parameters:
        * ``username`` (str): The username used to login.
        * ``password`` (str): The password used to login.
        """

        pass

class Agent(object):
    def __init__(self):
        """
        Initializes the Agent object.
        """

        self._form_regex = None
        self._data_regex = None
        self._end_form_regex = None
        self._end_form_regex = None

    def login_manager(self, register_url="http://uni-ulm.de"):
        """
        Retrieves form data from the ``register_url``
        and initializes a suitable LoginManager that can then
        be used for login.

        Parameters:
        ``register_url`` (str): The url to get the form data from.
        """

        # TODO: Implement it :-)
        pass

    @property
    def form_regex(self):
        if self._form_regex is None:
            self._compile_regex("_form_regex",
                                r'.*form *method="post" *action="([^"]+)".*',
                                re.IGNORECASE)

        return self._form_regex

    @property
    def data_regex(self):
        if self._data_regex is None:
            self._compile_regex("_data_regex",
                                r'.*type="hidden" *name="([^"]+)" *value="([^"]*)".*',
                                re.IGNORECASE)

        return self._data_regex

    @property
    def end_form_regex(self):
        if self._end_form_regex is None:
            self._compile_regex("_end_form_regex",
                                r"[ \t]*<\/ *form *>[ \t]*",
                                re.IGNORECASE)

        return self._end_form_regex

    @property
    def logout_regex(self):
        if self._logout_regex is None:
            self._compile_regex("_logout_regex",
                                r".*<h1>Logout OK<\/h1>.*",
                                re.IGNORECASE)

    def _compile_regex(name, pattern):
        self.__dict__[name] = re.compile(pattern)
