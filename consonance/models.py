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


from django.db import models
from django.template.loader import render_to_string


class User(models.Model):
    """A FriendFeed User."""
    uuid = models.CharField(blank=False, null=False, unique=True, max_length=36)
    name = models.CharField(blank=True, max_length=80)
    nickname = models.CharField(blank=True, max_length=80)
    profileurl = models.URLField(blank=True, verify_exists=False, max_length=255)
    
    class Meta:
        ordering = ["name"]
        verbose_name, verbose_name_plural = "user", "users"
    
    def __unicode__(self):
        return self.name or self.nickname or self.id


class Service(models.Model):
    """A FriendFeed Service."""
    uuid = models.CharField(blank=False, null=False, unique=True, max_length=36)
    name = models.CharField(blank=True, max_length=80)
    iconurl = models.URLField(blank=True, verify_exists=False, max_length=255)
    profileurl = models.URLField(blank=True, verify_exists=False, max_length=255)
    
    class Meta:
        ordering = ["name"]
        verbose_name, verbose_name_plural = "service", "services"
    
    def __unicode__(self):
        return self.name


class Via(models.Model):
    """A FriendFeed Via, represents a 3rd party API client to FriendFeed"""
    name = models.CharField(blank=False, max_length=80)
    url = models.URLField(blank=True, verify_exists=False, max_length=255)
    
    class Meta:
        ordering = ["name"]
        verbose_name, verbose_name_plural = "via", "vias"
    
    def __unicode__(self):
        return self.name


class Room(models.Model):
    """A FriendFeed Room"""
    uuid = models.CharField(blank=False, null=False, unique=True, max_length=36)
    name = models.CharField(blank=True, max_length=80)
    nickname = models.CharField(blank=True, max_length=80)
    url = models.URLField(blank=True, verify_exists=False, max_length=255)
    
    class Meta:
        ordering = ["name"]
        verbose_name, verbose_name_plural = "room", "rooms"
    
    def __unicode__(self):
        return self.name


class Entry(models.Model):
    """Represents a single friendfeed activity entry."""
    uuid = models.CharField(blank=False, null=False, unique=True, max_length=36)
    title = models.CharField(blank=True, max_length=255)
    link = models.URLField(blank=True, verify_exists=False, max_length=255)
    published = models.DateTimeField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    hidden = models.BooleanField(default=False)
    anonymous = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name="entries")
    service = models.ForeignKey(Service, related_name="entries")
    via = models.ForeignKey(Via, blank=True, null=True, related_name="entries")
    room = models.ForeignKey(Room, blank=True, null=True, related_name="entries")
    
    class Meta:
        ordering = ["-published"]
        verbose_name, verbose_name_plural = "entry", "entries"
    
    def __unicode__(self):
        return self.title or self.id
    
    def get_rendered_html(self):
        pass


class Like(models.Model):
    """A FriendFeed 'Like'."""
    date = models.DateTimeField(blank=False, null=False)
    user = models.ForeignKey(User, related_name="likes")
    entry = models.ForeignKey(Entry, related_name="likes")
    
    class Meta:
        ordering = ["-date"]
        verbose_name, verbose_name_plural = "like", "likes"
    
    def __unicode__(self):
        return u"Like"


class Comment(models.Model):
    """A FriendFeed comment."""
    uuid = models.CharField(blank=False, null=False, unique=True, max_length=36)
    date = models.DateTimeField(blank=True, null=True)
    body = models.TextField(blank=True)
    user = models.ForeignKey(User, related_name="comments")
    entry = models.ForeignKey(Entry, related_name="comments")
    
    class Meta:
        ordering = ["-date"]
        verbose_name, verbose_name_plural = "comment", "comments"
    
    def __unicode__(self):
        return u"%s: %s" % (self.entry, self.id)


class Media(models.Model):
    """A FriendFeed media item"""
    title = models.CharField(blank=True, max_length=255)
    player = models.URLField(blank=True, null=True, verify_exists=False, max_length=255)
    link = models.URLField(blank=False, verify_exists=False, max_length=255)
    entry = models.ForeignKey(Entry, related_name="medias")
    
    class Meta:
        ordering = ["title", "link"]
        verbose_name, verbose_name_plural = "media", "medias"
    
    def __unicode__(self):
        return self.title or self.link


class Thumbnail(models.Model):
    """A FriendFeed Thumbnail."""
    url = models.URLField(blank=False, verify_exists=False, max_length=255)
    width = models.IntegerField(blank=False, null=False)
    height = models.IntegerField(blank=False, null=False)
    media = models.ForeignKey(Media, related_name="thumbnails")
    
    class Meta:
        ordering = ["url"]
        verbose_name, verbose_name_plural = "thumbnail", "thumbnails"
    
    def __unicode__(self):
        return self.url


class Content(models.Model):
    """A FriendFeed content link, referenced by a Media item."""
    url = models.URLField(blank=False, verify_exists=False, max_length=255)
    mimetype = models.CharField(blank=True, max_length=80)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    media = models.ForeignKey(Media, related_name="contents")
    
    class Meta:
        ordering = ["url"]
        verbose_name, verbose_name_plural = "content", "contents"
    
    def __unicode__(self):
        return self.url


class Enclosure(models.Model):
    """A FriendFeed media enclosure, referenced by a Media item."""
    url = models.URLField(blank=False, verify_exists=False, max_length=255)
    mimetype = models.CharField(blank=True, max_length=80)
    length = models.CharField(blank=True, max_length=80) # TODO: Have no idea about the datatype here.
    media = models.ForeignKey(Media, related_name="enclosures")
    
    class Meta:
        ordering = ["url"]
        verbose_name, verbose_name_plural = "enclosure", "enclosures"
    
    def __unicode__(self):
        return self.url

