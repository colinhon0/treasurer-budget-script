import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.oauth2 import service_account

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1WU_kQWYORRPw5cWog3lHBKZy9bgoCRX_0T6OTHuEejw'
SAMPLE_RANGE_NAME = 'CSVData!A1:D204'

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()

        values = result.get('values', [])
        print(values)


    except HttpError as err:
        print(err)


if __name__ == '__main__':
    main()