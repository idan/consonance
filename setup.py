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


import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "consonance",
    version = "0.1.3",
    packages = find_packages(),
    author = "Idan Gazit",
    author_email = "idan@pixane.net",
    description = "A django app for consuming public FriendFeed streams.",
    long_description = """
    FriendFeed_ is a fantastic service which does all of the hard work in
    aggregating and "normalizing" (for lack of a better description) all of
    the online activity we generate on socal sites like Flickr, YouTube, et
    al.

    *Consonance* is merely a set of django models which mirrors the structure
    set forth in the `FriendFeed API Documentation`_ and a convenient
    cron-callable script for fetching updates from FriendFeed. It should be
    useful for integrating a lifestream into a django-powered site, but the
    display and styling of the lifestream is left up to the user -- there are
    no views or templates included.
    
    .. _FriendFeed: http://www.friendfeed.com
    .. _FriendFeed API Documentation: http://code.google.com/p/friendfeed-api/wiki/ApiDocumentation
    """,
    url = "http://github.com/idangazit/consonance/",
    license = "BSD",
    classifiers = [
        "Framework :: Django",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    #package_data = {"": ["*.rst", "*.html", "*.txt", "ez_setup.py"]},
    scripts = ["consonance_fetch.py"],
    include_package_data = True,
    )