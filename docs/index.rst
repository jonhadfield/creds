=====
creds
=====

A python library for user management.

Release v\ |version|.

Installation
------------

*Using pip package manager*::

    $ pip install creds

*From source*::

    $ git clone https://github.com/jonhadfield/creds
    $ cd creds
    $ python setup.py install

Example usage - adding a user
-----------------------------

*Import classes and functions*::

    from creds.users import User, Users
    from creds.plan import (create_plan, execute_plan)

*Discover existing users*::

    current_users = Users.from_passwd()

*Create a new user*::
    test_user = User(name='test')




|
|
|
|
|



API
---

.. toctree::
   :maxdepth: 3

   api/users
   api/plan
   api/ssh
   api/utils
