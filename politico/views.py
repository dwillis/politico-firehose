import StringIO
import datetime
import time
from google.appengine.api.labs import taskqueue
from politico.models import Story
from google.appengine.api.urlfetch import fetch
from toolbox import feedparser
from django.http import HttpResponse

feeds = ['http://feeds.politico.com/politico/rss/congress', 'http://www.politico.com/rss/life.xml', 'http://www.politico.com/rss/lobbyists.xml']

def fetch_feeds(request):
    for url in feeds:
        taskqueue.add(url = '/_update_feed/', params = {'url' : url}, method='GET')
    return HttpResponse('ok!')


def update_feed(request):
    url = request.GET['url']
    content = fetch(url).content
    d = feedparser.parse(StringIO.StringIO(content))
    for entry in d.entries:
        query = Story.all()
        story = query.filter('link =', entry.id).get()
        if not story:
            story = Story(link = entry.id, title = entry.title, byline = entry.author, updated_date = datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed)))
            story.put()
    return HttpResponse('ok!')

