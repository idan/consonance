====================
Consonance Changelog
====================

0.2
===

Backwards-incompatible changes
------------------------------

Added entry filtering to consonance, which changes the format of
settings.CONSONANCE_USERS. Where previously it was simply a list of usernames to fetch::
    
    CONSONANCE_USERS = [
        'user1',
        'user2',
    ]

Now it is a dictionary which includes values to exclude from fetching from FriendFeed::

    CONSONANCE_USERS = {
        'user1' : {
            "path.to.value" : ["list", "of", "patterns", "to", "exclude"],
        }
    }
