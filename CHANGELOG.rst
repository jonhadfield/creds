==========
Change Log
==========

This lists the changes made with each release.

`1.0.14`_ (2017-01-27)
----------------------

* Validate sudoers update using visudo to prevent corruption.


`1.0.13`_ (2017-01-13)
----------------------

* Add 'manage_home' parameter to plan. Setting it to True (default), means necessary changes to the home directory are applied. Note: If set to False, keys will not be managed.
* Add 'manage_keys' parameter to plan. Setting it to True (default), means necessary changes to a user's keys are applied.

