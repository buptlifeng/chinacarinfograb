#coding:utf-8
import requests
import random
import time
import sys
from bs4 import BeautifulSoup

#cookies we can use it safety in single thread
cookies = None

def loadkeys(fileName,outFile):
    f = open(fileName,mode = 'r')
    f1 = open(outFile,mode='w')
    curNo = 1
    for line in f.readlines():
        print line
        if len(line) > 0:
            key = line.strip('\n').strip('\r').strip(';')
            row = httpGetSearch(key)
            if row is None:
                f1.write(key + ';\n')
            else:
                f1.write(key + ';' + row.encode('utf-8') + ';\n')
            f1.flush()
            print line,'complete file ',curNo
            curNo = curNo + 1
            seconds = random.randint(2,6)
            time.sleep(seconds)
    f1.close()    
    f.close()

def httpGetSearch(key):
    host = "www.chinacar.com.cn"
    url = "http://" + host + "/sousuo.html"
    referer = host + "/sousuo.html?keys="+ key +"&order=&page=1"
    headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                #'Referer':referer,
                'Host':host,
                'Connection':'keep-alive'
                }
    payload={'keys':key,'order':'','page':'1'}
    global cookies
    if cookies:
        r = requests.get(url,headers=headers,params=payload,cookies=cookies)
    else:
        r = requests.get(url,headers=headers,params=payload)
    print r.status_code,r.url
    if r.status_code >= 400:
        seconds = random.randint(10,35)
        time.sleep(seconds)
        return
    cookies = r.cookies
    return parseHtml(r.text)

def httpGet(url):
    if len(url) > 0:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                   'Origin':'http://www.chinacar.com.cn',
                   'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
                   'Referer':'http://www.chinacar.com.cn/sousuo.html'
                  }
        global cookies
        if cookies:
            r = requests.get(url,headers=headers,cookies=cookies)
        else:
            r = requests.get(url,headers=headers)
        print r.status_code,r.url
        if r.status_code < 400:
            cookies = r.cookies
            soup = BeautifulSoup(r.text,'lxml')
            #the infomation maybe in these nodes
            div = soup.select_one('.xgcx_sm')
            if div is None:
                div = soup.select_one('#p_dhArrCon_1')
            if div is None:
                div = soup.select_one('.p_dhArrCon_1')
            if div:
                table = div.select_one('table')
                return parseTable(table)

#parse table contains a car info
def parseTable(table):
    #find all td to read information
    rows = table.select('td')
    if rows is None:
        return
    res = ''
    for row in rows:
        first_span = row.select_one('span')
        if first_span:
            desc = unicode(first_span.string)
        else:
            if row.string:
                desc = unicode(row.string)
            else:
                desc = unicode('')            
        if desc is None:
            res += ';'
        else:
            res += desc + ';' 
    return res

#the result html returned by sousuo.html
def parseHtml(text):
    if text is None:
        return
    soup = BeautifulSoup(text, 'lxml')
    divs = soup.select('.pro_title')
    if divs is None:
        return
    for div in divs:
        attr = div.select_one('a')
        href = attr['href']
        return httpGet(href)

def load_file_by_argv(argv):
    files = args[1]
    if files is None:
        print 'error with input file name,inst:','1.log,2.log',' use comma , to seprate files'
        return
    print 'output file name is:out_yourInputFileName,such as:out_1.log,out_2.log'
    return files.split(',')

if __name__ == "__main__":
    wait_read_files = load_file_by_argv(sys.argv)
    if wait_read_files is None:
    	for fileName in wait_read_files:
        	print 'ready to load file:',fileName
        	out_file = 'out_' + fileName
        	loadkeys(fileName,out_file)
        	print 'finish ',fileName,' reading,returned information in file:',out_file
        	time.sleep(6)
