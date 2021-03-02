#!/usr/bin/env python
# to be run inside Moneydance
#assumes accounts are not deeper than 3rd level in hierarch
from com.infinitekind.moneydance.model import *
from com.infinitekind.moneydance.model import AccountUtil, Account
book = moneydance.getCurrentAccountBook()
root = book.getRootAccount()

filename="/Users/george/argus/med-ins/existing-providers.csv"
count=0

with open(filename, 'w') as csvfile:
  csvfile.write('%s\t%s\t%s\t%s\n' % ("PROVIDER","PARENT","GRANDPARENT","CAT-STUB"))
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
            gpa = pa.getParentAccount() # moved these under liabilities
            csvfile.write( '%s\t%s\t%s\t%s\n'% (na,pa.getAccountName(),gpa.getAccountName(),cmt))
            count= count+1
  csvfile.close()
print ("%d items " % count)

