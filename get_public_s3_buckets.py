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

def main():
    
    # Local values required for accessing Google Sheets API as a service account. Could be read from SSM Parameter Store instead.
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    service_account_file = 'credentials.json'
    sample_spreadsheet_id = '1z36C1xvQwrvrxyLlYIHx5wTZFt_BpOYi-q6DF_2B39g'
    
    bucket_properties = dict()
    public_buckets = []



if __name__ == '__main__':
    main()
