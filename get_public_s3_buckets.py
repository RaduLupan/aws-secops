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

def main():
    
    # Local values required for accessing Google Sheets API as a service account. Could be read from SSM Parameter Store instead.
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    service_account_file = 'credentials.json'
    sample_spreadsheet_id = '1z36C1xvQwrvrxyLlYIHx5wTZFt_BpOYi-q6DF_2B39g'
    
    bucket_properties = dict()
    public_buckets = []

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

if __name__ == '__main__':
    main()
