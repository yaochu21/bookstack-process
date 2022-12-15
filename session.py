import requests
import trafilatura as tra
import json
import re

# a class to keep information related to a subtitle
class Subtitle:
    def __init__(self,string,level,start_index,end_index):
        self.string = string
        self.level = level
        self.s = start_index
        self.e = end_index

# a class to keep context related to a single processing session
class Pipe:
    def __init__(self,url):
        self.url = url
        self.text = ""      # xml text string representing the article that is put through stages of formatting
        self.name = ""      # name of the author, not implemented
        self.date = ""      # publication date
        self.tags = []      # a list of tags
        self.title = ""     # the main title of the article
        self.subtitles = [] # a list of Subtitle objects

    def extract_main(self,include_tables=False,include_imgs=False):
        fetched = tra.fetch_url(self.url)
        if (fetched == None):
            print("failed to fetch")
            return
        result_text = tra.extract(fetched,output_format="xml",include_formatting=True,include_images=include_imgs,include_tables=include_tables)
        self.text = result_text

    def extract_metadata(self):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        pattern = re.compile(r'<doc.*title="(.*?)".*date="(.*?)".*tags="(.*?).*">')
        match_obj = re.search(pattern,self.text)
        self.title,self.date,self.tags = match_obj.group(1),match_obj.group(2),match_obj.group(3).split(',')

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
        page = requests.get(self.url)
        page.encoding = 'utf-8'
        pattern = re.compile(r'<table.*?</table>')
        tables_page = re.findall(pattern,page.text)
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
            pattern = re.compile(r'<%s(.*?)</%s>' % (s,s))
            for matchobj in re.finditer(pattern,self.text):
                subtitle = Subtitle(matchobj.group(1),i+1,matchobj.start(),matchobj.end())
                self.subtitles.append(subtitle)
        
    def identify_non_formatted_titles(self,ruleset=[]):
        if (len(self.text) <= 0):
            print("no text to to process")
            return
        ruleset.extend([self.title_length_rule,self.title_prefix_rule])
        pattern = re.compile(r'<p(.*?)</p>')

        for match in re.finditer(pattern,self.text):
            line = match.group(1)
            if any([rule(line) for rule in ruleset]):
                subtitle = Subtitle(line,5,match.start(),match.end())
                self.subtitles.append(subtitle)
        
    def title_length_rule(line,thresh=15):
        return len(line) <= 15

    def title_prefix_rule(line):
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

    def get_subtitles_json(self):
        sorted_subtitles = sorted(self.subtitles,key=lambda sub: sub.s)
        
