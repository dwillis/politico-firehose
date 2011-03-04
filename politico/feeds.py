from politico.models import Story, Author
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist


class LatestStories(Feed):
    title = "Politico Firehose"
    link = "http://politico-firehose.appspot.com/"
    description = "The latest content churned out by Politico.com"
    title_template = "feeds/story_title.html"
    description_template = "feeds/story_description.html"
    
    def items(self):
        return Story.all().order("-updated_date")[:10]
    
    def item_pubdate(self, item):
        return item.updated_date
    
    def item_link(self, item):
        return item.get_url()


class AuthorFeeds(Feed):
    """
    The latest stories by a particular Author.
    """
    title_template = "feeds/story_title.html"
    description_template = "feeds/story_description.html"
    
    def get_object(self, bits):
        if len(bits) != 1:
            raise FeedDoesNotExist
        return Author.get_by_key_name(bits[0])
        
    def title(self, obj):
        return "%s Firehose" % obj.name
                
    def description(self, obj):
        return "The latest Politico stories by %s" % obj.name
        
    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()
        
    def items(self, obj):
        return obj.get_story_list().fetch(10)
    
    def item_link(self, item):
        if not item:
            raise FeedDoesNotExist
        return item.link
    
    def item_pubdate(self, item):
        return item.updated_date
