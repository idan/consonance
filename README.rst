==========
Consonance
==========

-----------------------------------------------------
A django app for consuming public friendfeed streams
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

* Homepage: http://github.com/idangazit/consonance/wiki
* Source: http://github.com/idangazit/consonance
* Issuetracker: http://http://pixane.lighthouseapp.com/projects/18943-consonance/

.. _github: http://www.github.com
.. _lighthouse: http://www.lighthouseapp.com/

History
=======

Originally I wanted an easy way to build a "lifestream" application in Django. Naturally, I took the long and stupid route. Originally starting with FriendFeed, I eventually decided (for reasons I can't recall now) that I should Build My Own, and boldly created Djangregator_, which abandoned FriendFeed and embraced a pluggable-backend model, with one backend for each of the supported online services. I wrote three such backends (Twitter, Flickr, Delicious).

Since the ultimate goal of Djangregator was to provide a lifestream for a blog, I started looking at oembed_ support, and `django-oembed`_, so users could easily embed media instead of just a link to some media. Then I got to thinking about "batching" -- what happens when you upload 52 images to Flickr? Should there be 52 separate entries that the user needs to deal with at display-time?

It turns out that FriendFeed already:
 * Does all of this for you
 * Does it for a heckuva lot more services than the three I cobbled together
 * And probably does it in a more robust, bug-free fashion given their userbase
 * Probably doesn't need to worry about API rate-limiting as it's a big-name consumer
 * Hands me the kind of embeddable media info I would have to use oembed for...
 * ... but also gives it to me for services that don't support oembed (I'm lookin' at you, YouTube)
 * Deals with batching!
 * Deals with service-specific date and time parsing (WTF? Can't everybody just agree on ISO8601?)
 * For that matter, gives all datetimes normalized to UTC
 * Makes tea and fetches your slippers
 
In retrospect, Djangregator_ was a good learning experience. I'm glad I came full-circle, though. Thank you FriendFeed!

.. _Djangregator: http://github.com/idangazit/djangregator/
.. _oembed: http://oembed.com/
.. _`django-oembed`: http://code.google.com/p/django-oembed/