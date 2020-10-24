## Import UHC claims data from csv

United health care lets you download claims data. We use the default name `MedicalClaimSummary.csv` for that data.

These utilities read that data and create transactions in Moneydance in the providers accounts.

![System Diagram](system-diagram.png)

There are 3 python programs, two of which run in Moneydance in the "MoneyBot Console".  

###Moneydance Set-up and Conventions

The expectation is that each medical provider has a liability account, which is named identically to the name that UHG uses.  These are expected to be sub-accounts of "Medical Providers".  Each of these accounts has a special comment (the only field available) to help the program set the correct category. In order to know the category to use, data is captured on the first row of the comment field of each provider

The first row of that field should contain the full category path and the non-unique part of the final element. So `X:Health:Tests:Test` is used for a test vendor such as Quest.  The program adds the last bit which is one of 'chg', 'ins adj' or 'ins pmt'.

### Steps

1. The UHG claims portal allows creating a filtered set of claims, which can be downloaded.  It must be named: `MedicalClaimSummary.csv`.  Thus best to delete it when done so the browser does not add `(1)`.  Note, if you edit the file with Excel - watch out so the claim numbers don't get represented as exponential notation as excel saves them that way.  To select only certain dates it is probably better to filter on the website by date.
2. To prepare the list of providers currently in Moneydance, run `list-medical-providers.py` inside moneydance.  This puts a csv file in the working directory.
3. The main program is `prepare.py`. It looks for its input file in the Downloads folder and the provider list in the current directory.  It verifies that the providers match before writing the .pkl file. Ignores generic vendor, 'PHARMACY'
4. Back in Moneydance run `med-ins-bridge.py`











