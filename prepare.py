#!/usr/bin/env python
#
import pandas as pd
import datetime
import numpy as np
import decimal
from os import listdir
import pprint

#parameters
verbose = False

#config
tempFileDir = '/Users/george/Downloads/'
claimsFile="MedicalClaimSummary.csv"
providerFile="existing-providers.csv"
bridgeFile="med-claims.pkl"

print "Using claims file: %s"% claimsFile
claims = pd.read_csv(tempFileDir + claimsFile,parse_dates=[2,7])
for col in ('Amount Billed','Deductible','Your Plan','Plan Discount','Your Responsibility','Paid at Visit/Pharmacy','You Owe'):
  claims[col] = claims[col].str.replace(r'$', '').astype(float)
claims['Visited Provider']=claims['Visited Provider'].str.upper()
  
claims.columns = [c.replace(' ', '_') for c in claims.columns]
claims=claims.sort_values(by='Date_Visited') #
providers=[x.upper() for x in claims.Visited_Provider.unique()]

existing = pd.read_csv(providerFile,sep='\t')
existing_providers= existing.PROVIDER.to_numpy()
found = [x in existing_providers for x in providers]

if not all(found): print ("Provider not found, create in MD first, then re export")
if not all(found):
  for i,p in enumerate(providers):
    if not found[i]:
      print p
if all(found):
  output = []
  merged = pd.merge(claims,existing,how="left", left_on='Visited_Provider',right_on='PROVIDER')

  def dateToInt(aDate):
    return(aDate.year * 10000)+(aDate.month*100)+aDate.day

  def add_entry(account,category,trans_date,value,description,patient):
    """formats an entry to be sent to Moneydance and appends it to the global output list
    value is the transaction value as a decimal number - eg 46.12
    trans_date is in pandas timestamp format, either the visit date or the date processed
    description is the claim number
    category is the MD category
    """
    val=int(round(100*value))
    dt=dateToInt(trans_date.date())
    oRow=[account,category,dt,val,description,patient]
    output.append(oRow)

      
  for i, row in merged.iterrows():
    claim_no="Claim #: "+row['Claim_Number']
    account= row['PARENT'] +":"+ row['Visited_Provider']
    patient=row['Patient_Name']
    visit_date=row['Date_Visited']
    process_date=row['Date_Processed']
    amt_billed=row['Amount_Billed']
    paid=-row['Your_Plan']
    adj=-row['Plan_Discount']
    cat_stub=row['CAT-STUB']
    if amt_billed != 0:
      add_entry(account,cat_stub+" Chg",visit_date,amt_billed,claim_no,patient)
    if adj!= 0:
      add_entry(account,cat_stub+" Ins Adj",process_date,adj,claim_no,patient)
    if paid!= 0:
      add_entry(account,cat_stub+" Ins Adj",process_date,paid,claim_no,patient)
  if verbose:
    for o in output:
      print (o)
  F=open(tempFileDir+bridgeFile,'wb')
  import pickle
  pickle.dump(output,F)
  F.close()
  print ("%d records written to %s"% (len(output),tempFileDir+bridgeFile))
