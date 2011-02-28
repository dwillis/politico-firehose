from politico.models import Story
from django.contrib.syndication.feeds import Feed


class LatestItems(Feed):
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
