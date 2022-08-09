from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

import datetime
from soctail_data import *

# TODO https://www.commbank.com.au/developer/documentation/Transactions to populate CSVData or autoload transaction data
# TODO Autofill with jira card information, now that would be poggers

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
        description = t[2]
    
    # zID Check
    idCheck = False
    
    '''for id in PRE_RELEASE_ID:
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
    '''       
    
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
SUMMARY_ID = '1gB9pvx6_kgp-oeo3Ronj7T2E6DnkoEQip1rchG9Vcys'
CSV_RANGE = 'CSVData!A1:C31'
LEDGER_RANGE = 'Ledger!A1'

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
            
        dates = [[t[0]] for t in parsedTransactions]
        price = [[t[1]] for t in parsedTransactions]
        description = [[t[2]] for t in parsedTransactions]
        quantity = [[t[3]] for t in parsedTransactions]
        
        data = [
            {
                'range': 'Ledger!B5',
                'values': dates
            },
            {
                'range': 'Ledger!C5',
                'values': price
            },
            {
                'range': 'Ledger!F5',
                'values': description
            },
            {
                'range': 'Ledger!D5',
                'values': quantity
            }
        ]
        
        body = {
            'valueInputOption': "USER_ENTERED",
            'data': data
        }
        
        # Write transactions to Ledger
        request = sheet.values().batchUpdate(
                spreadsheetId=SUMMARY_ID, body=body).execute()

    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()
