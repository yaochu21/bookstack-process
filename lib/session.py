import requests
import trafilatura as tra
import json
import re
from enum import Enum
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# used for debugging
class SegmentType(Enum):
    BODY = 1
    SUBTITLE = 2
    IMAGE = 3
    TABLE = 4
    NONE = 5

class Segment:
    def __init__(self,string,start,end,tag,type=SegmentType.NONE) -> None:
        self.string = string
        self.s = start
        self.e = end
        self.tag = tag
        self.type = type
        self.order = 0

    def seg_to_dict(self):
        return {"string":self.string,"s":self.s,"e":self.e,"type":self.type.name}

# a class to keep information related to a subtitle
class Subtitle():
    def __init__(self,text,level,id):
        self.text = text
        self.level = level
        self.valid = True
        self.s = id

    def to_dict(self):
        return {"text":self.text,"level":self.level,"valid":self.valid,"s":self.s}

class Image():
    def __init__(self,url,id,valid=True):
        self.url = url
        self.valid = valid
        self.id = id

    def to_dict(self):
        return {"url":self.url,"valid":self.valid,"id":self.id}

# a class to keep context related to a single processing session
class Pipe:
    def __init__(self,url):
        self.url = url
        self.raw = ""       # the raw html string from response.text
        self.bs4 = None     # the bs4 object constructed from self.raw
        self.text = ""      # xml text string representing the article that is put through stages of formatting

        self.author = ""    # name of the author, not implemented
        self.date = ""      # publication date
        self.tags = []      # a list of tags
        self.title = ""     # the main title of the article
        self.subtitles = [] # a list of Subtitle objects

        self.imgs = []
        self.segments = []

    # use trafilatura to extract main portion of the article into xml-formatted string
    def extract_main(self,include_tables=True,include_imgs=False):
        fetched = tra.fetch_url(self.url)
        if (fetched == None):
            raise Exception("tra failed to fetch")
        result_text = tra.extract(fetched,output_format="xml",include_formatting=True,include_images=include_imgs,include_tables=include_tables)
        self.text = result_text
        print(self.text)
        print("----------")

        page = requests.get(self.url)
        page.encoding = 'utf-8'
        self.raw = page.text

        self.bs4 = BeautifulSoup(self.raw, "html.parser")

    def extract_metadata(self):
        pattern = re.compile(r'<doc.*title="(.*?)".*date="(.*?)".*tags="(.*?)".*>')
        match_obj = re.search(pattern,self.text)
        self.title,self.date,self.tags = match_obj.group(1),match_obj.group(2),match_obj.group(3).split(',')

        print([self.tags,self.date,self.title])

    # break the html into defined segments of pure texts, tables, images, and subtitles
    def define_segments(self):
        patterns = []
        tags = ['img','table','hi','h1','h2','h3','p']
        for tag in tags:
            patterns.append(re.compile(r'<%s.*?>(.*?)</%s>' % (tag,tag)))

        for pattern,tag in zip(patterns,tags):
            objs = re.finditer(pattern,self.text)
            seg_type = SegmentType.NONE
            if (tag == 'p'):
                seg_type = SegmentType.BODY
            elif (tag == 'img'):
                seg_type = SegmentType.IMAGE
            elif (tag == 'table'):
                seg_type = SegmentType.TABLE
            elif (tag in ['hi','h1','h2','h3']):
                seg_type = SegmentType.SUBTITLE

            for obj in objs:
                if (not self.search_segment_range(obj.start(),obj.end())):
                    continue
                self.segments.append(Segment(obj.group(0),obj.start(),obj.end(),tag,seg_type))

        self.segments = sorted(self.segments,key=lambda seg: seg.s)

        last_seg = self.segments[0]
        new_segments = [last_seg]
        for i in range(1,len(self.segments)):
            curr_seg = self.segments[i]
            if (curr_seg.e < last_seg.e):
                continue
            if (curr_seg.s < last_seg.e):
                raise Exception("error parsing segment order")
            new_segments.append(curr_seg)
            last_seg = curr_seg
        self.segments = new_segments

        # print("validate seg partition:" + str(self.validate_segment_partition()))

    def search_segment_range(self,start,end):
        for segment in self.segments:
            if (start >= segment.s and end <= segment.e):
                return False
        return True

    def validate_segment_partition(self):
        last_seg = self.segments[0]
        for i in range(1,len(self.segments)):
            curr_seg = self.segments[i]
            if (curr_seg.s == last_seg.e):
                last_seg = curr_seg
                continue
            print(i)
            print(curr_seg.s)
            print(last_seg.e)
            return False
        return True

    def format_tables(self): 
        pattern = re.compile(r'<table.*?</table>')
        tables_page = re.findall(pattern,self.raw)

        i = 0
        for segment in self.segments:
            if (segment.type != SegmentType.TABLE):
                continue
            if (i >= len(tables_page)):
                break
            segment.string = tables_page[i]
            segment.e = segment.s + len(segment.string)
            i += 1

    def identify_subtitles(self,ruleset=[]):
        ruleset = []
        ruleset.extend([lambda x: (self.title_length_rule(x)),lambda x: (self.title_prefix_rule(x))])

        for segment in self.segments:
            if (segment.type not in [SegmentType.BODY,SegmentType.SUBTITLE]):
                continue

            # pattern = re.compile(r'<%s.*?>(.*?)</%s>' % (segment.tag,segment.tag))
            # match = re.search(pattern,segment.string)
            # clean_text = match.group(1)

            bs = BeautifulSoup(segment.string,"html.parser")
            clean_text = bs.text

            if (segment.type == SegmentType.SUBTITLE):
                self.subtitles.append(Subtitle(clean_text,1,segment.s))
            elif (segment.type == SegmentType.BODY):
                if (any([rule(clean_text) for rule in ruleset])):
                    segment.type = SegmentType.SUBTITLE
                    self.subtitles.append(Subtitle(clean_text,segment.s))
    
    def title_length_rule(self,line,thresh=15):
        return (len(line) <= thresh) and (len(line) > 3)

    def title_prefix_rule(self,line):
        prefix_patterns = [r'^[A-Z][.,、，]',
                           r'^[0-9]+[.,、，]',
                           r'^\([A-Z]\)[.,、，]*',
                           r'^\([0-9]+\)[.,、，]*',
                           r'^[一二三四五六七八九十+][.,、，]',
                           r'^\([一二三四五六七八九十]+\)[.,、，]*']

        for prefix_pattern in prefix_patterns:
            pattern = re.compile(prefix_pattern)
            match = re.search(pattern,line)
            if (match != None):
                return True
        return False

    def extract_images(self):
        imgs = self.bs4.find_all('img')
        for i,img in enumerate(imgs):
            url = img['src']
            url = urljoin(self.url,url)
            self.imgs.append(Image(url,i))

    def get_dict_data(self):
        sorted_subtitles_dict =[subtitle.to_dict() for subtitle in self.subtitles]
        sorted_segments_dict = [segment.seg_to_dict() for segment in self.segments]
        sorted_imgs_dict = [img.img_to_dict() for img in self.imgs]
        data = {"url":self.url,"text":self.text,"author":self.author,"date":self.date,"tags":self.tags,"title":self.title,"imgs":sorted_imgs_dict,"subtitles":sorted_subtitles_dict,"segments":sorted_segments_dict}
        return data

    def get_json_data(self):
        data = self.get_dict_data()
        data_string = json.dumps(data,ensure_ascii=False).encode('utf-8')
        return data_string.decode()