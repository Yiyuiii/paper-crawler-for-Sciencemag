#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import requests
import os
import re

#global constrant
target="http://science.sciencemag.org/content/sci/%s/%s/"
tar_content="http://science.sciencemag.org/content/%s/%s"
tar_prefix="http://science.sciencemag.org"
first_year=1880
issue_per_vol=13
issue_1stinvol_known=(6415,362)
RESPONSE_FAILED="failed"

#function
def get_filename_webpath(text):
    index=text.rindex('/')+1
    return text[index:len(text)]

def filename_cln(text):
    return text.replace(".full.", ".")

def get_vol_issue(text):
    vol_index=text.index('content')+8
    issue_index=vol_index+4
    vol=text[vol_index:vol_index+3]
    issue=text[issue_index:issue_index+4]
    return (int(vol),int(issue))
    
def get_vol_issue_cur():
    source_url_pre="http://science.sciencemag.org/content/current"
    source_url=requests.get(source_url_pre).url
    return get_vol_issue(source_url)

def get_text(url):
    source=requests.get(url)
    if(source.status_code == requests.codes.ok):
        return source.text
    else:
        return RESPONSE_FAILED
    
def get_text_volissue(vol,issue):
    source_url=tar_content%(vol,issue)
    return get_text(source_url)

def get_text_cur():
    source_url_pre="http://science.sciencemag.org/content/current"
    return get_text(source_url_pre)

def get_tarloc_vol_issue(vol,issue,local):
    tar=target%(vol,issue)+"%d.full.pdf"
    loc=local%(vol,issue)+"%d.pdf"
    return (tar,loc)

#main download module
def down_direct(url,dest):
    if(os.path.exists(dest)):
        return False
    if(not os.path.exists(os.path.dirname(dest))):
        os.makedirs(os.path.dirname(dest)) 
    r=requests.get(url,stream=True)
    if(r.status_code == requests.codes.ok):
        with open(dest,"wb") as f:
            f.write(r.content)
    else:
        return False
    return True

def down_page(target,local,page):
    dest=local%(page)
    if(os.path.exists(dest)):
        return True
    url=target%(page)
    return down_direct(url,dest)

def down_searchbywebcontent_findnext(text,index):
    temp=text.find('title="PDF"',index)
    if(temp==-1): 
        return (False,'',-1)
    left=text.rfind('<a href="',0,temp)+9
    right=text.find('.pdf"',left)+4
    return (True,tar_prefix+text[left:right],temp+1)

def down_searchbywebcontent(text,local):
    index=0
    while(index!=-1):
        (flag,target,right)=down_searchbywebcontent_findnext(text,index)
        if(flag):
            (vol,issue)=get_vol_issue(target)
            filename=get_filename_webpath(target)
            filename=filename_cln(filename)
            if(down_direct(target,local%(vol,issue)+filename)):
                print("%s - finished"%(filename))
            else:
                print("%s - canceled"%(filename))
        index=right

#depend on down_searchbywebcontent()
def down_searchbyvolissue(vol,issue,local):
    text=get_text_volissue(vol,issue)
    down_searchbywebcontent(text,local)

def get_volissuelist():
    source_url="http://science.sciencemag.org/content/by/year/%d"
    #year=2018
    while(True):
        url=source_url%(year)
        text=get_text(url)
        if(text==RESPONSE_FAILED):
            break
        result=re.findall(r">Vol ([0-9]*), Iss ([0-9]*)<",text)
        #sort
        #merge
        #save
        year-=1
    return vol

