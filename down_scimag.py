#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import print_function

import numpy as np
import requests
import os

target="http://science.sciencemag.org/content/sci/%s/%s/"
tar_content="http://science.sciencemag.org/content/%s/%s"
tar_prefix="http://science.sciencemag.org"

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
    
def cur_vol_issue():
    source_url_pre="http://science.sciencemag.org/content/current"
    source_url=requests.get(source_url_pre).url
    return get_vol_issue(source_url)

def get_text(vol,issue):
    source_url_pre=tar_content%(vol,issue)
    source=requests.get(source_url_pre)
    if(source.status_code == requests.codes.ok):
        return source.text
    else:
        return "Failed"

def cur_text():
    source_url_pre="http://science.sciencemag.org/content/current"
    source=requests.get(source_url_pre)
    if(source.status_code == requests.codes.ok):
        return source.text
    else:
        return "Failed"

def init_vol_issue(vol,issue,local):
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

def down_searchbywebsite_findnext(text,index):
    temp=text.find('title="PDF"',index)
    if(temp==-1): 
        return (False,'',-1)
    left=text.rfind('<a href="',0,temp)+9
    right=text.find('.pdf"',left)+4
    return (True,tar_prefix+text[left:right],temp+1)

def down_searchbywebsite(text,local):
    index=0
    while(index!=-1):
        (flag,target,right)=down_searchbywebsite_findnext(text,index)
        if(flag):
            (vol,issue)=get_vol_issue(target)
            filename=get_filename_webpath(target)
            filename=filename_cln(filename)
            if(down_direct(target,local%(vol,issue)+filename)):
                print("%s - finished"%(filename))
            else:
                print("%s - canceled"%(filename))
        index=right

#not conpleted        
def down_searchbynum(target,local):
    page=650
    for p in range(page,500,-1):
        down_page(target,local,p)
    for n in range(page,800):
        down_page(target,local,p)