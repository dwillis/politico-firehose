# Feeds
from politico import get_feeds
from toolbox import feedparser
from google.appengine.api import taskqueue
from google.appengine.api.urlfetch import fetch
import StringIO

# Models
from politico.models import Story, Author

# Etc.
import time
from datetime import datetime
from django.http import HttpResponse
from django.template.defaultfilters import slugify


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
    # Ready the db query object
    story_query = Story.all()
    author_query = Author.all()
    # Loop through all the items
    for entry in d.entries:
        # See if this link already exists
        story = story_query.filter('link =', entry.id).get()
        # And if it doesn't ...
        if not story:
            # Create a new Story object
            story = Story(
                link = entry.id,
                title = entry.title,
                updated_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed)), 
            )
            # Save it
            story.put()
            # Prep the authors
            authors = entry.author.split(',')
            author_keys = []
            # Loop through the authors
            for author in authors:
                # Check if the author already exists
                this_slug = str(slugify(author))
                a = Author.get_by_key_name(this_slug)
                # If it does...
                if a:
                    # Synce updates
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
            story.put()
    return HttpResponse('ok!')
