#!/usr/bin/env python
# Python script to be run in Moneydance 

from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import ParentTxn
from com.infinitekind.moneydance.model import SplitTxn

import sys
import time
import pickle
import java.util.ArrayList

fileDir = "/Users/george/Downloads/"
bridgeFile = 'med-claims.pkl'
doSave = True # False allows dry run

# get the input data
with open(fileDir+bridgeFile,'rb') as F:
  input = pickle.load(F)
print ("%d rows read"% len(input))

# peculiar code to set tags. otxn can be the other side or a split
def markWithTag(otxn,modTag):
  tags = otxn.getKeywords()
  if modTag not in tags:
    jtags =java.util.ArrayList(tags)
    jtags.add(modTag)
    otxn.setKeywords(jtags)

# rows are [account,category,dt,val,description,patient]
book = moneydance.getCurrentAccountBook()
i=0
for row in input:
  if i<2:
    acct = book.getRootAccount().getAccountByName(row[0])
    cat =book.getRootAccount().getAccountByName(row[1])
    if cat is None:
      raise ValueError ('No such category: %s' % row[1])

    parent= ParentTxn(book)
    parent.setAccount(acct)
    parent.setDateInt(row[2])
    parent.setTaxDateInt(row[2]) # otherwise it shows zeros
    parent.setDescription(row[4])
    parent.setMemo("From med-ins-bridge")
    
    split=SplitTxn.makeSplitTxn(parent,row[3],row[3],1,cat,row[4],0,parent.getStatus())
    markWithTag(split,row[5])
    parent.addSplit(split)
    print (parent)
    i=i+1
    if doSave:
      parent.syncItem()
 
  
  
