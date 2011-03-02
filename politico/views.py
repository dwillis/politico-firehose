from politico.models import Story, Author, AuthorStory
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template



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
    


