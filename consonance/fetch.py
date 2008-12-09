# Copyright (c) 2008, Idan Gazit
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#     * Neither the name of the author nor the names of other
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from consonance.models import *
import logging
import sys
import re

logger = logging.getLogger("Fetch")

def get_generic_exc_info(exc_type, exc_value):
    return '%s: "%s"' % (
        exc_type.__name__,
        exc_value if exc_value else "no additional information",
    )

def handle_exception(user, errortext):
    exc_type, exc_value = sys.exc_info()[:2]
    logger.exception('User "%s": %s: %s' % (
        user,
        errortext,
        get_generic_exc_info(exc_type, exc_value)
    ))

def process_user(rawuser):
    user, usercreated = User.objects.get_or_create(id=rawuser['id'])
    if usercreated:
        user.name = rawuser['name']
        user.nickname = rawuser['nickname']
        user.profileurl = rawuser['profileUrl']
        user.save()
    return user

def process_media(entry, rawmedia):
    logger.debug("Processing media %s" % rawmedia['link'])
    mediaobj, mediacreated = Media.objects.get_or_create(
        link=rawmedia['link'],
        entry=entry)
    if mediacreated:
        if 'title' in rawmedia and rawmedia['title'] is not None:
            mediaobj.title = rawmedia['title']
        if 'player' in rawmedia and rawmedia['player'] is not None:
            mediaobj.player = rawmedia['player']
    mediaobj.save()
    
    if 'thumbnails' in rawmedia and rawmedia['thumbnails'] is not None:
        for thumbnail in rawmedia['thumbnails']:
            thumbobj, thumbcreated = Thumbnail.objects.get_or_create(
                url=thumbnail['url'],
                width=thumbnail['width'],
                height=thumbnail['height'],
                media=mediaobj)
            thumbobj.save()

    if 'content' in rawmedia and rawmedia['content'] is not None:
        for content in rawmedia['content']:
            logger.debug(content)
            contentobj, contentcreated = Content.objects.get_or_create(
                url=content['url'],
                media=mediaobj)
            if contentcreated:
                contentobj.mimetype = content['type']
                contentobj.width = content['width']
                contentobj.height = content['height']
            contentobj.save()
    
    if 'enclosures' in rawmedia and rawmedia['enclosures'] is not None:
        for enclosure in rawmedia['enclosures']:
            enclosureobj, enclosurecreated = Enclosure.objects.get_or_create(
                url=enclosure['url'],
                media=mediaobj)
            if enclosurecreated:
                enclosureobj.mimetype = enclosure['type']
                enclosureobj.length = enclosure['length']
            enclosureobj.save()
    
    return mediaobj
    
def dict_pathsearch(dict, path):
    """
    Finds a value inside a dictionary of dictionaries given a path-like string
    of keys separated by periods. Raises KeyError if the requested path
    doesn't exist.
    
    Example
    -------
    
    Given a dictionary like the following:
    
    {
        foo : "foo"
        bar : "bar"
        baz : {
            bling: "bling"
            spam: {
                eggs: "eggs"
                ham: "ham"
            }
        } 
    }
    
    and a path like:
    
    dict_pathsearch(dict, "baz.spam.ham") returns "ham"
    dict_pathsearch(dict, "foo") returns "foo"
    dict_pathsearch(dict, "baz.bling") returns "bling"
    dict_pathsearch(dict, "python") raises KeyError
    """
    pathchunks = path.split('.')
    current = dict
    for chunk in pathchunks:
        if chunk in current:
            current = current[chunk]
        else:
            raise KeyError
    return current

