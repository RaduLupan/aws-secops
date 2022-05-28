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

    public_bucket_report = [] 
    public_buckets_report = []

    # Get the service client.
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        bucket_properties=aws_secops.evaluate_s3_public_access (bucket_name=bucket['Name'])
        if bucket_properties['PublicACL'] or bucket_properties['PublicPolicy']:
            public_buckets.append(bucket_properties)
            
            # Serialize each bucket_properties and append to public_bucket_report list.
            public_bucket_report.append(json.dumps(bucket_properties))
            
            # Append all public_bucket_report lists to the public_buckets_report list.
            public_buckets_report.append(public_bucket_report)

    if len(public_buckets) == 0:
        print("No public buckets detected. That's actually great!")
    else:
        print(f'The list of public buckets is below:\n {public_buckets}')

        # Credentials for Google Sheets API.
        creds = gsheets_api.ServiceAccountCredentials.from_json_keyfile_name(
        service_account_file,
        scopes,
        )

        # Create new sheet in the existing spreadsheet.
        gsheets_api.create_sheet(creds=creds, title='S3 Public Buckets', spreadsheet_id=sample_spreadsheet_id)

        # Append values contained in public_buckets_report list to newly created sheet after A1 row.
        gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range="S3 Public Buckets!A1",
                          insert_data_option='OVERWRITE',
                          data=public_buckets_report
        )
        
if __name__ == '__main__':
    main()
