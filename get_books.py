import requests
import json

token = "OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8"
token_id = "vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I"
api_url = "https://report.laodongqushi.com/api/pages"
book_id = 1
name = "测试页面"
html = "<body><p>hi</p></body>"
tags = [
    {'name':'作者/机构','value':'某作者'},
    {'name':'地区','value':'全国'}
]

post_data = {
    "book_id":book_id,
    "name":name,
    "html":html,
    "tags":tags
}
headers = {
    "Authorization":"Token vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I:OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8",
}

# ret = requests.post(api_url,json=post_data,headers=headers)
# print(ret.text)
ret = requests.get("https://report.laodongqushi.com/api/books",headers=headers)

ret.encoding = 'utf-8'
ret_dict = json.loads(ret.text)
books = ret_dict['data']

book_labels = []
for book in books:
    book_labels.append({"label":book["name"],"value":book["id"]})

print(books)
print("-----")
print(book_labels)