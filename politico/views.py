import StringIO
import datetime
import time
from google.appengine.api.labs import taskqueue
from politico.models import Story, Author
from google.appengine.api.urlfetch import fetch
from toolbox import feedparser
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify

feeds = ['http://feeds.politico.com/politico/rss/congress', 'http://www.politico.com/rss/life.xml', 'http://www.politico.com/rss/lobbyists.xml',
'http://www.politico.com/rss/pitboss.xml', 'http://www.politico.com/rss/politics.xml', 'http://www.politico.com/rss/2012-election.xml', 
'http://www.politico.com/rss/2012-election-blog.xml', 'http://feeds.politico.com/politico/rss/click', 'http://www.politico.com/rss/rogersimon.xml',
'http://www.politico.com/rss/suitetalk.xml', 'http://www.politico.com/rss/playbook.xml', 'http://www.politico.com/rss/morningscore.xml', 
'http://www.politico.com/rss/morningmoney.xml', 'http://www.politico.com/rss/politicopulse.xml', 'http://www.politico.com/rss/huddle.xml', 
'http://www.politico.com/rss/morningenergy.xml', 'http://www.politico.com/rss/morningdefense.xml', 'http://www.politico.com/rss/morningtech.xml',
'http://www.politico.com/rss/politicopicks.xml', 'http://www.politico.com/rss/Top10Blogs.xml', 'http://www.politico.com/rss/bensmith.xml',
'http://www.politico.com/rss/davidcatanese.xml', 'http://www.politico.com/rss/laurarozen.xml', 'http://www.politico.com/rss/glennthrush.xml', 
'http://www.politico.com/rss/onmedia.xml', 'http://www.politico.com/rss/joshgerstein.xml', 'http://www.politico.com/rss/maggiehaberman.xml', 
'http://www.politico.com/rss/Politico44box.xml', 'http://www.politico.com/rss/livepulse.xml']

def index(request):
    return HttpResponse("nothing to see here. yet.")


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
            author_query = Author.all()
            author = author_query.filter('name = ', entry.author).get()
            if author:
                author.story_count += 1
                if story.updated_date > author.last_updated:
                    author.last_updated = story.updated_date
                author.save
            else:
                author = Author(name = entry.author, slug = str(slugify(entry.author)), story_count = 1, last_updated = story.updated_date)
                author.put()
    return HttpResponse('ok!')

