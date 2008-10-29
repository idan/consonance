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

logger = logging.getLogger("Fetch")

def handle_exception(user, errortext):
    exc_type, exc_value = sys.exc_info()[:2]
    logger.exception('User "%s": %s: %s: "%s"' % 
    (user,
    errortext,
    exc_type.__name__,
    exc_value if exc_value else "no additional information"))

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
        if 'title' in rawmedia:
            mediaobj.title = rawmedia['title']
        if 'player' in rawmedia:
            mediaobj.player = rawmedia['player']
    mediaobj.save()
    
    for thumbnail in rawmedia['thumbnails']:
        thumbobj, thumbcreated = Thumbnail.objects.get_or_create(
            url=thumbnail['url'],
            width=thumbnail['width'],
            height=thumbnail['height'],
            media=mediaobj)
        thumbobj.save()
    
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
    

def process_entry(entry):
    logger.debug("Processing entry %s" % entry['id'])
    
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
        if entry['updated'] == entry_obj.updated:
            return
    
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
            

def fetch():
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
    for user in settings.CONSONANCE_USERS:
        try:
            raw = api.fetch_user_feed(user)
            #import pickle
            #pickle_file = open('ffdata.pickle', 'rb')
            #raw = pickle.load(pickle_file)
        except:
            handle_exception(user, "failed to fetch activity")
            continue
        finally:
            pickle_file.close()
        
        if not raw['entries']:
            logger.info('No activity available for user "%s".' % user)
            continue
        
        for entry in raw['entries']:
            try:
                process_entry(entry)
            except:
                handle_exception(user, "failed to process entry")
                continue
    
    logger.info('Fetch complete.')