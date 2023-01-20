import requests
import base64
from io import BytesIO

url = "https://pic2.pedaily.cn/22/202209/2022951740572246.jpg"

ret = requests.get(url)
bts = base64.b64encode(ret.content)
img_string = "data:image/png;base64, " + str(bts)
print(img_string)