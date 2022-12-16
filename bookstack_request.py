
class BookstackRequest:
    def __init__(self,data_dict,token,token_id,book_id):
        self.data_dict = data_dict
        self.token = token
        self.token_id = token_id
        self.book_id = book_id
        self.api_url = "https://report.laodongqushi.com/api/pages"

    def post(self):
        name = self.data_dict["title"]
        tags = [{"发布年份"}]
        tags.extend([{"name":"关键词","value":entry} for entry in self.data_dict["tags"]])

