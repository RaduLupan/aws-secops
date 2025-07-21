'''
--------------------------------------------------------------------------------
This module contains functions to use in AWS for performing security operations.
--------------------------------------------------------------------------------
'''

import boto3
import botocore.session
from botocore.exceptions import ClientError

import json

def evaluate_s3_public_access (bucket_name):
    '''
    Description: Returns relevant properties of an S3 bucket that determine whether the bucket is public due to Access Control List (ACL) or bucket policy.
    Parameters:
    - bucket_name: the name of the S3 bucket to be evaluated for public access.
    Examples:
    # Call the function for the bucket to be evaluated.
    my_bucket_properties=evaluate_s3_public_access(bucket_name='my-bucket')
    
    # Test if the bucket is public due to ACL or bucket policy.
    if my_bucket_properties['PublicACL'] or my_bucket_properties['PublicPolicy']:
        print('The bucket my-bucket is public.')
    else:
        print('The bucket my-bucket is not public.')
    '''
    s3 = boto3.client('s3')

    public_acl=None
    public_policy = None
    bucket_properties = {'Name':bucket_name, 'Grants':'Some grants'}
    
    # Get bucket ACL.
    try:
        bucket_acl = s3.get_bucket_acl(Bucket=bucket_name)
    
        bucket_properties['Owner']=bucket_acl['Owner']
        bucket_properties['Grants']=bucket_acl['Grants']
    
        # Amazon S3 considers a bucket or object ACL public if it grants any permissions to members of the predefined AllUsers or AuthenticatedUsers groups.
        # See The meaning of "Public" section here: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html 
        for grant in bucket_acl['Grants']:
            if grant['Grantee']['Type'] == 'Group':
                if (grant['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers') or (grant['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AuthenticatedUsers') :
                    public_acl = True
            # if grant['Grantee']['Type'] is not 'Group' the bucket is not public by ACL.
            else:
                public_acl = False

    except botocore.exceptions.ClientError as e:
        print("Unexpected error: %s" % (e.response))

    # Get bucket policy status.
    try:
        bucket_policy_status = s3.get_bucket_policy_status(Bucket=bucket_name)
    
        bucket_properties['PolicyStatus']=bucket_policy_status['PolicyStatus']
    
        public_policy = bucket_policy_status['PolicyStatus']['IsPublic']

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
            print(f"Bucket {bucket_name} does not have a bucket policy.")
            bucket_properties['PolicyStatus']="NOT_APPLICABLE"
        else:
            print("Unexpected error: %s" % (e.response))


    bucket_properties['PublicACL']=public_acl
    bucket_properties['PublicPolicy']=public_policy

    return bucket_properties

def serialize_bucket_properties(bucket_properties, mode):
    '''
    Description: Uses json module to serialize a public_bucket_properties dictionary so they can be printed.
    Parameters:
    - bucket_properties: Dictionary of dictonaries representing the properties of an S3 bucket returned by the evaluate_s3_public_access(bucket_name) function.
    - mode: string with accepted values 'RAW' or 'NORMALIZED'. 
        If mode = 'RAW' the whole bucket_properties dictionary is serialized to a flat string.
        If mode = 'NORMALIZED' the bucket's Name, PublicACL and PublicPolicy attributes are extracted and the Owner and Grants dictionaries are serialized. 
    TO-DO:
    -Introduce parameter validation for mode so that only RAW and NORMALIZED are accepted.
    '''

    serialized_bucket_properties = []

    match mode:
        case 'RAW':
            serialized_bucket_properties = [json.dumps(bucket_properties)]
    
        case 'NORMALIZED':
            serialized_bucket_properties = [
                bucket_properties['Name'],
                bucket_properties['PublicACL'],
                bucket_properties['PublicPolicy'],
                json.dumps(bucket_properties['Owner']),
                json.dumps(bucket_properties['Grants'])
            ]

    return serialized_bucket_properties
