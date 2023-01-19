from .session import Pipe
from .bookstack_request import BookstackRequest
from .utils import validate
# from session import Pipe
# from bookstack_request import BookstackRequest
# from utils import validate

import json

def extract(input):
    """
    Extract the main content of the article, metadata, and subtitles
    """
    url = validate(input)
    pipe = Pipe(url)
    try:
        pipe.extract_main()
    except Exception as e:
        raise ValueError("Failed to extract main content: " + str(e))
    try:
        pipe.extract_metadata()
    except Exception as e:
        raise ValueError("Failed to extract metadata: " + str(e))
    try:
        pipe.define_segments()
    except Exception as e:
        raise ValueError("Failed to define segments: " + str(e))
    try:
        pipe.format_tables()
    except Exception as e:
        raise ValueError("Failed to format tables: " + str(e))
    try:
        pipe.identify_subtitles()
    except Exception as e:
        raise ValueError("Failed to identify titles: " + str(e))
    try:
        pipe.extract_images()
    except Exception as e:
        raise ValueError("Failed to extract images: " + str(e))
    
    pipe_data = pipe.get_dict_data()
    return pipe_data

def generate(data):
    request = BookstackRequest(data)
    with open("../test/result.json",'w') as f:
        f.write(data)
    return "None"

if __name__ == "__main__":
    # urls = [
    #     "http://www.stats.gov.cn/tjsj/zxfb./202204/t20220429_1830126.html",
    #     "http://www.stats.gov.cn/tjsj/zxfb/201901/t20190125_1646796.html",
    #     "https://finance.sina.com.cn/china/gncj/2022-06-29/doc-imizirav1142142.shtml",
    #     "https://new.qq.com/rain/a/20220616A09TVG00",
    #     "https://www.163.com/news/article/H5AEBRQN00019UD6.html",
    #     "https://www.jiemian.com/article/7813186.html",
    #     "https://archive.vn/0gYCh",
    # ]

    # pipe_data = extract(urls[2])

    # with open("../test/pipe.json", "w", encoding='utf-8') as f:
    #     f.write(json.dumps(pipe_data,ensure_ascii=False))

    data = {}
    with open("../test/result.json",'r') as f:
        data = json.load(f)

    print(data)
    
    req = BookstackRequest(data)

