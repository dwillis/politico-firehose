# Feeds
from politico import get_feeds
from toolbox import feedparser
from google.appengine.api import taskqueue
from google.appengine.api.urlfetch import fetch
import StringIO

# Models
from google.appengine.ext import db
from politico.models import Story, Author, HourlyStats

# Etc.
import time
import logging
from datetime import datetime
from django.http import HttpResponse
from django.utils import simplejson
from django.template.defaultfilters import slugify


def get_key_or_none(request):
    """
    Gets the key param from the db, or returns None.
    """
    # Is the key is in the GET params?
    key = request.GET.get('key', None)
    if not key:
        return None
    # Is the key is valid?
    try:
        key = db.Key(key)
    except:
        return None
    # Is the key in the database?
    obj = db.get(key)
    if not obj:
        return None
    # If all of the above are yes...
    return obj


def fetch_feeds(request):
    """
    Loop through all of the feeds and schedule an update for each.
    """
    for feed in get_feeds():
        taskqueue.add(
            url = '/_update_feed/',
            params = {'url' : feed.get("feed_url")},
            method='GET'
        )
    return HttpResponse('ok!')


def update_feed(request):
    """
    Fetch a feed and sync each item with the database.
    """
    # Fetch the url
    url = request.GET['url']
    content = fetch(url).content
    d = feedparser.parse(StringIO.StringIO(content))
    # Loop through all the items
    for entry in d.entries:
        # See if this link already exists
        story_query = Story.all()
        story = story_query.filter('link =', entry.id).get()
        # And if it doesn't ...
        if not story:
            # Create a new Story object
            story = Story(
                link = entry.id,
                title = entry.title,
                updated_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed)), 
            )
            # Prep the authors
            authors = entry.author.split(',')
            author_keys = []
            # Loop through the authors
            for author in authors:
                # Check if the author already exists
                this_slug = str(slugify(author))
                if not this_slug:
                    continue
                a = Author.get_by_key_name(this_slug)
                # If it does...
                if a:
                    # Sync updates
                    if story.updated_date > a.last_updated:
                        a.last_updated = story.updated_date
                        a.put()
                # Otherwise...
                else:
                    # Create a new Author obj
                    a = Author(
                        key_name = this_slug,
                        name = author,
                        slug = this_slug,
                        story_count = 1,
                        last_updated = story.updated_date
                    )
                    a.put()
                # Add this to the Author key list
                author_keys.append(a.key())
            # Add the author keys to the story object
            story.bylines = author_keys
            # Save the story
            story.put()
            # Schedule total updates for all the authors
            [taskqueue.add(
                url = '/_update_story_count_for_author/',
                params = {'key' : i},
                method='GET'
            ) for i in author_keys]
    return HttpResponse('ok!')


def update_story_count_for_author(request):
    """
    Update the story count for an Author.
    
    Pass in the key of the object as a GET param.
    """
    obj = get_key_or_none(request)
    if not obj:
        raise Http404
    logging.debug("Updating story count for Author %s" % obj)
    obj.story_count = obj.get_story_count()
    obj.put()
    return HttpResponse('ok!')


def update_story_count_for_all_authors(request):
    """
    Updates the story count for all Authors.
    """
    logging.info("Updating story count for all Authors")
    [taskqueue.add(
        url = '/_update_story_count_for_author/',
        params = {'key' : i.key()},
        method='GET'
    ) for i in Author.all()]
    return HttpResponse('ok!')


def update_hourly_stats(request):
    """
    Group stories by hour and record the totals in the database.
    """
    qs = Story.all().order("-updated_date")
    data_dict = {}
    for obj in qs:
        this_hour = obj.updated_local().hour
        try:
            data_dict[this_hour] += 1
        except KeyError:
            data_dict[this_hour] = 1
    data_json = simplejson.dumps(data_dict)
    logging.info("Creating a new HourlyStats record")
    obj = HourlyStats(creation_datetime=datetime.now(), data=data_json)
    obj.put()
    return HttpResponse('ok!')

