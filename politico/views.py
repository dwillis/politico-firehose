import StringIO
import datetime, time
from google.appengine.api import taskqueue
from politico.models import Story, Author, AuthorStory
from google.appengine.api.urlfetch import fetch
from toolbox import feedparser
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.template.defaultfilters import slugify

feeds = ['http://feeds.politico.com/politico/rss/congress', 'http://www.politico.com/rss/life.xml', 'http://www.politico.com/rss/lobbyists.xml',
'http://www.politico.com/rss/pitboss.xml', 'http://www.politico.com/rss/politics.xml', 'http://www.politico.com/rss/2012-election.xml', 
'http://www.politico.com/rss/2012-election-blog.xml', 'http://www.politico.com/rss/rogersimon.xml', 'http://www.politico.com/rss/suitetalk.xml', 'http://www.politico.com/rss/playbook.xml', 'http://www.politico.com/rss/morningscore.xml', 
'http://www.politico.com/rss/morningmoney.xml', 'http://www.politico.com/rss/politicopulse.xml', 'http://www.politico.com/rss/huddle.xml', 
'http://www.politico.com/rss/morningenergy.xml', 'http://www.politico.com/rss/morningdefense.xml', 'http://www.politico.com/rss/morningtech.xml',
'http://www.politico.com/rss/politicopicks.xml', 'http://www.politico.com/rss/Top10Blogs.xml', 'http://www.politico.com/rss/bensmith.xml',
'http://www.politico.com/rss/davidcatanese.xml', 'http://www.politico.com/rss/laurarozen.xml', 'http://www.politico.com/rss/glennthrush.xml', 
'http://www.politico.com/rss/onmedia.xml', 'http://www.politico.com/rss/joshgerstein.xml', 'http://www.politico.com/rss/maggiehaberman.xml', 
'http://www.politico.com/rss/Politico44box.xml', 'http://www.politico.com/rss/livepulse.xml']

def index(request):
    latest_stories = Story.all().order('-updated_date').fetch(25)
    context = {
        'headline': "Winning the present",
        'object_list': latest_stories,
    }
    return direct_to_template(request, 'index.html', context)

def byline_detail(request, slug):
    author = Author.all().filter('slug =', slug).get()
    context = {
        'author' : author,
        'headline': "Article Archive",
        'object_list': author.stories,
    }
    return direct_to_template(request, 'byline_detail.html', context)
    

def fetch_feeds(request):
    for url in feeds:
        taskqueue.add(url = '/_update_feed/', params = {'url' : url}, method='GET')
    return HttpResponse('ok!')


def update_feed(request):
    url = request.GET['url']
    content = fetch(url).content
    d = feedparser.parse(StringIO.StringIO(content))
    for entry in d.entries:
        story_query = Story.all()
        story = story_query.filter('link =', entry.id).get()
        if not story:
            authors = entry.author.split(',')
            if len(authors) > 1:
                multi_byline = True
            else:
                multi_byline = False
            story = Story(link = entry.id, title = entry.title, updated_date = datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed)), multi_byline = multi_byline)
            story.put()
            for author in authors:
                author_query = Author.all()
                a = author_query.filter('slug =', str(slugify(author))).get()
                if a:
                    a.story_count += 1
                    if story.updated_date > a.last_updated:
                        a.last_updated = story.updated_date
                        a.save()
                else:
                    a = Author(name = author, slug = str(slugify(author)), story_count = 1, last_updated = story.updated_date)
                    a.put()
                AuthorStory(author=a, story=story).put()

    return HttpResponse('ok!')
