from appengine_django.models import BaseModel
from google.appengine.ext import db
from pytz.gae import pytz
from datetime import timedelta

class Author(BaseModel):
    name = db.StringProperty()
    slug = db.StringProperty()
    story_count = db.IntegerProperty()
    last_updated = db.DateTimeProperty()
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/bylines/%s" % self.slug
    
    def story_list(self):
        return [x.story for x in sorted(author.stories)]
    
    def updated_local(self):
        return self.last_updated - timedelta(hours=5)

class Story(BaseModel):
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
    
class AuthorStory(BaseModel):
    author = db.ReferenceProperty(Author, required=True, collection_name="stories")
    story = db.ReferenceProperty(Story, required=True, collection_name="authors")
    

    