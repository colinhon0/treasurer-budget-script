from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

import datetime
from soctail_data import *


'''
    Ledger of ALL transactions
    
    Transactions to record. Need to differentiate between Expense and Revenue here
    
    Yearly budget
    
    Plan:

    1. Export the months transfers as a CSV file in netbank
    
    2. Upload CSV file to CSVData on the monthly summary
    
    3. For each description, only keep the description
    
    3a. Extra parsing,
            Merge transactions which have equal date, total and 
            
    4. Write parsed data to Ledger page
    
    5. Manually allocate all categories to the correct budget before using the next script
    
    - Colin Hon
'''

# Function to merge transactions
def mergeTransactions(transactions, t):
    date, amount, description, _ = t
    
    # Parse description
    t[2] = description.replace("Transfer From ","")
    t[2] = t[2].replace("Transfer to ", "") 
    
    # Parse for Soctail in description
    if "soctail" not in description.lower():
        transactions.append(t)
        return 
    
    if float(amount) < 0:
        t[2] = "Soctail Refund"
        transactions.append(t)
        return
    
    # zID Check
    idCheck = False
    
    for id in PRE_RELEASE_ID:
        if id in description.lower():
            description = "Soctail Pre-Release"
            idCheck = True
            break;
            
    if not idCheck:
        for id in EARLY_BIRD_ID:
            if id in description.lower():
                description = "Soctail Early Bird"
                idCheck = True
                break;
                
    if not idCheck:
        for id in GENERAL_ID:
            if id in description.lower():
                description = "Soctail General Release"
                idCheck = True
                break;    
    
    # Check dates
    if not idCheck:
        dtime = datetime.strptime(date, '%d/%m/20%y')
        
        if (dtime >= GENERAL_TICKETS_START):
            description = "Soctail General Release"
        elif (dtime >= EARLY_BIRD_START):
            description = "Soctail Early Bird"
        else:
            description = "Soctail Pre-Release"
            
    t[2] = description
    
    for add_t in transactions:
        addedDate, addedAmount, addedDescription, _ = add_t
        
        if addedDate == date and addedAmount == amount and addedDescription == description:
            add_t[3] = add_t[3] + 1
            return
            
    transactions.append(t);
    return

# Connecting to sheets API with api account
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID and range of the exported CSV data
# CHANGE FOR EVERY MONTH!
SUMMARY_ID = '1OhG1af4-r3FQ4_emuFoKm6ccdGvHPj64SmZQ7NJ2qo8'
CSV_RANGE = 'CSVData!A1:C204'
LEDGER_RANGE = 'Test!A1'

def main():
    
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SUMMARY_ID,
                                    range=CSV_RANGE).execute()

        values = result.get('values', [])
        
        values.reverse()
        
        # Parse through transactions
        parsedTransactions = []
        for transaction in values:
            # Index 3 refers to amount
            transaction.append(1)
            mergeTransactions(parsedTransactions, transaction)
            
        # Write transactions to Ledger
        request = sheet.values().update(spreadsheetId=SUMMARY_ID, range=LEDGER_RANGE, 
            valueInputOption="USER_ENTERED", body={"values":parsedTransactions}).execute()

    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()
