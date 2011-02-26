import StringIO
import datetime
import time
from google.appengine.api.labs import taskqueue
from politico.models import Story
from google.appengine.api.urlfetch import fetch
from toolbox import feedparser
from django.http import HttpResponse

feeds = ['http://feeds.politico.com/politico/rss/congress', 'http://www.politico.com/rss/life.xml', 'http://www.politico.com/rss/lobbyists.xml',
'http://www.politico.com/rss/pitboss.xml', 'http://www.politico.com/rss/politics.xml', 'http://www.politico.com/rss/2012-election.xml', 
'http://www.politico.com/rss/2012-election-blog.xml', 'http://www.politico.com/rss/click.xml', 'http://www.politico.com/rss/rogersimon.xml',
'http://www.politico.com/rss/suitetalk.xml', 'http://www.politico.com/rss/playbook.xml', 'http://www.politico.com/rss/morningscore.xml', 
'http://www.politico.com/rss/morningmoney.xml', 'http://www.politico.com/rss/politicopulse.xml', 'http://www.politico.com/rss/huddle.xml', 
'http://www.politico.com/rss/morningenergy.xml', 'http://www.politico.com/rss/morningdefense.xml', 'http://www.politico.com/rss/morningtech.xml',
'http://www.politico.com/rss/politicopicks.xml', 'http://www.politico.com/rss/Top10Blogs.xml', 'http://www.politico.com/rss/bensmith.xml',
'http://www.politico.com/rss/davidcatanese.xml', 'http://www.politico.com/rss/laurarozen.xml', 'http://www.politico.com/rss/glennthrush.xml', 
'http://www.politico.com/rss/onmedia.xml', 'http://www.politico.com/rss/joshgerstein.xml', 'http://www.politico.com/rss/maggiehaberman.xml', 
'http://www.politico.com/rss/arena/arenatop10.xml', 'http://www.politico.com/rss/Politico44box.xml', 'http://www.politico.com/rss/livepulse.xml']

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