def process_entry(entry, userdict={}):
    """
    Process a single raw FriendFeed entry. Returns True if the entry was
    processed, False if the entry was skipped due to filtering rules.
    
    process_entry takes two arguments: a raw entry dict, and a "userdict",
    which is a dictionary of friendfeed-user-specific settings which is defined
    in CONSONANCE_USERS (in the project settings).
    
    Currently the main use of the userdict is to allow filtering of the
    FriendFeed entries. See the Consonance README for a detailed explanation
    of the required format of CONSONANCE_USERS.
    """
    
    logger.debug("Processing entry %s" % entry['id'])
    
    # skip entry if there's a matching exclusion rule
    for rule in userdict.keys():
        try:
            # Find the value referenced by the rule
            value = dict_pathsearch(entry, rule)
        except KeyError:
            logger.debug("Exclusion rule \"%s\" references nonexistant path. Continuing..." % rule)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            logger.debug("Unable to process exclusion rule: %s. Continuing..." %
                get_generic_exc_info(exc_type, exc_value))
        else:
            for pattern in userdict[rule]:
                try:
                    if re.match(pattern.__str__(), value.__str__()) is not None:
                        # rule matched, skip this entry, return
                        logger.debug("Exclusion rule \"%s : %s\" matched, skipping!" % (rule, pattern))
                        return False
                except:
                    exc_type, exc_value = sys.exc_info()[:2]
                    logger.debug("Exclusion rule found but could not be processed: %s. Continuing..." % (
                        get_generic_exc_info(exc_type, exc_value)))
        
    
    # fk user field
    user = process_user(entry['user'])
    
    # fk service field
    service, servicecreated = Service.objects.get_or_create(
        id=entry['service']['id'])
    if servicecreated:
        service.name = entry['service']['name']
        service.iconurl = entry['service']['iconUrl']
        service.profileurl = entry['service']['profileUrl']
        service.save()
    
    entryobj, created = Entry.objects.get_or_create(
        id=entry['id'],
        user=user,
        service=service)
    
    # skip if already exists and not updated
    if not created:
        if entry['updated'] == entryobj.updated:
            logger.debug('Entry already cached, no new updates.')
            return True
    
    # basic fields
    entryobj.title = entry['title']
    entryobj.link = entry['link']
    entryobj.published = entry['published']
    entryobj.updated = entry['updated']
    entryobj.hidden = entry['hidden']
    entryobj.anonymous = entry['anonymous']
    
    # fk via field, if present
    if 'via' in entry:
        via, viacreated = Via.objects.get_or_create(name=entry['via']['name'])
        if viacreated:
            via.url = entry['via']['url']
            via.save()
        entryobj.via = via
    
    # fk room field, if present
    if 'room' in entry:
        room, roomcreated = Room.objects.get_or_create(id=entry['room']['id'])
        if roomcreated:
            room.name = entry['room']['name']
            room.nickname = entry['room']['nickname']
            room.url = entry['room']['url']
            room.save()
        entryobj.room = room
    
    entryobj.save()
    
    # comments
    for comment in entry['comments']:
        commentuser = process_user(comment['user'])
        commentobj, commentcreated = Comment.objects.get_or_create(
            id=comment['id'],
            user=commentuser,
            entry=entryobj)
        if commentcreated:
            commentobj.date = comment['date']
            commentobj.body = comment['body']
            commentobj.save()
    
    # likes
    for like in entry['likes']:
        likeuser = process_user(like['user'])
        like, likecreated = Like.objects.get_or_create(
            date=like['date'],
            user=likeuser,
            entry=entryobj)
        like.save()
    
    # media
    for media in entry['media']:
        process_media(entryobj, media)
    
    return True

def fetch(load_picklepath=None, save_picklepath=None):
    try:
        import friendfeed
    except ImportError:
        logger.error("Aborting fetch: unable to import friendfeed api.")
        return
    
    if not hasattr(settings, 'CONSONANCE_USERS'):
        logger.error("Aborting fetch: settings.CONSONANCE_USERS is undefined or empty.")
        return
    
    logger.info("Commencing fetch for %s users." % 
                settings.CONSONANCE_USERS.__len__())
    
    api = friendfeed.FriendFeed()
    
    if (settings.CONSONANCE_USERS.__len__() > 1) and (load_picklepath or save_picklepath):
        logger.critical("The mock/pickle data functionality cannot work with multiple users in CONSONANCE_USERS. Aborting...")
        return
        
    for user in settings.CONSONANCE_USERS.keys():
        
        if load_picklepath:
            logger.debug("Attempting to use pickle data file at %s" % load_picklepath)
            try:
                import pickle
                load_picklefile = open(load_picklepath, 'rb')
                raw = pickle.load(load_picklefile)
            except:
                handle_exception(user, "attempted to use pickled data but failed.")
                continue
            else:
                logger.info("Using pickled data from file, not accessing FriendFeed!")
            finally:
                load_picklefile.close()
        else:
            try:
                raw = api.fetch_user_feed(user)
            except:
                handle_exception(user, "failed to fetch activity")
                continue
        
        if not raw['entries']:
            logger.info('No activity available for user "%s".' % user)
            continue
        
        if save_picklepath:
            try:
                import pickle
                save_picklefile = open(save_picklepath, 'wb')
                pickle.dump(raw, save_picklefile)
            except:
                handle_exception(user, "failed to save pickle data")
                continue
            else:
                logger.info("Successfully saved FriendFeed activity to pickle file %s" % save_picklepath)
            finally:
                save_picklefile.close()
        
        processed_ok = 0
        processed_skip = 0
        processed_fail = 0
        
        for entry in raw['entries']:
            try:
                if process_entry(entry, settings.CONSONANCE_USERS[user]):
                    processed_ok += 1
                else:
                    processed_skip += 1
            except:
                handle_exception(user, "failed to process entry")
                processed_fail += 1
                continue
    
    logger.info('Fetch complete. Processed %i OK / %i Skipped / %i Failed.' % (
        processed_ok, processed_skip, processed_fail
    ))