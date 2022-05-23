'''
-------------------------------------------------------------
This module contains functions to use with Google Sheets API.
-------------------------------------------------------------
'''

from __future__ import print_function

import google.auth

from googleapiclient.discovery import build   
from googleapiclient.errors import HttpError

from oauth2client.service_account import ServiceAccountCredentials

def get_values(creds, spreadsheet_id, range, major_dimension):
    '''
    Description: Returns a range of values from a spreadsheet.
    Parameters: 
    - creds: Credentials for a service account. The service account used must have have Editor access to the spreadsheet.
    - spreadsheet_id: the ID of the spreadsheet to retrieve from.
    - range: The A1 notation or R1C1 notation of the range to retrieve values from.
    - major_dimension: The major dimension that results should use. Accepted values 'ROWS' or 'COLUMNS'. 
    Method: spreadsheets.values.get
    HTTP Request: GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/{range}
    Documentation: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get
    '''
    
    # How values should be represented in the output.
    # The default render option is ValueRenderOption.FORMATTED_VALUE.
    value_render_option = 'FORMATTED_VALUE'

    # How dates, times, and durations should be represented in the output.
    # This is ignored if value_render_option is
    # FORMATTED_VALUE.
    # The default dateTime render option is [DateTimeRenderOption.SERIAL_NUMBER].
    date_time_render_option = 'FORMATTED_STRING' 

    try:
        service = build('sheets', 'v4', credentials=creds)

        request = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            majorDimension=major_dimension,
            range=range, 
            valueRenderOption=value_render_option, 
            dateTimeRenderOption=date_time_render_option)
        response = request.execute()

        rows = response.get('values', [])
        print(f"{len(rows)} rows retrieved.")
        return rows
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def append_values(creds, spreadsheet_id, range_name, value_input_option,
                  _values):
    try:
        service = build('sheets', 'v4', credentials=creds)

        values = [
            [
                # Cell values ...
            ],
            # Additional rows ...
        ]
        # [START_EXCLUDE silent]
        values = _values
        # [END_EXCLUDE]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def create_sheet(creds,title,spreadsheet_id):
    '''
    Description: Creates new sheet in spreadsheet.
    Parameters: 
    - creds: Credentials for a service account. The service account used must have have Editor access to the spreadsheet.
    - title: String representing the name of the sheet to be created.
    - spreadsheet_id: the ID of the spreadsheet containing the new sheet.
    Method: spreadsheets.values.batchUpdate
    HTTP Request: POST https://sheets.googleapis.com/v4/spreadsheets/spreadsheetId:batchUpdate
    Documentation: https://developers.google.com/sheets/api/samples/sheet
    '''   
    try:
        service = build('sheets', 'v4', credentials=creds)
        
        batch_update_spreadsheet_request_body = {'requests':[{'addSheet': {'properties': {'title': title}}}]}
        
        request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_spreadsheet_request_body)
        response = request.execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def update_sheet(creds, title, spreadsheet_id, data):
    '''
    Description: Sets values in the Sheet!A1 range in a sheet.
    Parameters: 
    - creds: Credentials for a service account. The service account used must have have Editor access to the spreadsheet.
    - title: String representing the name of the sheet to be updated.
    - spreadsheet_id: the ID of the spreadsheet that contains the sheet to be updated.
    - data: a list of values to be written in the title.A1 range of the title sheet.
    Method: spreadsheets.values.batchUpdate
    HTTP Request: POST https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values:batchUpdate
    Documentation: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate
    '''
    try:
        service = build('sheets', 'v4', credentials=creds)
        
        batch_update_values_request_body = {"data":[{"majorDimension": "ROWS", "range": (title+"!A1"), "values": [data]}], "valueInputOption": "USER_ENTERED"}
        
        request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_values_request_body)

        response = request.execute()
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
