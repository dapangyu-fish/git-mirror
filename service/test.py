import requests

url = "https://github.com/Genymobile/scrcpy.git/info/refs?service=git-upload-pack"
filename = "abc"

response = requests.get(url)
if response.status_code == 200:
    with open(filename, "wb") as file:
        file.write(response.content)
    print("文件下载成功！")
else:
    print("文件下载失败！")