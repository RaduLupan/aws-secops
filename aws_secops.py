'''
--------------------------------------------------------------------------------
This module contains functions to use in AWS for performing security operations.
--------------------------------------------------------------------------------
'''

import boto3
import botocore.session
from botocore.exceptions import ClientError

def evaluate_s3_public_access (bucket_name):
    
    s3 = boto3.client('s3')

    public_acl=True
    public_policy = False
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
