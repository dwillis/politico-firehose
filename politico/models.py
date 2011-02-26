from appengine_django.models import BaseModel
from google.appengine.ext import db

class Story(BaseModel):
    title = db.StringProperty()
    link = db.StringProperty()
    byline = db.StringProperty()
    updated_date = db.DateTimeProperty()
    
    def __unicode__(self):
        return self.title
        
    def get_url(self):
        return self.link
