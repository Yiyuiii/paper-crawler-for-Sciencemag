#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from down_scimag import websitecrawler
local="E:\\GitHub Repository\\paper\\science\\%s\\%s\\"

with websitecrawler() as wcr:
    wcr.down_issues(range(6401,6411),local)
#    (vol,issue)=wcr.get_vol_issue_cur()
#    wcr.down_searchbyvolissue(vol,issue,local)

#with websitecrawler() as wcr:
#    print(wcr.get_volissuelist())