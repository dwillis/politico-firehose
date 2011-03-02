# Feeds
from politico import get_feeds
from toolbox import feedparser
from google.appengine.api import taskqueue
from google.appengine.api.urlfetch import fetch
import StringIO

# Models
from politico.models import Story, Author, AuthorStory

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
            # Prep the authors
            authors = entry.author.split(',')
            if len(authors) > 1:
                multi_byline = True
            else:
                multi_byline = False
            # Create a new Story object
            story = Story(
                link = entry.id,
                title = entry.title,
                updated_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed)), 
                multi_byline = multi_byline
            )
            # Save it
            story.put()
            # Loop through the authors
            for author in authors:
                # Check if the author already exists
                a = author_query.filter('slug =', str(slugify(author))).get()
                # If it does...
                if a:
                    # Update the count
                    a.story_count += 1
                    # Synce updates
                    if story.updated_date > a.last_updated:
                        a.last_updated = story.updated_date
                        a.put()
                # Otherwise...
                else:
                    # Create a new Author obj
                    a = Author(
                        name = author,
                        slug = str(slugify(author)),
                        story_count = 1,
                        last_updated = story.updated_date
                    )
                    a.put()
                # Then always create an M2M link between the Author and the Story.
                AuthorStory(author=a, story=story).put()
    return HttpResponse('ok!')
