# GAE toys
from google.appengine.ext import db
from google.appengine.api import taskqueue
from appengine_django.models import BaseModel

# Et cetera
from datetime import timedelta
from django.utils import simplejson
from django.utils.text import get_text_list
from django.template import Template, Context


#
# Stories
#

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
        
    def get_absolute_url(self):
        return "/bylines/%s" % self.slug
    
    def get_feed_url(self):
        return "/feeds/author/%s/" % self.slug

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
    
    def get_display_story_count(self):
        """
        Pull the story count from the datastore with the fastest way available.
        
        Tries the `story_count` field first, but then falls back to a db query.
        """
        # If we have a count in the db, just use that
        if self.story_count:
            return self.story_count
        # Otherwise...
        else:
            # Schedule a write of the latest count to the db
            taskqueue.add(
                    url = '/_update_story_count_for_author/',
                    params = {'key' : self.key()},
                    method='GET'
            )
            # And return the results of a live db hit.
            return self.get_story_count()


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
        author_list = self.get_byline_list()
        author_list.sort(key=lambda x: x.name)
        return get_text_list([
            '<a href="%s">%s</a>' % (i.get_absolute_url(), i.name) 
            for i in author_list], 'and')

#
# Stats
#

class HourlyStats(BaseModel):
    """
    A breakdown of how many stories have been published in each hour of the 
    day, stored as a JSON object that can be easily analyzed and reused.
    """
    creation_datetime = db.DateTimeProperty()
    data = db.TextProperty()
    
    def get_data_dict(self):
        """
        Return JSON data stored in the object as a Python dictionary
        """
        return simplejson.loads(self.data)
    
    def get_sorted_data_list(self):
        """
        Return JSON data as a list of tuples sorted from midnight to 11pm.
        
        The first item in each tuple is the hour, the second is the story
        count.
        """
        data_dict = self.get_data_dict()
        # Convert it to a list of tuples, with the keys as ints
        data_list = [(int(k), v) for k,v in data_dict.items()]
        # Sort by the keys, a.k.a. the hours
        data_list.sort(key=lambda x:x[0])
        # Pass it out
        return data_list
    
    def get_chart_html(self):
        """
        Return a Google chart displaying the hourly distribution as a bar chart.
        """
        # Pull the data
        data_list = self.get_sorted_data_list()
        # Split the story counts from the hours, maintaining their order
        values = [i[1] for i in data_list]
        labels = [i[0] for i in data_list]
        # Configure the labels that run at the top of each column.
        point_labels = [(
           "number", "*0s*", "000000", i, 13, 1, "e::5"
           ) for i in range(0, len(values)+1)]
        # Set the scale for the chart based on the max value
        data_scale = "%s,%s" % (0, max(values)*1.2)
        # Stuff all of the data into a dictionary for use in the template
        kwargs = dict(
            values=values,
            labels=labels,
            point_labels=point_labels,
            data_scale=data_scale,
            style="747170,14,0,t,ffffff",
            colors="|".join(['1B70B3' for i in range(0, len(values))]),
        )
        # Slot all of the settings into the google chart maker templatetag.
        template = """
        {% load charts %}
            {% chart %}
                {% chart-title 'Total stories by hour' %}
                {% chart-data values %}
                {% chart-size "950x250" %}
                {% chart-type "column" %}
                {% chart-bar-width 30 10 10 %}
                {% data-point-labels 0 point_labels %}
                {% axis "bottom" %}
                    {% axis-style style %}
                    {% axis-labels labels %}
                {% endaxis %}
                {% axis "left" %}
                    {% axis-style "ffffff,10,0,t,ffffff" %}
                {% endaxis %}
                {% chart-data-scale data_scale %}
                {% chart-colors colors %}
            {% endchart %}
        """
        # Render the templatetag as HTML
        cxt = Context(kwargs)
        html = Template(template).render(cxt)
        # Pass it out
        return html


