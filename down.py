#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import down_scimag as down

local="E:\\BaiduYunDownload\\paper\\science\\%d\\%d\\"

(vol,issue)=down.cur_vol_issue()
#issue-=1

text=down.get_text(vol,issue)
down.down_searchbywebsite(text,local)
