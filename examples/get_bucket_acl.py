'''
Example: How to get the ACL of a bucket.
'''
import boto3

s3 = boto3.client('s3')

bucket_name = "test"

bucket_acl = s3.get_bucket_acl(Bucket=bucket_name)

print(bucket_acl)

grants = bucket_acl['Grants']

print(f"Bucket Grants:\n {grants}")
