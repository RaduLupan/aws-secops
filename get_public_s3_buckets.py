'''
------------------------------------------------------------------------------------------------
Description: 
This script loops through all the S3 buckets in an AWS account and determines if public access
is granted by either ACL or bucket policy.
The public buckets are listed in a Google Sheet as serialized dictionaries.
-------------------------------------------------------------------------------------------------
'''

import gsheets_api
import aws_secops
import boto3

import json

from datetime import datetime

def main():
    
    # Local values required for accessing Google Sheets API as a service account. Could be read from SSM Parameter Store instead.
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    service_account_file = 'credentials.json'
    sample_spreadsheet_id = '1z36C1xvQwrvrxyLlYIHx5wTZFt_BpOYi-q6DF_2B39g'
    
    bucket_properties = dict()
    
    # List of dictionaries.
    public_buckets = [] 

    public_bucket_report_raw = [] 
    public_bucket_report_normalized = []
    public_bucket_report_serialized = []

    public_buckets_report_raw = []
    public_buckets_report_normalized = []
    public_buckets_report_serialized = []

    now=datetime.now()
    # See the Python strftime cheatsheet https://strftime.org/ for more formatting options.
    now_str=now.strftime("%Y-%m-%d At %H:%M:%S")

    # Get the service client.
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    for bucket in response['Buckets']:
        bucket_properties=aws_secops.evaluate_s3_public_access (bucket_name=bucket['Name'])
        if bucket_properties['PublicACL'] or bucket_properties['PublicPolicy']:
            public_buckets.append(bucket_properties)
            
            # Serialize each bucket_properties and convert to list.
            public_bucket_report_raw = [json.dumps(bucket_properties)]
            public_bucket_report_normalized = [
                bucket_properties['Name'],
                bucket_properties['PublicACL'],
                bucket_properties['PublicPolicy'],
                json.dumps(bucket_properties['Owner']),
                json.dumps(bucket_properties['Grants'])
            ]
            public_bucket_report_serialized=aws_secops.serialize_bucket_properties(bucket_properties=bucket_properties, mode='NORMALIZED')

            # Append all public_bucket_report lists to the public_buckets_report list.
            public_buckets_report_raw.append(public_bucket_report_raw)
            public_buckets_report_normalized.append(public_bucket_report_normalized)
            public_buckets_report_serialized.append(public_bucket_report_serialized)

    if len(public_buckets) == 0:
        print("No public buckets detected. That's actually great!")
    else:
        print(f'The list of public buckets is below:\n {public_buckets}')

        # Credentials for Google Sheets API.
        creds = gsheets_api.ServiceAccountCredentials.from_json_keyfile_name(
        service_account_file,
        scopes,
        )

        # Create new sheets for raw and normalized reports in the existing spreadsheet.
        gsheets_api.create_sheet(creds=creds, title='S3 Public Buckets-RAW', spreadsheet_id=sample_spreadsheet_id)
        gsheets_api.create_sheet(creds=creds, title='S3 Public Buckets-NORMALIZED', spreadsheet_id=sample_spreadsheet_id)
        gsheets_api.create_sheet(creds=creds, title='S3 Public Buckets-SERIALIZED', spreadsheet_id=sample_spreadsheet_id)
       
        datetime_stamp=[f'S3 Public Buckets Report - Created on {now_str}']

        # Add a datetime stamp on both sheets. 
        gsheets_api.update_sheet(creds, title = 'S3 Public Buckets-RAW', spreadsheet_id=sample_spreadsheet_id, data=datetime_stamp)
        gsheets_api.update_sheet(creds, title = 'S3 Public Buckets-NORMALIZED', spreadsheet_id=sample_spreadsheet_id, data=datetime_stamp)
        gsheets_api.update_sheet(creds, title = 'S3 Public Buckets-SERIALIZED', spreadsheet_id=sample_spreadsheet_id, data=datetime_stamp)

        # Data to be appended by append_values is a list of lists (rows).
        sheet_header_normalized=[['BucketName', 'PublicACL', 'PublicPolicy', 'Owner', 'Grants']]

        # Append sheet header to normalized report.
        gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range="S3 Public Buckets-NORMALIZED!A2",
                          insert_data_option='OVERWRITE',
                          data=sheet_header_normalized
        )
        
        gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range="S3 Public Buckets-SERIALIZED!A2",
                          insert_data_option='OVERWRITE',
                          data=sheet_header_normalized
        )
        
        # Append values contained in public_buckets_report_normalized list to the normalized sheet at A3 row.
        gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range="S3 Public Buckets-NORMALIZED!A3",
                          insert_data_option='OVERWRITE',
                          data=public_buckets_report_normalized
        )

        gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range="S3 Public Buckets-SERIALIZED!A3",
                          insert_data_option='OVERWRITE',
                          data=public_buckets_report_serialized
        )

        # Append values contained in public_buckets_report_raw list to the raw sheet at A2 row.
        gsheets_api.append_values(creds=creds,
                          spreadsheet_id=sample_spreadsheet_id,
                          range="S3 Public Buckets-RAW!A2",
                          insert_data_option='OVERWRITE',
                          data=public_buckets_report_raw
        )
        
if __name__ == '__main__':
    main()
