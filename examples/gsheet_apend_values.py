'''
Example: How to append values to Google sheet using service account credentials.
'''
import gsheets_api

scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

service_account_file = 'credentials.json'

# The ID and range of a sample spreadsheet.
sample_spreadsheet_id = '1z36C1xvQwrvrxyLlYIHx5wTZFt_BpOYi-q6DF_2B39g'
sample_range_name = 'My New Sheet!A1'

creds = gsheets_api.ServiceAccountCredentials.from_json_keyfile_name(
    service_account_file,
    scopes,
)

# Populate the data list with values to be appended.
data=[]
data.append(['John Green', 'Microsoft', '123 John Street'])
data.append(['Pamela Brown', 'Amazon', '456 Pamela Street'])

# Append values in a list to a sheet after specified range.
gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range=sample_range_name,
                          insert_data_option='OVERWRITE',
                          data=data
)
