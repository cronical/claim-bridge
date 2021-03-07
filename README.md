## Import UHC claims data from csv

United health care lets you download claims data. We use the default name `MedicalClaimSummary.csv` for that data.

These utilities read that data and create transactions in Moneydance in the providers accounts.

![System Diagram](system-diagram.png)

There are 3 python programs, two of which run in Moneydance in the "MoneyBot Console".  

###Moneydance Set-up and Conventions

The expectation is that each medical provider has a liability account, which is named identically to the name that UHG uses.  These are expected to be sub-accounts of "Medical Providers".  Each of these accounts has a special comment (the only field available) to help the program set the correct category. In order to know the category to use, data is captured on the first row of the comment field of each provider

The first row of that field should contain the full category path and the non-unique part of the final element. So `X:Health:Maj-med:Tests:Test` is used for a test vendor such as Quest.  The program adds the last bit which is one of 'chg', 'ins adj' or 'ins pmt'.

### Steps

1. Remove `MedicalClaimSummary.csv` from the Downloads folder. So that browser does not add `(1)`. 

2. Download from he UHG claims portal.  Got to the Claims and Accounts -> Claims. Use the ability to create a filtered set of claims.   It will be named: `MedicalClaimSummary.csv`.   

   1. To select only certain dates it is probably better to filter on the website by date. Note - the download bottom is at the bottom of the claims page.
   2. Note, if you edit the file with Excel - watch out so the claim numbers don't get represented as exponential notation as excel saves them that way.  To select only certain dates it is probably better to filter on the website by date. Note - the download bottom is at the bottom of the claims page.

3. Display the list of providers downloaded with 

   ```bash
   ./dl_providers
   ```

4. Add any needed accounts in Moneydance

5. To prepare the list of providers currently in Moneydance, run `list-medical-providers.py` inside moneydance.  This puts a csv file in the working directory.

6. The main program is `prepare.py`. It looks for its input file in the Downloads folder and the provider list in the current directory.  It verifies that the providers match before writing the .pkl file. Ignores generic vendor, 'PHARMACY' and in process claims.

7. Back in Moneydance run `med-ins-bridge.py`











