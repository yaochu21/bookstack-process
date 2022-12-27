from .session import Pipe
from .utils import validate_url

def validate(input):
    """
    Validate the input string is a url
    """
    if not validate_url(input):
        raise ValueError("Input is not a valid url")
    return input

def extract(input):
    """
    Extract the main content of the article and date, tags etc. metadata
    """
    url = validate(input)
    pipe = Pipe(url)
    pipe.extract_main()
    pipe.extract_metadata()
    pipe.format_images()
    pipe.format_tables()
    pipe.identify_formatted_titles()
    pipe.identify_non_formatted_titles()
    pipe_data = pipe.get_dict_data()
    return pipe_data

if __name__ == "__main__":
    urls = [
        "http://www.stats.gov.cn/tjsj/zxfb./202204/t20220429_1830126.html",
        "http://www.stats.gov.cn/tjsj/zxfb/201901/t20190125_1646796.html",
        "https://finance.sina.com.cn/china/gncj/2022-06-29/doc-imizirav1142142.shtml",
        "https://new.qq.com/rain/a/20220616A09TVG00",
        "https://www.163.com/news/article/H5AEBRQN00019UD6.html",
        "https://www.jiemian.com/article/7813186.html",
        "https://archive.vn/0gYCh",
    ]

    pipe_data = extract(urls[0])

    with open("test/pipe.json", "w") as f:
        f.write(pipe_data)
