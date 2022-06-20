#!/usr/bin/env python
#
import json
from os import listdir
import yaml

import argparse
from dateutil.parser import parse as date_parse
import pandas as pd
import numpy as np
import decimal
import pprint

#parameters
verbose = False

#config
tempFileDir = '/Users/george/Downloads/'
bridgeFileDir = '/Users/george/argus/med-ins/'
claimsFile="MedicalClaimSummary.csv"
providerFile="existing-providers.csv"
bridgeFile="med-claims.pkl"
last_processed_file='last_processed.json'
diagnostic_data_file='diagnostic_data.csv'
valid_bases='valid_bases.yaml'

with open(last_processed_file, 'r') as f:
  acct_dates=json.load(f)

parser=argparse.ArgumentParser('This program prepares UHC medical expense data for Moneydance')
parser.add_argument('account',choices=list(acct_dates.keys()),help='provide the account identifier to process')
args=parser.parse_args()
acct=args.account
last_processed=acct_dates[acct]
print("Account %s was last processed on %s"%(acct,last_processed))
print ("Using claims file: %s"% claimsFile)
claims = pd.read_csv(tempFileDir + claimsFile,dtype={'Claim_Number' : 'str'},parse_dates=[2,8])
for col in ('Amount Billed','Deductible','Your Plan','Plan Discount','Your Responsibility','Paid at Visit/Pharmacy','You Owe'):
  claims[col] = claims[col].str.replace(r'$', '').str.replace(r',', '').astype(float)
claims['Visited Provider']=claims['Visited Provider'].str.upper()
  
claims.columns = [c.replace(' ', '_') for c in claims.columns]
claims=claims.sort_values(by='Date_Visited') #
claims=claims.loc[claims['Claim_Status']!='In Process'] # ignore inprocess items

ld=date_parse(last_processed)
claims = claims.loc[claims.Date_Processed > ld]
print ("Ignoring claims on or before {}".format(last_processed))

providers=[x.upper() for x in claims.Visited_Provider.unique()]

# ability to handle data errors on the names from the insurer:
import json
with open('alias.json') as f: alias=json.load(f)
ak= alias.keys()
for x in range(len(providers)): 
  p=providers[x]
  if p in ak:
    claims.loc[claims.Visited_Provider == p,'Visited_Provider']=alias[p]
    print ("Substituted alias {} for {}".format(alias[p],p))
providers=[x.upper() for x in claims.Visited_Provider.unique()]
existing = pd.read_csv(bridgeFileDir+providerFile,sep='\t')
existing_providers= existing.PROVIDER.to_numpy()
existing_providers=np.append(existing_providers,['PHARMACY']) # generic vendor, we will ignore later
found = [x in existing_providers for x in providers]

if not all(found): print ("Provider(s) not found, create in MD first, then re export")
if not all(found):
  for i,p in enumerate(providers):
    if not found[i]:
      print (p)
if all(found):
  merged = pd.merge(claims,existing,how="left", left_on='Visited_Provider',right_on='PROVIDER')
  with open(valid_bases,'r') as f:
    bases=yaml.load(f,yaml.CLoader)
  bad_bases=[x not in bases for x in merged['CAT-STUB'].to_list()]
  if any(bad_bases):
    print ("Not all categories are valid")
    print (merged.loc[bad_bases,['Visited_Provider','Date_Visited','CAT-STUB']])
    quit()
  print (claims)
  output = []
  merged.to_csv(diagnostic_data_file)
  print ('Data table written to %s, in case you need it' % diagnostic_data_file)
  if 0 < claims.shape[0]: # update the last processed date if there are any remaining rows
    last_processed = '{}\n'.format(claims['Date_Processed'].max())[0:10] # its UHC's process date.

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
    if row['Visited_Provider'] != 'PHARMACY':
      claim_no="Claim #: "+row['Claim_Number']
      account= row['GRANDPARENT']+":"+row['PARENT'] +":"+ row['Visited_Provider']
      patient=row['Patient_Name']
      visit_date=row['Date_Visited']
      process_date=row['Date_Processed']
      amt_billed=row['Amount_Billed']
      paid=-row['Your_Plan']
      adj=-row['Plan_Discount']
      cat_stub=row['CAT-STUB']
      if pd.isna(cat_stub):
        print('Provider %s does not have an account stub in its comment field. Skipping...'%row['Visited_Provider'])
        continue
      if amt_billed != 0:
        add_entry(account,cat_stub+" Chg",visit_date,amt_billed,claim_no,patient)
      if adj!= 0:
        add_entry(account,cat_stub+" Ins Adj",process_date,adj,claim_no,patient)
      if paid!= 0:
        add_entry(account,cat_stub+" Ins Pmt",process_date,paid,claim_no,patient)
  if verbose:
    for o in output:
      print (o) 
  F=open(bridgeFileDir+bridgeFile,'wb')
  import pickle
  pickle.dump(output,F,protocol=2)
  F.close()
  print ("%d records written to %s"% (len(output),bridgeFileDir+bridgeFile))
  with open(last_processed_file,'w') as f:
    acct_dates[acct]=(last_processed)
    json.dump(acct_dates,f)
    print("Last processed date written to %s"% last_processed)
