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
from politico import views
from politico import tasks

# Feeds
from politico import feeds
from django.contrib.syndication.views import feed as feed_view

# Urls
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Homepage
    url('^$', views.index, name="index"),
    
    # Bylines
    url('^bylines/scoreboard/$', views.byline_scoreboard,
        name="bylines-scoreboard"),
    url('^bylines/(?P<slug>.*)/$', views.byline_detail),
    
    # RSSy Feeds
    url('^feeds/list/$', views.feed_list, name="feeds-list"),
    url(r'^feeds/(?P<url>.*)/$', feed_view,
        {'feed_dict': {
            'latest': feeds.LatestStories,
            'author': feeds.AuthorFeeds,
        }},
        name='feeds'),
    
    # Tasks
    url('^_update_feed/$', tasks.update_feed),
    url('^_update_all_feeds/$', tasks.fetch_feeds),
    url('^_update_all_feeds/$', tasks.fetch_feeds),
    url('^_update_story_count_for_author/$', tasks.update_story_count_for_author),
    url('^_update_story_count_for_all_authors/$', 
        tasks.update_story_count_for_all_authors),
)
