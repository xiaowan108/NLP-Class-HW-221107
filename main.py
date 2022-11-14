import requests
from bs4 import BeautifulSoup
from string import punctuation, ascii_letters, digits
import nltk
import os

def ptt_scraping(url):
    articles = []
    r = requests.get(url=URL, cookies={"over18":"1"})
    soup = BeautifulSoup(r.text, "lxml")
    tag_divs = soup.find_all("div", class_="r-ent")
    for tag in tag_divs:
        if tag.find("a"):
            href = tag.find("a")["href"]
            title = tag.find("a").text
            
            r2=requests.get(url="http://ptt.cc"+href, cookies={"over18":"1"})
            soup2 = BeautifulSoup(r2.text, "lxml")
            articles.append({"title":title, "href":href, "text":soup2.text})
    return articles

URL = "https://www.ptt.cc/bbs/Plant"
print(URL)

articles = ptt_scraping(url=URL)
for i in range(5):
    article = articles[i]
    filename = article["href"].split("/")[-1]
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "Plant")):
        os.mkdir(os.path.join(os.path.dirname(__file__), "Plant"))

    with open(os.path.join(os.path.dirname(__file__), "Plant", F"{filename}.txt"), "w", encoding="utf8") as file1:
        file1.write(article["title"] + "\n")
        file1.write(article["text"])
    print("full-href", URL[:14] + article["href"])
    print("title", article["title"])


URL = "https://www.ptt.cc/bbs/Agriculture"
print(URL)
articles = ptt_scraping(url=URL)
for i in range(5):
    article = articles[i]
    filename = article["href"].split("/")[-1]
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "Agriculture")):
        os.mkdir(os.path.join(os.path.dirname(__file__), "Agriculture"))
    with open(os.path.join(os.path.dirname(__file__), "Agriculture", F"{filename}.txt"), "w", encoding="utf8") as file1:
        file1.write(article["title"] + "\n")
        file1.write(article["text"])
    print("full-href", URL[:14] + article["href"])
    print("title", article["title"])
