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
        
    def get_url(self):
        return "/bylines/%s" % self.slug

    def updated_local(self):
        return self.last_updated - timedelta(hours=5)
    
    def get_story_list(self):
        """
        Get all the stories written by this author
        """
        from politico.models import Story
        return Story.all().filter('bylines =', self.key()).order("-updated_date")

    def get_story_count(self):
        """
        Count all the stories written by this Author.
        """
        return self.get_story_list().count()


class Story(BaseModel):
    """
    A story harvested from one of our feeds.
    """
    title = db.StringProperty()
    link = db.StringProperty()
    updated_date = db.DateTimeProperty()
    bylines = db.ListProperty(db.Key, default=None)
    
    def __unicode__(self):
        return self.title
        
    def get_url(self):
        return self.link
    
    def updated_local(self):
        return self.updated_date - timedelta(hours=5)
        
    def get_byline_list(self):
        """
        Return all the Authors associated with this story.
        """
        return db.get(self.bylines)
    
    def get_rendered_byline_html(self):
        """
        Return a pretty HTML link list of all the Authors in the bylines.
        """
        from django.utils.text import get_text_list
        author_list = self.get_byline_list()
        author_list.sort(key=lambda x: x.name)
        return get_text_list([
            '<a href="%s">%s</a>' % (i.get_url(), i.name) for i in author_list
        ], 'and')
    


