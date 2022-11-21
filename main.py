import requests
from bs4 import BeautifulSoup
from string import punctuation, ascii_letters, digits
import nltk
import os
import codecs
import jieba
from collections import Counter
import json
from threading import Thread


URL = "https://www.ptt.cc/bbs/Plant"
baseUrl = 'https://www.ptt.cc/bbs/'
articles = []

def getAllContent(hrefs, page):
    num = len(hrefs)
    #設定8線程
    threadsNum = 8
    #新增Thread
    print(F"取得所有資料中，共{num}筆")
    tmp = (int)(num/threadsNum)
    thr = {}
    thr[0] = Thread(target=getContent, kwargs={'start':1, 'end':tmp, 'hrefs': hrefs, 'page': page})
    for i in range(1,threadsNum-1):
        thr[i] = Thread(target=getContent, kwargs={'start':tmp*i, 'end':tmp*(i+1), 'hrefs': hrefs, 'page': page})
    thr[threadsNum-1] = Thread(target=getContent, kwargs={'start':tmp*(threadsNum-1), 'end':num, 'hrefs': hrefs, 'page': page})
    #thread開始
    for i in range(threadsNum):
        thr[i].start()
    #將thread加入完成檢查
    for i in range(threadsNum):
        thr[i].join()

def getAllhref(page):
    hrefs = []
    baseUrl = 'https://www.ptt.cc/bbs/'
    url = baseUrl + page
    r = requests.get(url, cookies={"over18":"1"})
    soup = BeautifulSoup(r.text, "html5lib")
    #將標題頁網址加入
    tag_divs = soup.find_all("div", class_="title")
    for tag in tag_divs:
        if tag.find("a"):
            hrefs.append(tag.find("a")["href"])
    #尋找最後一頁
    tag_a = soup.find_all("a", class_="btn wide")
    num = 1
    for a in tag_a:
        if a.contents[0] == '‹ 上頁':
            num = (int)((((a['href']).split('/')[3]).replace('index','')).replace('.html', ''))
    

    #取得剩下頁面的網址
    #設定8線程
    threadsNum = 8
    #新增Thread
    print(F"取得所有網址中，共{num}頁")
    tmp = (int)(num/threadsNum)
    thr = {}
    thr[0] = Thread(target=getUrl, kwargs={'start':1, 'end':tmp, 'url':url, 'hrefs': hrefs})
    for i in range(1,threadsNum-1):
        thr[i] = Thread(target=getUrl, kwargs={'start':tmp*i, 'end':tmp*(i+1), 'url':url, 'hrefs': hrefs})
    thr[threadsNum-1] = Thread(target=getUrl, kwargs={'start':tmp*(threadsNum-1), 'end':num, 'url':url, 'hrefs': hrefs})
    #thread開始
    for i in range(threadsNum):
        thr[i].start()
    #將thread加入完成檢查
    for i in range(threadsNum):
        thr[i].join()

    return hrefs

def getUrl(start, end, url, hrefs):
    for i in range(start, end):
        print(F"正在處理第{i}頁")
        r = requests.get(F'{url}/index{i}.html', cookies={"over18":"1"})
        soup = BeautifulSoup(r.text, "html5lib")
        tag_divs = soup.find_all("div", class_="title")
        for tag in tag_divs:
            if tag.find("a"):
                hrefs.append(tag.find("a")["href"])

def getContent(start, end, hrefs, page):
    for i in range(start, end):
        r = requests.get(url="http://ptt.cc"+hrefs[i], cookies={"over18":"1"})
        soup = BeautifulSoup(r.text, "html5lib")
        filename = hrefs[i].split("/")[-1]
        with open(os.path.join(os.path.dirname(__file__), page, F"{filename}.txt"), "w", encoding="utf8") as file1:
            #file1.write((soup.find_all("span", class_="article-meta-value"))[2].contents[0] + "\n")
            file1.write(soup.text)

#Plant
page = 'Plant'
#檢查是否已新增資料夾
if not os.path.exists(os.path.join(os.path.dirname(__file__), page)):
    os.mkdir(os.path.join(os.path.dirname(__file__), page))
"""
hrefs = getAllhref(page)
#儲存list
with open(os.path.join(os.path.dirname(__file__), F"{page}.hrefs.txt"), "w", encoding="utf8") as fs1:
    fs1.write(json.dumps(hrefs))
"""
#讀取list

with open(os.path.join(os.path.dirname(__file__), F"{page}.hrefs.txt"), "r", encoding="utf8") as fs1:
    hrefs = json.loads(fs1.read())

print(F"共{len(hrefs)}筆資料")
#getAllContent(hrefs, page)


#Agriculture
page = 'Agriculture'
#檢查是否已新增資料夾
if not os.path.exists(os.path.join(os.path.dirname(__file__), page)):
    os.mkdir(os.path.join(os.path.dirname(__file__), page))
"""
hrefs = getAllhref(page)
#儲存list
with open(os.path.join(os.path.dirname(__file__), F"{page}.hrefs.txt"), "w", encoding="utf8") as fs1:
    fs1.write(json.dumps(hrefs))
"""
#讀取list
with open(os.path.join(os.path.dirname(__file__), F"{page}.hrefs.txt"), "r", encoding="utf8") as fs1:
    hrefs = json.loads(fs1.read())

print(F"共{len(hrefs)}筆資料")

#getAllContent(hrefs, page)

"""
#Teacher's code
from nltk.corpus.reader import PlaintextCorpusReader
source_dir = "Gossiping/May 27/"
pcr = PlaintextCorpusReader(root=source_dir, fileids=".*\.txt")

from nltk.probability import FreqDist
fd = FreqDist(samples=pcr.words())
print(fd.most_common(n=100))

# 1. What are the most common words in your two PTT boards respectively? 
#    Do they correspond to what you have expected?
#    (Please upload your Python script to GitHub, and paste your GitHub link on the online text of eCourse homework.)


from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences
corpus = PathLineSentences(source_dir)#"Gossiping")

#model = Word2Vec(sentences=corpus, vector_size=100, window=5, min_count=1, workers=4)
#print(model.wv.most_similar(positive=['女性',"老公"], negative=['男性']))

# 2. By using the GenSim Word2Vec module, 
#    find a word x in an analogy like "man : king :: woman : x" (read: man is to king as woman is to x) 
#    in your PTT texts.
#    (Please upload your Python script to GitHub, and paste your GitHub link on the online text of eCourse homework.)
"""
