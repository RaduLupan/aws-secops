'''
---------------------------------------------------------------------------------------------
Description: This script loops through all the S3 buckets in an AWS account and determines if 
public access is granted by either ACL or bucket policy.
The public buckets are listed in a Google Sheet.
Parameters: 
----------------------------------------------------------------------------------------------
'''

import gsheets_api
import aws_secops
import boto3

import json

def main():
    
    # Local values required for accessing Google Sheets API as a service account. Could be read from SSM Parameter Store instead.
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    service_account_file = 'credentials.json'
    sample_spreadsheet_id = '1z36C1xvQwrvrxyLlYIHx5wTZFt_BpOYi-q6DF_2B39g'
    
    bucket_properties = dict()
    
    # List of dictionaries.
    public_buckets = []

    # List of rows to append to Google Sheet.
    public_buckets_report =[]
    row = []

    # Get the service client.
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        bucket_properties=aws_secops.evaluate_s3_public_access (bucket_name=bucket['Name'])
        if bucket_properties['PublicACL'] or bucket_properties['PublicPolicy']:
            public_buckets.append(bucket_properties)

    if len(public_buckets) == 0:
        print("No public buckets detected. That's actually great!")
    else:
        print(f'The list of public buckets is below:\n {public_buckets}')

        for bucket in public_buckets:
            
            row.append(bucket['Name'])
            row.append(json.dumps(bucket['Grants'][0]))
            row.append(json.dumps(bucket['Owner']))

        # Credentials for Google Sheets API.
        creds = gsheets_api.ServiceAccountCredentials.from_json_keyfile_name(
        service_account_file,
        scopes,
        )

        # Create new sheet in the existing spreadsheet.
        gsheets_api.create_sheet(creds=creds, title='S3 Public Buckets', spreadsheet_id=sample_spreadsheet_id)

        # Update newly created sheet with data from a list.
        headers=['Name', 'Grants', 'Owner', 'PolicyStatus', 'PublicACL']
        gsheets_api.update_sheet(creds, title = 'S3 Public Buckets', spreadsheet_id=sample_spreadsheet_id, data=headers)

        # Append values to newly created sheet.
        result = gsheets_api.append_values(creds, sample_spreadsheet_id, "S3 Public Buckets!A2:C3", "USER_ENTERED",
             [
                 row
            ])
        print(result)

if __name__ == '__main__':
    main()
