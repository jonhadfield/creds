.. image:: https://readthedocs.org/projects/creds/badge/?version=master
    :target: http://creds.readthedocs.io/en/master/?badge=master
    :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/jonhadfield/creds/badge.svg?branch=master
    :target: https://coveralls.io/github/jonhadfield/creds?branch=master
.. image:: https://travis-ci.org/jonhadfield/creds.svg?branch=master
    :target: https://travis-ci.org/jonhadfield/creds
.. image:: https://landscape.io/github/jonhadfield/creds/master/landscape.svg?style=flat
   :target: https://landscape.io/github/jonhadfield/creds/master
   :alt: Code Health

Creds
=====

Creds is a library that simplifies the management of user accounts and
their credentials on Linux, FreeBSD and OpenBSD.

Instead of issuing commands to create, update and delete users and their
ssh keys, supply Creds with details of the users you want and it will
take care of the implementation.

The supported inputs are currently YAML, JSON or python dictionaries.

User vs System accounts
-----------------------

| Linux has a default range of user ids to provide to system and user
  accounts, found in /etc/login.defs.
| Creds will attempt to read this file to determine which accounts are
  in scope for management and, if unavailable, will default to:

    | UID\_MIN = 1000 # User accounts will have an id of 1000 or more
    | UID\_MAX = 60000 # User accounts will not have an id higher than
      60000

Example Usage
-------------

Read a list of users from users.yml and create them (if missing) or
update (if existing):

::

    from creds.users import Users
    from creds.plan import (create_plan, execute_plan)

    existing_users = Users.from_passwd()  # Get a list of existing users and their keys
    proposed_users = Users.from_yaml('users.yml')  # Read the proposed list of users and their keys

    # Generate a list of operations to transition from current to existing
    plan = create_plan(existing_users=existing_users, proposed_users=proposed_users)
    execute_plan(plan=plan)  # Execute the plan

Deleting users


If your input defines all of the user accounts you want to exist, you
can choose to purge any that are undefined by adding a parameter to
create\_plan:

::

    plan = create_plan(existing_users=existing_users, proposed_users=proposed_users,
                       purge_undefined=True)

Protecting users


If there are users you want to protect from change, e.g. you want to
make sure that certain users are not deleted or updated under any
circumstances, then you can supply a list of usernames for Creds to
ignore:

::

    plan = create_plan(existing_users=existing_users, proposed_users=proposed_users,
                       purge_undefined=True, protected_users=['rod', 'jane', 'freddy'])

