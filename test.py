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
import datetime

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
        try:
            r = requests.get(url="http://ptt.cc"+hrefs[i], cookies={"over18":"1"})
            soup = BeautifulSoup(r.text, "lxml")
            meta_spans = soup.find_all("span", class_="article-meta-value")
            date_span = meta_spans[-1].contents[0]
            date_time_obj = datetime.datetime.strptime(date_span, '%a %b %d %H:%M:%S %Y')
            create_date = date_time_obj.strftime("%Y-%m-%d")
            title = soup.title

            filename = hrefs[i].split("/")[-1]
            folder_year = date_time_obj.year
            folder_month = date_time_obj.month

            #filepath = os.path.join(os.path.dirname(__file__), page, str(folder_year), str(folder_month), F"{filename}.txt")
            filepath = os.path.join(os.path.dirname(__file__), page, str(folder_year), F"{filename}.txt")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf8") as file1:
                file1.writelines(create_date)
                file1.writelines("\n")
                file1.writelines(title)
                file1.writelines("\n")
                file1.write(soup.text)
                print(F'{page}:{i}')
        except Exception as ex:
            print(ex)



def multiProSol(page):
    #檢查是否已新增資料夾
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "jieba")):
        os.mkdir(os.path.join(os.path.dirname(__file__), "jieba"))
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "jieba", page)):
        os.mkdir(os.path.join(os.path.dirname(__file__), "jieba", page))
    #設定16執行緒
    prosNum = 16
    fs = []
    jieba.load_userdict(os.path.join(os.path.dirname(__file__), "jieba.word.txt"))
    pool = Pool(prosNum)
    for root, dirs, files in os.walk(page):
        for name in files:
            if name.endswith(".txt"):
                fs.append([os.path.join(root, name)])

    pool.starmap(doSol, fs)
    print(F"{page}已完成")


    

def doSol(filename):
    with open(filename, "r", encoding="utf8") as fs1:
        contents = fs1.read()
        tagged_words = jieba.posseg.cut(contents)
        words = [word for word, pos in tagged_words if pos not in ['m']]
        os.makedirs(os.path.join("jieba", os.path.dirname(filename)), exist_ok=True)
        with open(os.path.join("jieba", filename), "w", encoding="utf8") as fs2:
            fs2.write(" ".join(words))
        print(filename)



def doFrequency(page):
    #讀取stopword
    f = open('stopwords-tw.txt', 'r', encoding="utf8")
    stopword = f.read()
    stopwords = stopword.split()
    f.close()
    dirs = os.listdir(os.path.join("jieba", page))
    for folder in dirs:
        print(F"處理{page}: {folder}")
        #讀取所有檔案
        pcr = PlaintextCorpusReader(root=os.path.join("jieba", page, folder), fileids=".*\.txt")
        #進行頻率分析
        fd = FreqDist(samples=pcr.words())
        #印出最常出現前500個詞
        tmp = fd.most_common(500)
        #過濾
        words = []
        for word in tmp:
            if(word[0] not in stopwords and word[0] not in printable):
                words.append(word)
        
        #words = [word for word,freq in tmp if word not in stopwords and word[0] not in printable]
        #儲存最常出現前200個詞
        
        with open(os.path.join("jieba", page, F"{folder}.txt"), "w", encoding="utf-8") as fs1:
            #fs1.write(json.dumps(words))
            for word in words:
                fs1.writelines(word[0] +"\t\t"+ str(word[1])+"\n")
        


def doAll(page):
    #檢查是否已新增資料夾
    if not os.path.exists(os.path.join(os.path.dirname(__file__), page)):
        os.mkdir(os.path.join(os.path.dirname(__file__), page))
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

    #對jieba斷詞做詞頻分析
    print("[對jieba斷詞做詞頻分析]")
    doFrequency(page)
    

if __name__ == "__main__":
    page = 'Plant'
    doAll(page)
    page = 'Agriculture'
    doAll(page)
