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


from django.contrib import admin
from consonance.models import *


#class VanillaAdmin(admin.ModelAdmin):
#    pass
#admin.site.register(User, VanillaAdmin)
#admin.site.register(Service, VanillaAdmin)
#admin.site.register(Via, VanillaAdmin)
#admin.site.register(Room, VanillaAdmin)

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class LikeInline(admin.TabularInline):
    model = Like
    extra = 0

class MediaInline(admin.TabularInline):
    model = Media
    extra = 0
    
    
class EntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'published'
    inlines = [
        LikeInline,
        CommentInline,
        MediaInline,
    ]
    list_display = ['user', 'service', 'published', 'title']
    list_display_links = ['title',]
    list_filter = ['user', 'service', 'published']
    search_fields = ['title', ]
    
admin.site.register(Entry, EntryAdmin)


class EnclosureInline(admin.TabularInline):
    model = Enclosure
    extra = 0

class ThumbnailInline(admin.TabularInline):
    model = Thumbnail
    extra = 0    

class ContentInline(admin.TabularInline):
    model = Content
    extra = 0

class MediaAdmin(admin.ModelAdmin):
    inlines = [
        ContentInline,
        ThumbnailInline,
        EnclosureInline,
    ]
    list_display = ['title', 'entry', 'link',]
    list_display_links = ['title',]
    search_fields = ['title', 'entry', 'link',]
admin.site.register(Media, MediaAdmin)
