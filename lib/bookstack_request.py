import requests

# incomplete & deprecated, this request should be handled by the client side
class BookstackRequest:
    def __init__(self,url,data_dict):
        self.url = url
        self.data_dict = data_dict
        self.api_url = "https://report.laodongqushi.com/api/pages"

    def post(self):
        name = self.data_dict["title"]
        html = self.data_dict["text"]
        tags = [{"name":"发布年份","value":self.data_dict["date"]},
                {"name":"地区","value":self.data_dict["area"]},
        ]
        tags.extend([{"name":"作者/机构","value":entry} for entry in self.data_dict["author"]])
        tags.extend([{"name":"调查方式","value":entry} for entry in self.data_dict["rtype"]])
        tags.extend([{"name":"关键词","value":entry} for entry in self.data_dict["tags"]])
        book_id = 0

        post_data = {
            "book_id":book_id,
            "name":name,
            "html":html,
            "tags":tags
        }
        headers = {
            "Authorization":"Token vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I:OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8",
        }

        ret = requests.post(self.api_url,json=post_data,headers=headers)
        ret.encoding = 'utf-8'


