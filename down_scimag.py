#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import requests
import shelve
import time
import os
import re

class websitecrawler(object):
    
    tar_prefix="http://science.sciencemag.org"
    target="http://science.sciencemag.org/content/sci/%s/%s/"
    tar_content="http://science.sciencemag.org/content/%s/%s"
    url_source_cur="http://science.sciencemag.org/content/current"
    url_list="http://science.sciencemag.org/content/by/year/%d"
    format_dict_volissue=r">Vol (.*), Iss (.*)<"
    format_dumb_filename=(".full.", ".")
    format_url_vol_issue="content/([^/]*)/([^/]*)"
    year_first=1880
    num_issue_per_vol=13
    num_issue_1stinvol_known=(6415,362)
    RESPONSE_FAILED="failed"
    dir_dat='data\\'
    filename_dat='sciencemag'
    path_dat='data\\sciencemag' #auto created in __init__
    dict_volissue={}
    
    def __init__(self):
        self.path_dat=self.dir_dat+self.filename_dat
        self.load_data()
        
    def __enter__(self):
        self.__init__()
        return self
        
    def __exit__(self, type, value, trace):
        self.save_data()
        
    #function
    def save_data(self):
        if(not os.path.exists(self.dir_dat)):
            os.makedirs(os.path.dirname(self.dir_dat)) 
        dbase = shelve.open(self.path_dat)
        dbase['dict_volissue']=self.dict_volissue
        dbase.close()
        
    def load_data(self):
        if(os.path.exists(self.path_dat+'.dat')):
            dbase = shelve.open(self.path_dat)  
            #len(dbase)
            self.dict_volissue=dbase['dict_volissue']
        
    def get_year_cur(self):
        return int(time.strftime('%Y',time.localtime()))
    
    def get_filename_webpath(self,text):
        index=text.rindex('/')+1
        return text[index:len(text)]
    
    def filename_cln(self,text):
        return text.replace(self.format_dumb_filename[0], self.format_dumb_filename[1])
    
    def get_vol_issue(self,url):
        result=re.findall(self.format_url_vol_issue,url)
        if(len(result)==0):
            return (-1,-1)
        (vol,issue)=result[len(result)-1]
        return (vol,issue)
        
    def get_vol_issue_cur(self):
        source_url=requests.get(self.url_source_cur).url
        return self.get_vol_issue(source_url)
    
    def get_text(self,url):
        source=requests.get(url)
        if(source.status_code == requests.codes.ok):
            return source.text
        else:
            return self.RESPONSE_FAILED
        
    def get_text_volissue(self,vol,issue):
        source_url=self.tar_content%(str(vol),str(issue))
        return self.get_text(source_url)
    
    def get_text_cur(self):
        return self.get_text(self.url_source_cur)

    #outdated
    def get_tarloc_for_page(self,vol,issue,local):
        tar_page=self.target%(str(vol),str(issue))+"%d.full.pdf"
        loc_page=local%(str(vol),str(issue))+"%d.pdf"
        return (tar_page,loc_page)
    
    #main download module
    #returns string
    def down_direct(self,url,dest):
        if(os.path.exists(dest)):
            return 'already exist'
        if(not os.path.exists(os.path.dirname(dest))):
            os.makedirs(os.path.dirname(dest)) 
        try:
            r=requests.get(url,stream=True, timeout=(10,20))
    #        timer = Timer(interval, time_out)
            if(r.status_code == requests.codes.ok):
#                timer.start()
#                res = func(*args, **kwargs)
#                timer.cancel()
                with open(dest,"wb") as f:
                    f.write(r.content)
            else:
                return str(r.status_code)
        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError
                ) as e:
            if(os.path.exists(dest)):
                os.remove(dest)
            return str(e)
        else:
            pass
        return 'finished'
    
    def down_page(self,tar_page,loc_page,page):
        dest=loc_page%(page)
        if(os.path.exists(dest)):
            return True
        url=tar_page%(page)
        return self.down_direct(url,dest)
    
    def down_searchbywebcontent_findnext(self,text,index):
        temp=text.find('title="PDF"',index)
        if(temp==-1): 
            return (False,'',-1)
        left=text.rfind('<a href="',0,temp)+9
        right=text.find('.pdf"',left)+4
        return (True,self.tar_prefix+text[left:right],temp+1)
    
    def down_searchbywebcontent(self,text,local):
        index=0
        while(index!=-1):
            (flag,target,right)=self.down_searchbywebcontent_findnext(text,index)
            if(flag):
                (vol,issue)=self.get_vol_issue(target)
                filename=self.get_filename_webpath(target)
                filename=self.filename_cln(filename)
                print("%s - "%(filename),end='')
                dest=local%(str(vol),str(issue))+filename
                print(self.down_direct(target,dest))
            index=right
    
    #Depend on down_searchbywebcontent()
    def down_searchbyvolissue(self,vol,issue,local):
        text=self.get_text_volissue(vol,issue)
        self.down_searchbywebcontent(text,local)
    
    #recommended
    def down_issues(self,issues,local):
        for issue in issues:
            issue=int(issue)
            if(issue in self.dict_volissue):
                vol=self.dict_volissue[issue]
            else:
                print('Cannot find Issue %d in I-V dictionary.'%(issue))
                continue
            print('Downloading Issue %d.'%(issue))
            self.down_searchbyvolissue(vol,issue,local)
        
    #This takes a while
    def get_volissuelist(self):
        year=self.get_year_cur()
        print('Started searching vol-issue dictionary on website.','This takes a while.')
        while(True):
            #print('Current:%d'%year,end='\r')
            print('Current:%d'%year)
            url=self.url_list%(year)
            text=self.get_text(url)
            if(text==self.RESPONSE_FAILED):
                print(text)
            else:
                result=re.findall(self.format_dict_volissue,text)
                for (vol,issue) in result:
                    self.dict_volissue[int(issue)]=int(vol)
            #TODO:optimize
            if(year==self.year_first):
                break
            year-=1
        return self.dict_volissue

    def update_volissuelist(self):
        m=max(self.dict_volissue)
