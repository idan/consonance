==========
Consonance
==========

-----------------------------------------------------
A django app for consuming public FriendFeed streams
-----------------------------------------------------


About
=====

FriendFeed_ is a fantastic service which does all of the hard work in aggregating and "normalizing" (for lack of a better description) all of the online activity we generate on socal sites like Flickr, YouTube, et al.

*Consonance* is merely a set of django models which mirrors the structure set forth in the `FriendFeed API Documentation`_ and a convenient cron-callable script for fetching updates from FriendFeed. I imagine that it will be most useful in presenting a lifestream to readers of your blog or similar. How you display the content is up to you -- there are no views or templates included with this application.

.. _FriendFeed: http://www.friendfeed.com
.. _FriendFeed API Documentation: http://code.google.com/p/friendfeed-api/wiki/ApiDocumentation

License & How to Contribute
===========================

Sad that these two subjects rarely go together in a README. They should.

Consonance is yours to use, modify, and redistribute according to the terms of the BSD license, the full text of which is in a file named ``LICENSE.txt``, which should be in the same directory as this readme.

Consonance is hosted on github_, with issuetracking supplied by the equally-lovely lighthouse_. It is ridiculously easy to contribute code, and it is ridiculously easy to fork off your own branch.

* Homepage & Source: http://github.com/idangazit/consonance
* Issuetracker: http://pixane.lighthouseapp.com/projects/18943-consonance

.. _github: http://www.github.com
.. _lighthouse: http://www.lighthouseapp.com/

Usage
=====

Requirements
------------

Consonance requires:

* Django 1.0
* Python 2.5
* `friendfeed-api`_

.. _`friendfeed-api`: http://code.google.com/p/friendfeed-api

It might work with python < 2.5 but I haven't tested and don't intend to. If some kind soul verifies that it works on older python versions I'll note it here, but I don't plan on spending time supporting such a configuration.

Getting Consonance
------------------

**Using easy_install**: run ``easy_install consonance`` from your favorite shell. The latest version of consonance will be fetched and installed from PyPI_. If you don't already have easy_install_, go get it.

.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _PyPI: http://pypi.python.org/pypi/consonance

**Note**: the version of easy_install used to create the installer is 0.6c9. Sadly, python on the mac (leopard) comes bundled with 0.6c7 and this causes installation to fail even if you have a newer setuptools in your site_packages. Some googling has yielded this information_, but the short solution is to open your favorite terminal and upgrade the built-in easy_install script as follows::

    sudo easy_install -s /usr/bin setuptools

.. _information: http://andreasjacobsen.com/2008/10/10/using-python-setuptools-on-the-mac/

**From source**: get yourself a copy of consonance from the homepage_. If you're comfortable with git, then clone yourself a copy. If you just want a tarball, click on the "download" button near the top of the page, download a .zip or tarball, and unpack it somewhere convenient. Either way, you should end up with a directory looking something like this::

    consonance
    |- LICENSE.txt
    |- README.rst
    |- README.html
    |- consonance_fetch.py
    |- setup.py
    |- ez_setup.py
    |- consonance
       |- __init__.py
       |- admin.py
       |- fetch.py
       |- models.py
       |- views.py

.. _homepage: http://github.com/idangazit/consonance

Put the inner ``consonance`` directory somewhere on your python path. You can copy it to your django directory, to your site-packages directory. You can also just run ``python setup.py install``.

You will also need to make use of the ``consonance_fetch.py`` script to fetch updates, so put that somewhere on your ``$PATH``.


Using Consonance
================

Make sure to add consonance to the ``INSTALLED_APPS`` list in ``settings.py``.

Consonance will look for a list or tuple of friendfeed usernames called ``CONSONANCE_USERS`` in your project's ``settings.py``::
    
    CONSONANCE_USERS = (
        'joe_user',
        'jane_user',
    )

Make sure to add at least one name to ``CONSONANCE_USERS``.

Consonance *does not* perform fetches automatically. You've got to do it yourself, using a script called ``consonance_fetch.py``. If you installed consonance using easy_install, then it should be present on your path. You can invoke the script as follows::
    
    consonance_fetch.py --projectpath="/path/to/my/django/project"

The ``projectpath`` argument should contain the path to your django project, which is usually wherever your project's ``settings.py`` resides.

Every time the script is run, it fetches the new updates for each of the users specified in the ``CONSONANCE_USERS``. You'll probably want to run this script periodically via a cron job or similar.

**Be nice to FriendFeed's servers. You probably don't generate new content more than once every ten minutes. If you call consonance_fetch.py too often, eventually FriendFeed's API will throttle/ignore you.**

If you want to see more about what ``consonance_fetch.py`` can do, run it as follows::
    
    consonance_fetch.py --help
    

History
=======

Originally I wanted an easy way to build a "lifestream" application in Django. Naturally, I took the long and stupid route. Originally starting with FriendFeed, I eventually decided (for reasons I can't recall now) that I should Build My Own, and boldly created Djangregator_, which abandoned FriendFeed and embraced a pluggable-backend model, with one backend for each of the supported online services. I wrote three such backends (Twitter, Flickr, Delicious).

Since the ultimate goal of Djangregator was to provide a lifestream for a blog, I started looking at oembed_ support, and `django-oembed`_, so users could easily embed media instead of just a link to some media. Then I got to thinking about "batching" -- what happens when you upload 52 images to Flickr? Should there be 52 separate entries that the user needs to deal with at display-time?

It turns out that FriendFeed already:
 * Does all of this for you
 * Does it for a heckuva lot more services than the three I cobbled together
 * And probably does it in a more robust, bug-free fashion given their userbase
 * Probably doesn't need to worry about API rate-limiting as it's a big-name consumer
 * Deals with batching!
 * Deals with service-specific date and time parsing (WTF? Can't everybody just agree on ISO8601?)
 * For that matter, gives all datetimes normalized to UTC
 * Makes tea and fetches your slippers
 
**Update: Sadly it seems that "enclosures" doesn't contain the embed HTML. Looking into doing it with django-oembed, but that seems to be broken too.**
 
In retrospect, Djangregator_ was a good learning experience. I'm glad I came full-circle, though. Thank you FriendFeed!

.. _Djangregator: http://github.com/idangazit/djangregator/
.. _oembed: http://oembed.com/
.. _`django-oembed`: http://code.google.com/p/django-oembed/

Naming
------

Going with the jazz themes of Django, and the fact that FriendFeed shines at pulling together the disparate elements of your online life:

**CONSONANCE** | *noun*

agreement or compatibility between opinions or actions: *consonance between conservation measures and existing agricultural practice.*
 * the recurrence of similar sounds, esp. consonants, in close proximity (chiefly as used in prosody).
 * *Music* the combination of notes that are in harmony with each other due to the relationship between their frequencies.