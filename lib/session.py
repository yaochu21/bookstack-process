import requests
import trafilatura as tra
import json
import re
from enum import Enum
from bs4 import BeautifulSoup

class SegmentType(Enum):
    BODY = 1
    SUBTITLE = 2
    IMAGE = 3
    TABLE = 4

class Segment:
    def __init__(self,string,start,end,type) -> None:
        self.string = string
        self.s = start
        self.e = end
        self.type = type
        self.order = 0

    def seg_to_dict(self):
        return {"string":self.string,"s":self.s,"e":self.e,"type":self.type.name}

# a class to keep information related to a subtitle
class Subtitle(Segment):
    def __init__(self,text,level,start_index,end_index,string):
        self.text = text
        self.level = level
        self.valid = True
        Segment.__init__(self,string,start_index,end_index,SegmentType.SUBTITLE)

    def to_dict(self):
        return {"text":self.text,"level":self.level,"s":self.s,"e":self.e,"valid":self.valid,"string":self.string}

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

        self.segments = []

    # use trafilatura to extract main portion of the article into xml-formatted string
    def extract_main(self,include_tables=True,include_imgs=False):
        fetched = tra.fetch_url(self.url)
        if (fetched == None):
            print("failed to fetch")
            return
        result_text = tra.extract(fetched,output_format="xml",include_formatting=True,include_images=include_imgs,include_tables=include_tables)
        self.text = result_text

        page = requests.get(self.url)
        page.encoding = 'utf-8'
        self.raw = page.text

        self.bs4 = BeautifulSoup(self.raw, "html.parser")

    def extract_metadata(self):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        pattern = re.compile(r'<doc.*title="(.*?)".*date="(.*?)".*tags="(.*?)".*>')
        match_obj = re.search(pattern,self.text)
        self.title,self.date,self.tags = match_obj.group(1),match_obj.group(2),match_obj.group(3).split(',')

        print([self.tags,self.date,self.title])

    def extract_images(self,surround_range=20):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        pattern = re.compile(r'(<)(%s)(.*>)' % "img")
        for matchobj in re.finditer(pattern,self.raw):
            

            new_segment = Segment(matchobj.group(0),matchobj.start(),matchobj.end(),SegmentType.IMAGE)

        pass

    def format_images(self,img_tag="graphic"):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        pattern = re.compile(r'(<)(%s)(.*>)' % img_tag)
        repl = lambda matchobj: matchobj.group(1) + "img" + matchobj.group(3)
        self.text = re.sub(pattern,repl,self.text)

    def format_tables(self):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        pattern = re.compile(r'<table.*?</table>')
        tables_page = re.findall(pattern,self.raw)
        tables_xml = re.findall(pattern,self.text)

        for i,table in enumerate(tables_xml):
            if (i >= len(tables_page)):
                break
            self.text = self.text.replace(table,tables_page[i])

    def identify_formatted_titles(self):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        for i,s in enumerate(["h1","h2","h3","hi"]):
            pattern = re.compile(r'<%s.*>(.*?)</%s>' % (s,s))
            for matchobj in re.finditer(pattern,self.text):
                subtitle = Subtitle(matchobj.group(1),i+1,matchobj.start(),matchobj.end(),matchobj.group(0))
                self.subtitles.append(subtitle)
        
    def identify_non_formatted_titles(self,ruleset=[]):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        ruleset.extend([lambda x: (self.title_length_rule(x))])
        pattern = re.compile(r'<p.*>(.*?)</p>')

        for match in re.finditer(pattern,self.text):
            line = match.group(1)
            if any([rule(line) for rule in ruleset]):
                subtitle = Subtitle(line,5,match.start(),match.end(),match.group(0))
                self.subtitles.append(subtitle)

        print(self.subtitles)
        
    def title_length_rule(self,line,thresh=15):
        return (len(line) <= thresh) and (len(line) > 0)

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

    # break the html into defined segments of pure texts, tables, images, and subtitles
    def define_segments(self):
        segments = [] + self.subtitles
        
        pattern = re.compile(r'<table.*?</table>')
        for matchobj in re.finditer(pattern,self.text):
            new_segment = Segment(matchobj.group(0),matchobj.start(),matchobj.end(),SegmentType.TABLE)
            segments.append(new_segment)
        
        pattern = re.compile(r'<img.*?</img>')
        for matchobj in re.finditer(pattern,self.text):
            new_segment = Segment(matchobj.group(0),matchobj.start(),matchobj.end(),SegmentType.IMAGE)
            segments.append(new_segment)
        self.segments = segments

        pass

    def get_dict_data(self):
        sorted_subtitles_dict =[subtitle.to_dict() for subtitle in sorted(self.subtitles,key=lambda sub: sub.s,reverse=False)]
        sorted_segments_dict = [segment.seg_to_dict() for segment in sorted(self.segments,key=lambda sub: sub.s,reverse=False)]
        data = {"url":self.url,"text":self.text,"author":self.author,"date":self.date,"tags":self.tags,"title":self.title,"subtitles":sorted_subtitles_dict,"segments":sorted_segments_dict}
        return data

    def get_json_data(self):
        data = self.get_dict_data()
        data_string = json.dumps(data,ensure_ascii=False).encode('utf-8')
        return data_string.decode()