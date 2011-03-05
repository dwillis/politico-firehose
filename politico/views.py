# Utils
from datetime import timedelta, datetime

# Models
from politico.models import Story, Author

# Responses
from django.http import Http404, HttpResponse
from django.views.generic.simple import direct_to_template


def index(request):
    """
    The homepage.
    """
    latest_stories = Story.all().order('-updated_date').fetch(25)
    context = {
        'headline': "Winning the present",
        'object_list': latest_stories,
        'selected': 'index',
    }
    return direct_to_template(request, 'index.html', context)


def byline_detail(request, slug):
    """
    A page with everything written by one of the Authors.
    """
    author = Author.get_by_key_name(slug)
    if not author:
        raise Http404
    context = {
        'author' : author,
        'now': datetime.now() - timedelta(hours=5),
        'selected': 'byline_list',
    }
    return direct_to_template(request, 'byline_detail.html', context)


def byline_scoreboard(request):
    """
    A ranking of the authors by number of bylines
    """
    object_list = Author.all().order("-story_count")
    context = {
        'object_list': object_list,
        'selected': 'byline_scoreboard',
    }
    return direct_to_template(request, 'byline_scoreboard.html', context)


def byline_list(request):
    """
    A list of all the Authors we have archived.
    """
    object_list = Author.all().order("name")
    context = {
        'object_list': object_list,
        'selected': 'byline_list',
    }
    return direct_to_template(request, 'byline_list.html', context)


def feed_list(request):
    """
    A list of all the RSS feeds we provide.
    """
    object_list = Author.all().order("name")
    context = {
        'object_list': object_list,
        'selected': 'feed_list',
    }
    return direct_to_template(request, 'feed_list.html', context)


