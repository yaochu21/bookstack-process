from session import Pipe
import trafilatura as tra
import requests
import json

urls = ["http://www.stats.gov.cn/tjsj/zxfb./202204/t20220429_1830126.html",
        "http://www.stats.gov.cn/tjsj/zxfb/201901/t20190125_1646796.html",
        "https://finance.sina.com.cn/china/gncj/2022-06-29/doc-imizirav1142142.shtml",
        "https://new.qq.com/rain/a/20220616A09TVG00",
        "https://www.163.com/news/article/H5AEBRQN00019UD6.html",
        "https://www.jiemian.com/article/7813186.html",
        "https://archive.vn/0gYCh"]

pipe = Pipe(urls[1])
pipe.extract_main()
pipe.extract_metadata()
pipe.format_images()
pipe.format_tables()
pipe.identify_formatted_titles()
pipe.identify_non_formatted_titles()
pipe_data = pipe.get_json_data()

with open('pipe.json','w') as f:
    f.write(pipe_data)

"""
token = "OxrfZbHz09xnUSbm6mRb7aY1XtwjRmU8"
token_id = "vZdwWsto1ZJHjyvQ9mDmzp9dZTDh3Z7I"

api_url = "https://report.laodongqushi.com/api/pages"
book_id = 1
name = "测试页面"
html = "<p>test</p>"
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
ret = requests.post(api_url,json=post_data,headers=headers)
"""