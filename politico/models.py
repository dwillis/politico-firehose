from pytz.gae import pytz
from datetime import timedelta
from google.appengine.ext import db
from appengine_django.models import BaseModel


class Author(BaseModel):
    """
    A reporter who writes a story.
    """
    name = db.StringProperty()
    slug = db.StringProperty()
    story_count = db.IntegerProperty()
    last_updated = db.DateTimeProperty()
    
    def __unicode__(self):
        return self.name
        
    def story_list(self):
        return (x.story for x in self.authorstory_set)
        
    def get_absolute_url(self):
        return "/bylines/%s" % self.slug


class Story(BaseModel):
    """
    A story harvested from one of our feeds.
    """
    title = db.StringProperty()
    link = db.StringProperty()
    updated_date = db.DateTimeProperty()
    multi_byline = db.BooleanProperty()
    
    def __unicode__(self):
        return self.title
        
    def get_url(self):
        return self.link
    
    def updated_local(self):
        return self.updated_date - timedelta(hours=5)
        
    def author_list(self):
        return (x.author.name for x in self.authorstory_set)


class AuthorStory(BaseModel):
    """
    The many-to-many relationship bewtween Stories and Authors.
    """
    author = db.ReferenceProperty(Author, required=True, collection_name="stories")
    story = db.ReferenceProperty(Story, required=True, collection_name="authors")


