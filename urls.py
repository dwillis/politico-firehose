# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Views
from politico.views import update_feed, fetch_feeds, index

# Feeds
from politico.feeds import LatestItems
from django.contrib.syndication.views import feed

# Urls
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Homepage
    url('^$', index),
    # RSSy Feeds
    url(r'^feeds/(?P<url>.*)/$', feed,
        {'feed_dict': dict(latest=LatestItems) },
        name='feeds'),
    # Tasks
    url('^_update_feed/$', update_feed),
    url('^_update_all_feeds/$', fetch_feeds),
)
