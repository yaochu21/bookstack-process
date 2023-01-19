import requests
import json
from bs4 import BeautifulSoup
# from session import Segment,SegmentType,Image,Subtitle
from .session import Segment,SegmentType,Image,Subtitle

# incomplete & deprecated, this request should be handled by the client side
class BookstackRequest:
    def __init__(self,data_dict):
        # data_dict = json.loads(data)
        self.html = data_dict['text']
        self.title = data_dict['title']
        self.year = data_dict['date']
        self.area = data_dict['area']
        self.authors = data_dict['author']
        self.rtype = data_dict['rtype']
        self.keywords = data_dict['tags']

        self.imgs = data_dict['imgs']
        self.segments = data_dict['segments']

        self.api_url = "https://report.laodongqushi.com/api/pages"
        self.posted_id = None

        self.final_body = ""

    def process_images(self):
        for img in self.imgs:
            if (not img['valid']):
                continue
            imgString = "<img src=" + img['src'] + " />"

        # map images to segments
        # add to list of segments
        pass

    def format_subtitles(self):
        # for each subtitle segment, edit tag/html string according to level
        pass

    def stich_segments(self):
        # join segments into string
        # make html string with bs4
        pass

    def post_body(self):
        tags = [{"name":"发布年份","value":self.year},
                {"name":"地区","value":self.area}]
        tags.extend([{"name":"作者/机构","value":entry} for entry in self.data_dict["author"]])
        tags.extend([{"name":"调查方式","value":entry} for entry in self.data_dict["rtype"]])
        tags.extend([{"name":"关键词","value":entry} for entry in self.data_dict["tags"]])
        book_id = 0

        post_data = {
            "book_id":book_id,
            "name":self.title,
            "html":self.html,
            "tags":tags
        }
        headers = {
            "Authorization":"Token vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I:OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8",
        }

        ret = requests.post(self.api_url,json=post_data,headers=headers)
        ret.encoding = 'utf-8'

    def post_attachments():
        pass
