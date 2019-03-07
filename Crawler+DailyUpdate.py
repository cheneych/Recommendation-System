
#from selenium import webdriver
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
url = 'ftp://ftp.ncbi.nlm.nih.gov/pubmed/updatefiles/pubmed19n0973.xml.gz'
#browser = webdriver.Chrome("D:/anaconda/Scripts/chromedriver.exe")


import csv
import ftplib
import gzip
import os
import platform
import re
import time
from ftplib import FTP

import pymongo


def judge_os():
    os_platfrom = platform.platform()
    if os_platfrom.startswith('Darwin'):
        print('this is mac os system')
        os.system('ls')
    elif os_platfrom.startswith('Window'):
        print('this is win system')
        os.system('dir')

def ftpconnect():
    ftp_server = 'ftp.ncbi.nlm.nih.gov'
    ftp = FTP()
    ftp.set_debuglevel(2)
    ftp.connect(ftp_server,21)
    ftp.login()
    #print(ftp.getwelcome())
    return ftp

def downloadfile():
    bufsize = 1024
    ftp = ftpconnect()

    if count < 1000:
        remotepath = "/pubmed/updatefiles/pubmed19n" + '0'+ str(count) + ".xml.gz"
        localpath = "pubmed19n" + '0'+  str(count) + ".xml.gz"
    else:
        remotepath = "/pubmed/updatefiles/pubmed19n" + str(count) + ".xml.gz"
        localpath = "pubmed19n" + str(count) + ".xml.gz"

    fp = open(localpath,'wb')
    try:
        ftp.retrbinary('RETR ' + remotepath,fp.write,bufsize)
    except ftplib.error_perm:
        print(".......Finish upgrade.......")
        ftp.set_debuglevel(0)
        fp.close()
        ftp.quit()
        os.remove(localpath) #delete
        exit(0)
 
    ftp.set_debuglevel(0)
    fp.close()
    ftp.quit()
    if count < 1000:
        Decompress("pubmed19n" + '0' + str(count) + ".xml.gz")
        classification(open("pubmed19n" + '0' + str(count) + ".xml").read())
        
    else:
        Decompress("pubmed19n" + str(count) + ".xml.gz")
        classification(open("pubmed19n" + str(count) + ".xml").read())
    return 1

def Decompress( file_name):
    f_name = file_name.replace(".gz", "")
    # 获取文件的名称，去掉
    g_file = gzip.GzipFile(file_name)
    # 创建gzip对象
    open(f_name, "wb").write(g_file.read())
    # gzip对象用read()打开后，写入open()建立的文件里。
    g_file.close()

def classification (fp):

    csvFile = open("Update1.csv","a") # a =  zhui jia 
    writer = csv.writer(csvFile)
    #article
    reg = r"<PubmedArticle>(.+?)</PubmedArticle>"
    #pmid
    reg0 = r'<PMID Version="1">(.{8})'
    #Abstract
    reg1 = r"<AbstractText>(.+?)</AbstractText>"
    #Title
    reg2 = r"<ArticleTitle>(.+?)</ArticleTitle>"
    #Journal
    reg3 = r"<Title>(.+?)</Title>"
    #Author
    #just has last name
    reg4 = r"<LastName>(.+?)</LastName>"
    reg5 = r"<Initials>(.+?)</Initials>"
    wordreg0 = re.compile(reg0)
    wordreg1 = re.compile(reg1)
    wordreg2 = re.compile(reg2)
    wordreg3 = re.compile(reg3)
    #wordreg4 = re.compile(reg4)
    #wordreg5 = re.compile(reg5)


    list0 = re.findall(wordreg0, fp)
    list1 = re.findall(wordreg1, fp)
    list2 = re.findall(wordreg2,fp)
    list3 = re.findall(wordreg3,fp)
    #list4 = re.findall(wordreg4,fp) 
    #list5 = re.findall(wordreg5, fp)

    #if list0 != [] and list1 != [] and list2 != [] and list3 != []:
    #    writer.writerows([list0, list1, list2, list3])
    
    for i in range(len(list0)):
        try:
            #writer.writerow([list0[i], list1[i], list2[i], list3[i]])
            with open("journal_abbr.txt", 'r') as foo:
                line = foo.readlines()
                if list3[i]+'\n' in line:
                    post_1 = posts.find_one_and_update({'ID': list0[i]}, {'$set': {'Abstract': list1[i]}})
                    post_2 = posts.find_one_and_update({'ID': list0[i]}, {'$set': {'Abstract': list2[i]}})
                    post_3 = posts.find_one_and_update({'ID': list0[i]}, {'$set': {'Abstract': list3[i]}})
                    if post_1 == None:
                        print("#INSERT")
                        post_1 = posts.insert_one({'ID': list0[i] , 'Abstract': list1[i], 'Title': list2[i], 'Journal': list3[i]})
                        continue
        except IndexError:
            break; 
    







if __name__ == '__main__':
    count = 1074  # first xml number
    connection = pymongo.MongoClient('127.0.0.1',27017)
    db = connection.local
    posts = db.tset  
    while(True):
        print("......Begin upgrade......")
        while (True):
            downloadfile()
            count = count + 1
        time.sleep(86400)
    
    #classification(open("pubmed19n1074.xml").read())

    #print( time.strftime("%Y/%m/%d ",time.localtime()))
