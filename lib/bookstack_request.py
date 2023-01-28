import requests
import json
from bs4 import BeautifulSoup
import base64
from .session import Segment,SegmentType,Image,Subtitle
# from session import Segment,SegmentType,Image,Subtitle

# incomplete & deprecated, this request should be handled by the client side
class BookstackRequest:
    def __init__(self,data,url):
        data_dict = json.loads(data)
        self.html = data_dict['text']
        self.title = data_dict['title']
        self.year = data_dict['date']
        self.area = data_dict['area']
        self.authors = data_dict['author']
        self.rtype = data_dict['rtype']
        self.keywords = data_dict['tags']
        self.book_id = data_dict['book_id']
        self.url = url

        self.imgs = data_dict['imgs']
        self.segments = data_dict['segments']

        self.posted_id = None
        self.post_return = None

        self.final_body = ""

    def img_level_map(self,level):
        if (level in [1,2,3]):
            return 'h' + str(level+2)
        if (level >= 4):
            return 'h6'

    def convert_segments(self):
        segments = []
        for seg_dict in self.segments:
            seg_type = SegmentType(seg_dict['type'])

            if (seg_type in [SegmentType.BODY,SegmentType.NONE]):
                seg = Segment(seg_dict['string'],seg_dict['s'],seg_dict['e'],seg_dict['tag'],SegmentType.BODY,seg_dict['order']) 
                segments.append(seg)
            elif (seg_type == SegmentType.TABLE):
                seg = Segment(seg_dict['string'],seg_dict['s'],seg_dict['e'],seg_dict['tag'],SegmentType.TABLE,seg_dict['order'])
                seg.center_segment()
                segments.append(seg)
            elif (seg_type == SegmentType.SUBTITLE):
                if (not seg_dict['valid']):
                    seg = Segment(seg_dict['string'],seg_dict['s'],seg_dict['e'],seg_dict['tag'],SegmentType.BODY,seg_dict['order'])
                    seg.update_tag("p")
                else:
                    seg = Segment(seg_dict['string'],seg_dict['s'],seg_dict['e'],seg_dict['tag'],SegmentType.SUBTITLE,seg_dict['order']) 
                    seg = Subtitle(seg_dict['text'],seg_dict['level'],seg)
                    seg.tag = self.img_level_map(seg.level)
                    seg.string = "<%s>%s</%s>" % (seg.tag,seg.text,seg.tag)

                    padding_seg = Segment("<p></p>",-1,-1,"p",SegmentType.BODY,seg.order - 1)
                    segments.append(padding_seg)
                segments.append(seg)
        self.segments = segments

    def process_images(self):
        for img in self.imgs:
            if (not img['valid']):
                continue

            src = "data:image/jpg;base64, " + str(img['url'])
            img_string = "<img src=\"{0}\" width=\"80%\" style=\"display: block; margin-left: auto; margin-right: auto; padding-bottom: 30px\"/>".format(src)
            
            seg = Segment(img_string,-1,-1,"img",SegmentType.IMAGE,img['order'])
            self.segments.append(seg)

    def stich_segments(self):
        self.segments = sorted(self.segments,key=lambda seg: seg.order)
        seg_strings = [segment.string for segment in self.segments]
        body = '\n'.join(seg_strings)
        body = '<body>%s</body>' % body

        bs = BeautifulSoup(body,"html.parser")
        self.final_body = bs.prettify()

    def post(self):
        tags = [{"name":"发布年份","value":self.year},
                {"name":"地区","value":self.area}]
        tags.extend([{"name":"作者/机构","value":entry} for entry in self.authors])
        tags.extend([{"name":"调查方式","value":entry} for entry in self.rtype])
        tags.extend([{"name":"关键词","value":entry} for entry in self.keywords])

        post_data = {
            "book_id":self.book_id,
            "name":self.title,
            "html":self.final_body,
            "tags":tags,
        }

        headers = {
            "Authorization":"Token vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I:OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8",
        }

        ret = requests.post("https://report.laodongqushi.com/api/pages",json=post_data,headers=headers)
        if (not ret.ok):
            raise Exception("Bookstack api invalid response: %s" % ret.status_code)
        
        ret.encoding = 'utf-8'
        self.post_return = json.loads(ret.text)

    def post_attachments(self):
        id = self.post_return['id']
        url = self.url

        post_data = {
            "name": "原文",
            "uploaded_to": id,
            "link": url
        }
        headers = {
            "Authorization":"Token vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I:OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8",
        }

        ret = requests.post("https://report.laodongqushi.com/api/attachments",json=post_data,headers=headers)

        if (not ret.ok):
            raise Exception("Bookstack api invalid response")
        
        post_data = {
            "name": "备份",
            "uploaded_to": id,
            "link": "https://archive.vn/" + url
        }

        ret = requests.post("https://report.laodongqushi.com/api/attachments",json=post_data,headers=headers)

        if (not ret.ok):
            raise Exception("Bookstack api invalid response")