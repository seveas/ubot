Contributing to µbot
====================

µbot is a young and active project that welcomes contributions from everyone in
any useful form. The code can be found on GitHub_, where it is also easy to
collaborate on fixes, new features and extra helpers.

Here are some additional tips for making contributing to µbot a pleasant
experience.

.. _GitHub: http://github.com/seveas/ubot

Bug reports
-----------
If you find a bug in µbot, please report it so it can be fixed. Issues can be
reported in the `GitHub issue tracker <https://github.com/seveas/ubot/issues>`_.

Bug fixes and new features
--------------------------
If you have fixed or improved µbot in any way, please share your contribution.
There are a few hard rules and a few guidleines to follow though, before your
contribution can be accepted.

Let's do the hard rules first:

* Any and all contributions should be licensed under the same terms as µbot
  itself: the GNU general public license, version 3 or later. 
* Copyright assignment is not required, you will still own all rights to the
  contributions you make.
* New helpers should be complete, that is: including a config file and all
  relevant data files. All these files need to be available under the same GNU
  GPL license.
* Any user interface or API change must be documented.

And the guidelines:

* You should follow the code style of the existing code, which is mostly PEP 8.
  I am picky about whitespace and will fix up commits that I think are ugly.
* If you think your change is significant, append your name and e-mail address 
  to the list of authors in doc/copying.rst.
* Patches are preferably submitted as github pull requests, but any other way
  will do.

Making a release
----------------
.. note:: This section is mainly meant for myself -- Dennis
To make a release, you will need to do some administrative tasks:

* Bump the version number in configure.ac and doc/conf.py
* Bump the version number in doc/Makefile.am
* Commit, tag and push to github
* ./autogen.sh
* make dist; make -C doc html
* Upload tarballs and documentation
