#!/usr/bin/env python
# to be run inside Moneydance
from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import AccountUtil, Account
book = moneydance.getCurrentAccountBook()
root = book.getRootAccount()

#print Account.AccountType.valueOf("INVESTMENT")

filename="/Users/george/argus/med-ins/existing-providers.csv"
count=0

with open(filename, 'w') as csvfile:
  csvfile.write('%s\t%s\t%s\n' % ("PROVIDER","PARENT","CAT-STUB"))
  for acct in AccountUtil.getAccountIterator(root):
    na = acct.getAccountName()
    ty = acct.getAccountType()
    cmt=acct.getComment().strip()
    if len(cmt)>0:
      cmt=cmt.splitlines()[0]
    inact = acct.getAccountIsInactive()
    if not inact :
      if ty.code() == Account.AccountType.LIABILITY.code():
        pa = acct.getParentAccount()
        if not pa.getAccountIsInactive():
          if pa.getAccountName() == "Medical Providers":
            csvfile.write( '%s\t%s\t%s\n'% (na,pa.getAccountName(),cmt))
            count= count+1
  csvfile.close()
print "%d items " % (count)

