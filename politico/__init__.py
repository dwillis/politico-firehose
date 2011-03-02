import os
import yaml


def get_feeds():
    """
    Retrieve all the feeds from the YAML config as a Python list.
    """
    path = os.path.join(os.path.dirname(__file__), 'feeds.yaml')
    data = yaml.load(open(path))
    return data['feeds']
