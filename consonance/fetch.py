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

def process_entry(entry):
    logger.debug("Processing entry %s" % entry['id'])
    obj, created = Entry.objects.get_or_create(id=entry['id'])
    
    # skip if already exists and not updated
    if not created:
        if entry['updated'] == obj.updated:
            return
    
    # basic fields
    obj.title = entry['title']
    obj.link = entry['link']
    obj.published = entry['published']
    obj.updated = entry['updated']
    obj.hidden = entry['hidden']
    obj.anonymous = entry['anonymous']
    
    # fk user field
    obj.user = process_user(entry['user'])
    
    # fk service field
    service, servicecreated = Service.objects.get_or_create(
        id=entry['service']['id'])
    if servicecreated:
        service.name = entry['service']['name']
        service.iconurl = entry['service']['iconUrl']
        service.profileurl = entry['service']['profileUrl']
        service.save()
    obj.service = service
    
    # fk via field, if present
    if entry['via']:
        via, viacreated = Via.objects.get_or_create(name=entry['via']['name'])
        if viacreated:
            via.url = entry['via']['url']
            via.save()
        obj.via = via
    
    # fk room field, if present
    if entry['room']:
        room, roomcreated = Room.objects.get_or_create(id=entry['room']['id'])
        if roomcreated:
            room.name = entry['room']['name']
            room.nickname = entry['room']['nickname']
            room.url = entry['room']['url']
            room.save()
        obj.room = room
    
    obj.save()
    
    # comments
    for comment in entry['comments']:
        comment, commentcreated = Comment.objects.get_or_create(
            id=comment['id'])
        if commentcreated:
            comment.date = comment['date']
            comment.body = comment['body']
            comment.user = process_user(comment['user'])
            comment.entry = obj
            comment.save()
    
    # likes
    for like in entry['likes']:
        likeuser = process_user(like['user'])
        like, likecreated = Like.objects.get_or_create(
            date=like['date'],
            user=likeuser)
        like.entry = obj
        like.save()
        

def fetch():
    logger = logging.getLogger("Fetch")
    if not settings.CONSONANCE_USERS:
        logger.error("No users: settings.CONSONANCE_USERS is undefined or empty.")
        raise ImproperlyConfigured()
    
    logger.info("Commencing fetch for %n users." % 
                settings.CONSONANCE_USERS.__len__())
    
    api = friendfeed.FriendFeed()
    for user in settings.CONSONANCE_USERS:
        try:
            raw = api.fetch_user_feed(user)
        except:
            handle_exception(user, "failed to fetch activity")
            continue
        
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