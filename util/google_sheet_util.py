from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Service account credentials file
SERVICE_ACCOUNT_FILE = '../resource/sage-inquiry-388907-041263e1f9e9.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Google Sheets setup
SPREADSHEET_ID = '18qF2qRLfyNfCozqSEOx4NrlW1tK7Di7_91syJ1UuL-o'  # Replace with your Sheet ID
RANGE_NAME = 'checkout_page'  # Replace with your sheet/tab name


def lookup_row(channel_name, ts):
    # Authenticate and build the Sheets API client
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Get all rows from the sheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    # Find the row with matching criteria
    headers = rows[0]  # Assumes the first row is headers
    channel_idx = headers.index('channel name')
    ts_idx = headers.index('ts time')

    for i in range(0, len(rows)):  # Skip the header row
        row = rows[i]
        if len(row) > max(channel_idx, ts_idx):  # Ensure the row has enough columns
            if row[channel_idx] == channel_name and row[ts_idx] == ts:
                return i

    return None  # No matching row found


def update(channel_name, ts):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Get all rows from the sheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    # Find the row with matching criteria
    headers = rows[0]  # Assumes the first row is headers
    channel_idx = headers.index('channel name')
    ts_idx = headers.index('ts time')
    body = {
        "values": [["Y"]]
    }
    for i in range(1, len(rows)):  # Skip the header row
        row = rows[i]
        if len(row) > max(channel_idx, ts_idx):  # Ensure the row has enough columns
            if row[channel_idx] == channel_name and row[ts_idx] == ts:
                service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"{RANGE_NAME}!H{i + 1}",
                    valueInputOption="RAW",  # or "USER_ENTERED" for formatted input
                    body=body
                ).execute()
                print(f"Row updated at")
                return


if __name__ == '__main__':
    print(update("hktvmall-hybris-revamp-checkout-qa", "12/3/2024 6:35:33"))
