#!/usr/bin/python
# coding=utf-8
import os, urllib, urllib2, urlparse, HTMLParser
#下载功能
        #以下代码改自：http://www.cnpythoner.com/post/pythonurldown.html
def url2name(url):
    return os.path.basename(urlparse.urlsplit(url)[2])

def reporthook(count,block_size,total_size):
    print '\x0D','已下载：'+'%d MB' % int(count*block_size/(1024.0*1024.0)),#'%02.1f%%' % (100*count*block_size/total_size),
      
def download(url, destDir = None, localFileName = None):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url:
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    localName = urllib2.unquote(localName)
    if localFileName:
        # we can force to save the file as specified name
        localName = localFileName
    elif destDir:
        localName = destDir + localName
    urllib.urlretrieve(r.url,localName,reporthook)
    print ''
    
class My12Parser(HTMLParser.HTMLParser):
    def __init__(self):
        self.downloadList = []
        self.nameList = []
        HTMLParser.HTMLParser.__init__(self)
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            isDownloadLink = False
            for name,value in attrs:
                if name == 'class' and value == 'download_link':
                    isDownloadLink = True
                    break
            if isDownloadLink:
                for name,value in attrs:
                    if name == 'href':
                        self.downloadList.append(str(value))
                    if name == 'title':
                        self.nameList.append(str(value))
                        
    def get_downloadlist(self):
        return self.downloadList

    def get_namelist(self):
        return self.nameList
#End

#搜索功能
def search(key):
    '根据传入的参数key在12club上进行搜索'
    url12 = r'http://12club.nankai.edu.cn'
    urlreq = urllib.urlopen(url12)
    sc = urlreq.read()
    sc = sc[sc.find('authenticity_token')+5:]
    sc = sc[sc.find('authenticity_token'):]
    sc = sc[sc.find(r'value="'):]
    sc = sc[sc.find(r'"')+1:]
    token = sc[:sc.find(r'"')]
    params = {
        'utf8':'?',
        'authenticity_token':token,
        'keyword':key
        }
    params = urllib.urlencode(params)
    r = urllib.urlopen(url12+r'/search', params)
    sc = r.read()
    return sc

class SearchParser(HTMLParser.HTMLParser):
    '搜索结果的parser'
    def __init__(self):
        self.linkList = []
        self.nameList = []
        self.isTag = False
        self.tags = []
        self.taglist = []
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'a' :
            names = [name for name, value in attrs]
            values = [value for name, value in attrs]
            if 'href' in names and 'class' not in names and r'/programs/' in values[names.index('href')]:
                self.linkList.append(values[names.index('href')])
                self.nameList.append(values[names.index('title')])
        elif tag == 'div' and [('class', 'tag_list')] == attrs:
            self.isTag = True
            
    def handle_data(self,data):
        if self.isTag and data.strip():
            self.tags.append(data)
            
    def handle_endtag(self,tag):
        if tag == 'div' and self.isTag:
            self.isTag = False
            self.taglist.append(self.tags)
            self.tags = []

    def get_linklist(self):
        return self.linkList

    def get_namelist(self):
        return self.nameList
    
    def get_taglist(self):
        return self.taglist

def showSearchResult(codes):
    '显示搜索结果并且让用户选择想要的下载结果'
    parser = SearchParser()
    parser.feed(codes)
    links = parser.get_linklist()
    names = parser.get_namelist()
    tags = parser.get_taglist()
    parser.close()
    if names:
        i = 0
        print '搜索结果如下所示:'
        for name in names:
            i += 1
            print i,'. ',name
            print '标签：',','.join(tags[i-1][1:]), '\n'
        i = int(raw_input('请问您选择下载哪一个(请输入对应编号):'))
        return links[i-1]
    else:
        print '没有搜索到结果,您必须重新输入关键词!'
#搜索功能End

if __name__ == '__main__':
    addr = 'http://12club.nankai.edu.cn'
    print '欢迎来到12下载器，请根据提示进行搜索或者下载，如有卖萌提示，作者概不负责！'
    
    while True:
        choose = raw_input('本程序有如下功能：\n1.搜索并下载某部动画的全集\n2.根据动画id下载该动画现有全集\n请输入您选择的功能：')
        if choose == '1':
            while True:
                key = raw_input('请输入您想查询的关键词：')
                searchResult = search(key)
                searchResult = searchResult
                url = showSearchResult(searchResult)
                if url:
                    break
            break
        elif choose == '2':
            cartoonid = raw_input("你想下载的动画的ID(在对应页面的地址栏中最后找，为若干数字，注意别输错了，否则程序会有错哦~)：")
            url = addr+'/programs/'+cartoonid
            break
        else:
            print r'输入的有错啊！，从新来过吧！'

    while True:
        yesorno = raw_input("要把动画下载到当前文件夹内么？下载到当前文件夹请输y按回车，下载到其他文件夹请输入n按回车：")
        if yesorno == 'y':
            dest_dir = None
            break
        elif yesorno == 'n':
            while True:
                dest_dir = raw_input("输入您想把动画下载到哪里(即文件绝对路径，若目录不存在，将新建)：")
                if not os.path.isdir(dest_dir):
                    try:
                        print '提示：目录不存在，将尝试新建...',
                        os.makedirs(dest_dir)
                        print '新建成功！'
                        break
                    except:
                        print '尝试新建的时候发生了错误！有可能因为您给的目录有问题，重新输入吧！',
                        continue
                else:
                    break
            break
        else:
            print r"这位绅士，拜托输入y或n，不要随便把什么东西都放到人家里面来啦~（＃￣▽￣＃），again，",

    sourcecode = urllib2.urlopen(url).read()
    parser = My12Parser()
    parser.feed(sourcecode)
    downlist = parser.get_downloadlist()
    namelist = parser.get_namelist()
    i=1
    for downlink in downlist:
        print '开始下载' , namelist[i-1], '，请稍等，请不要退出程序，否则正在下载的动画将无效。下载完成将提示......'
        if dest_dir:
            download('http://12club.nankai.edu.cn'+downlink,dest_dir)
        else:
            download('http://12club.nankai.edu.cn'+downlink)
        print namelist[i-1], '下载完毕！'
        i += 1
    raw_input('下载完成！请按下回车关闭程序！')
