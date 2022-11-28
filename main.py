import requests
from bs4 import BeautifulSoup
import os
import json
import jieba.posseg
from threading import Thread
from multiprocessing import Pool
from nltk.corpus.reader import PlaintextCorpusReader
from nltk.probability import FreqDist
from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences
from string import printable

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
    soup = BeautifulSoup(r.text, "lxml")
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
        soup = BeautifulSoup(r.text, "lxml")
        tag_divs = soup.find_all("div", class_="title")
        for tag in tag_divs:
            if tag.find("a"):
                hrefs.append(tag.find("a")["href"])

def getContent(start, end, hrefs, page):
    for i in range(start, end):
        r = requests.get(url="http://ptt.cc"+hrefs[i], cookies={"over18":"1"})
        soup = BeautifulSoup(r.text, "lxml")
        filename = hrefs[i].split("/")[-1]
        with open(os.path.join(os.path.dirname(__file__), page, F"{filename}.txt"), "w", encoding="utf8") as file1:
            #file1.write((soup.find_all("span", class_="article-meta-value"))[2].contents[0] + "\n")
            file1.write(soup.text)
            print(F'{page}:{i}')



def multiProSol(page):
    #檢查是否已新增資料夾
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "jieba")):
        os.mkdir(os.path.join(os.path.dirname(__file__), "jieba"))
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "jieba", page)):
        os.mkdir(os.path.join(os.path.dirname(__file__), "jieba", page))
    #設定12執行緒
    prosNum = 16
    dirs = os.listdir(page)
    fs = []
    pool = Pool(prosNum)
    for filename in dirs:
        fs.append((filename, page))
    pool.starmap(doSol, fs)
    print(F"{page}已完成")


    

def doSol(filename, page):
    with open(os.path.join(page, filename), "r", encoding="utf8") as fs1:
        contents = fs1.read()
        tagged_words = jieba.posseg.cut(contents)
        words = [word for word, pos in tagged_words if pos not in ['m']]
        with open(os.path.join("jieba", page, filename), "w", encoding="utf8") as fs2:
            fs2.write(" ".join(words))
        print(filename)



def doFrequency(page):
    #讀取stopword
    f = open('stopwords-tw.txt', 'r', encoding="utf8")
    stopword = f.read()
    stopwords = stopword.split()
    f.close()
    #讀取所有檔案
    pcr = PlaintextCorpusReader(root=os.path.join("jieba", page), fileids=".*\.txt")
    #進行頻率分析
    fd = FreqDist(samples=pcr.words())
    #印出最常出現前100個詞
    tmp = fd.most_common(n=200)
    #過濾
    words = [word for word,freq in tmp if word not in stopwords and word[0] not in printable]
    print(words)
    #儲存最常出現前100個詞
    with open(F"{page}.freqTop100.txt", "w", encoding="utf-8") as fs1:
        fs1.write(json.dumps(words))

def w2v(page, a, b, c):
    #讀入所有檔案
    corpus = PathLineSentences(os.path.join("jieba", page))
    model = Word2Vec(sentences=corpus, vector_size=100, window=5, min_count=1, workers=4)
    #印出結果
    tmp = model.wv.most_similar(positive=[a,b], negative=[c])
    print(tmp)
    with open(F"{page}.w2v.txt", "w", encoding="utf-8") as fs1:
        fs1.write(json.dumps(tmp))


def doAll(page, a, b, c):
    #檢查是否已新增資料夾
    if not os.path.exists(os.path.join(os.path.dirname(__file__), page)):
        os.mkdir(os.path.join(os.path.dirname(__file__), page))
    """
    #取得所有連結
    print("[獲得所有連結]")
    hrefs = getAllhref(page)
    #儲存所有連結
    print("[儲存所有連結]")
    with open(os.path.join(os.path.dirname(__file__), F"{page}.hrefs.txt"), "w", encoding="utf8") as fs1:
        fs1.write(json.dumps(hrefs))
    #讀取所有連結
    print("[讀取所有連結]")
    with open(os.path.join(os.path.dirname(__file__), F"{page}.hrefs.txt"), "r", encoding="utf8") as fs1:
        hrefs = json.loads(fs1.read())
    print(F"共{len(hrefs)}筆資料")
    #取得所有連結資料並儲存
    print("[取得所有連結資料並儲存]")
    getAllContent(hrefs, page)
    
    #前面的資料做jieba斷詞並儲存
    print("[前面的資料做jieba斷詞並儲存]")
    multiProSol(page)
    """
    #對jieba斷詞做詞頻分析
    print("[對jieba斷詞做詞頻分析]")
    doFrequency(page)
    #a對b如同c對什麼?
    print("[a對b如同c對什麼?]")
    w2v(page, a, b, c)


if __name__ == "__main__":
    page = 'Plant'
    doAll(page, "植物", "作者", "踢踢")
    page = 'Agriculture'
    doAll(page, "農業", "台灣", "農民")
