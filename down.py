#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from down_scimag import *

local="E:\\GitHub Repository\\paper\\science\\%d\\%d\\"

(vol,issue)=get_vol_issue_cur()
#issue-=1
down_searchbyvolissue(vol,issue,local)
