from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from pyasn1_modules.rfc2459 import ExtensionORAddressComponents

# Connecting to sheets API with api account
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID and range of the exported CSV data
# CHANGE FOR EVERY MONTH!
SUMMARY_ID = '1gB9pvx6_kgp-oeo3Ronj7T2E6DnkoEQip1rchG9Vcys'
LEDGER_RANGE = 'Ledger!B5:I109'
BUDGET_ID = '1TxV6Jc5VTb6I9F2TzQ88MYJoM1d4COZfJM1c9JiTeaM'

def main():
    
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SUMMARY_ID,
                                    range=LEDGER_RANGE).execute()

        values = result.get('values', [])
        
        expenses = []
        income = []
        
        for t in values:
            t[3] = t[3].replace('$','')
            if '-' in t[1]:
                t[3] = t[3].replace('-','')
                expenses.append(t)
            else:
                income.append(t)
        
        eDates = [[t[0]] for t in expenses]
        eAmount = [[t[3]] for t in expenses]
        eDescription = [[t[4]] for t in expenses]
        eCategory = [[t[6]] for t in expenses]
        
        iDates = [[t[0]] for t in income]
        iAmount = [[t[3]] for t in income]
        iDescription = [[t[4]] for t in income]
        iCategory = [[t[6]] for t in income]
        
        data = [
            {
                'range': 'Transactions!B5',
                'values': eDates
            },
            {
                'range': 'Transactions!C5',
                'values': eAmount
            },
            {
                'range': 'Transactions!D5',
                'values': eDescription
            },
            {
                'range': 'Transactions!E5',
                'values': eCategory
            },
            {
                'range': 'Transactions!G5',
                'values': iDates
            },
            {
                'range': 'Transactions!H5',
                'values': iAmount
            },
            {
                'range': 'Transactions!I5',
                'values': iDescription
            },
            {
                'range': 'Transactions!J5',
                'values': iCategory
            }
        ]
        
        body = {
            'valueInputOption': "USER_ENTERED",
            'data': data
        }
        
        # Write transactions to Transactions
        request = sheet.values().batchUpdate(
                spreadsheetId=SUMMARY_ID, body=body).execute()
                
                
                
        # Write to budget
        # Revenue
        # TODO REFACTOR 
        for inc in income:
            print(inc)
                            
        for exp in expenses:
            print(exp)
            
        
        

    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()