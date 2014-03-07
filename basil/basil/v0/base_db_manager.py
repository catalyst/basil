"""
Basil: Build A System Instant-Like
Copyright (C) 2014 Catalyst IT Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from inspect import isclass
from utils import BasilVersionException, get_module
from sys import modules
from io import to_unicode


class BaseDatabaseManager(object):
    """A base manager class for configuring databases.

    A db_manager's docstring will be displayed at the beginning of the database
    configuration process, and when 'basil doc' is run for this db_manager.

    Each db_manager's docstring should contain a description of:
        - The kind of database that will be configured"""

    class Database(object):
        """Encapsulates data related to a database this db_manager manages."""

        def __init__(self, name):
            self.name = name

        def __unicode__(self):
            return to_unicode(self.name)

        def __str__(self):
            return str(unicode(self))

    class DatabaseUser(object):
        """Encapsulates data related to a database user this db_manager
        manages."""

        def __init__(self, name, password, granted_dbs):
            self.name = name
            self.password = password
            self.granted_dbs = granted_dbs

        def __unicode__(self):
            return to_unicode(self.name)

        def __str__(self):
            return str(unicode(self))

    @classmethod
    def get_version(cls):
        """Returns the version number of the module this db_manager class is
        defined in.

        The version number should be specified in the module's __version__
        The first digit should be the major version of Basil the db_manager is
        designed for;
        The second digit should be the major version of the db_manager for
        that version of Basil.

        E.g. 1.2.3 would be the 3rd minor version of the 2nd major version of
        the db_manager for basil 1.x.
        """
        return modules[cls.__module__].__version__

    @staticmethod
    def get_prereq_packages():
        """Should return a list of system packages to be installed before
        running database configuration."""
        return []

    @staticmethod
    def get_virtualenv_prereq_pip_packages():
        """Should return a list of pip packages to be installed in the
        virtualenvironment before running the database configuration."""
        return []

    def __init__(self):
        """Any database-related services should be started in here."""
        pass

    def create_database(self, db):
        """Should create a database on the local machine."""
        """db should be of type self.Database"""
        raise Exception('create_database() Should create a database on the '
                'local machine.')

    def delete_database(self, db):
        """Should delete a database on the local machine."""
        """db should be of type self.Database"""
        raise Exception('delete_database() should delete the database on the'
                'local machine.')

    def create_user(self, user):
        """Should create a database user on the local machine."""
        """user should be of type self.DatabaseUser"""
        raise Exception('create_user() should create a database user on the '
                'local machine with permissions to use the database.')

    def delete_user(self, user):
        """Should delete a database user on the local machine."""
        """user should be of type self.DatabaseUser"""
        raise Exception('delete_user() should delete a database user on the '
                'local machine.')

    def grant_permissions(self, db_name, user):
        """Should grant a user permissions to use a database."""
        """user should be of type self.DatabaseUser"""
        raise Exception('grant_permissions() should grant a user permissions '
                'to use a database.')


def get_db_manager_class(db_manager_name, major_version_number=None):
    """Factory to get a database manager class for a certain version of
    basil."""

    # Get the appropriate db_manager module.
    db_module = get_module('db_managers.' + db_manager_name,
            major_version_number)

    db_manager = None
    for c in db_module.__dict__.values():
        # Find the class that inherits from BaseDatabaseManager.
        if (isclass(c) and issubclass(c, BaseDatabaseManager) and
                c != BaseDatabaseManager):
            db_manager = c
            break
    if db_manager != None:
        return db_manager
    else:
        raise BasilVersionException("{} database manager class could not be "
                "found.".format(db_manager_name))


class DbManagerConfig(object):
    """Configuration management class for templates to specify their required
    database configuration."""

    def __init__(self, db_manager_name, major_version_number):
        self.db_manager_name = db_manager_name
        self.major_version_number = major_version_number
        self.db_manager_class = get_db_manager_class(db_manager_name,
                major_version_number)
        self.dbs = []
        self.users = []

    def add_db(self, *args, **kwargs):
        """Add a database to the db_manager configuration.
        Arguments will be the same as those for initializing a Database
        for this configuration's db_manager type"""
        self.dbs.append(self.db_manager_class.Database(*args, **kwargs))

    def add_user(self, *args, **kwargs):
        """Add a database user to the db_manager configuration.
        Arguments will be the same as those for initializing a DatabaseUser
        for this configuration's db_manager type"""
        self.users.append(self.db_manager_class.DatabaseUser(*args, **kwargs))
