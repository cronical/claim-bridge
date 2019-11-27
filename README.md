## Import insurance data from csv

United health care lets you download claims data. We use the default name `MedicalClaimSummary.csv` for that data.

These utilities read that data and create transactions in Moneydance in the providers accounts.

This runs mostly outside of moneydance, but to prepare the list of providers, run 

`list-medical-providers.py` 

inside moneydance.  This puts a csv file in the working directory.

The main program is `prepare.py`. It looks for its input file in the Downloads folder.

In order to know the category to use, data is captured on the comment field of each provider

The first row of that field should contain the full category path and the non-unique part of the final element. So `X:Health:Tests:Test` is used for a test vendor such as Quest.  The program adds the last bit which is one of 'chg', 'ins adj' or 'ins pmt'.









