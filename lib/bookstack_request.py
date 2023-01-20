import requests
import json
from bs4 import BeautifulSoup
import base64
from .session import Segment,SegmentType,Image,Subtitle
# from session import Segment,SegmentType,Image,Subtitle

# incomplete & deprecated, this request should be handled by the client side
class BookstackRequest:
    def __init__(self,data):
        data_dict = json.loads(data)
        self.html = data_dict['text']
        self.title = data_dict['title']
        self.year = data_dict['date']
        self.area = data_dict['area']
        self.authors = data_dict['author']
        self.rtype = data_dict['rtype']
        self.keywords = data_dict['tags']
        self.book_id = data_dict['book_id']

        self.imgs = data_dict['imgs']
        self.segments = data_dict['segments']

        self.posted_id = None
        self.post_return = None

        self.final_body = ""

    def img_level_map(self,level):
        if (level in [1,2,3]):
            return 'h' + str(level+1)
        if (level >= 4):
            return 'h5'

    def convert_segments(self):
        segments = []
        for seg_dict in self.segments:
            seg_type = SegmentType(seg_dict['type'])

            if (seg_type in [SegmentType.BODY,SegmentType.TABLE,SegmentType.NONE]):
                seg = Segment(seg_dict['string'],seg_dict['s'],seg_dict['e'],seg_dict['tag'],SegmentType.BODY,seg_dict['order']) 
                segments.append(seg)
            elif (seg_type == SegmentType.SUBTITLE):
                seg = Segment(seg_dict['string'],seg_dict['s'],seg_dict['e'],seg_dict['tag'],SegmentType.BODY,seg_dict['order']) 
                seg = Subtitle(seg_dict['text'],seg_dict['level'],seg)
                seg.tag = self.img_level_map(seg.level)
                seg.string = "<%s>%s</%s>" % (seg.tag,seg.text,seg.tag)
                segments.append(seg)
        self.segments = segments

    def process_images(self):
        for img in self.imgs:
            if (not img['valid']):
                continue

            img_string = ""
            img_ret = requests.get(img['url'])
            if (not img_ret.ok):
                img_string = "<img src=\"%s\" referrerPolicy=\"no-referrer\" />" % img['url']
            else:
                bts64 = base64.b64encode(img_ret.content)
                src = "data:image/png;base64, " + str(bts64)
                img_string = "<img src=\"%s\" />" % src
            
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
        pass
