'''
Example: How to flag the ingress rules that open remote access ports to the whole Internet.
'''

import boto3
from botocore.exceptions import ClientError

def flag_remote_access(groupId):
    '''
    Description: Returns a list of ingress security rules that allow access to port 3389 (RDP)/22 (SSH) from anywhere.
    '''

    # Get the client for the EC2 service.
    ec2 = boto3.client('ec2')

    filters=[{'Name': 'group-id', 'Values': [groupId]}]

    print(f"Processing security group: {groupId}")
    
    try:
        response = ec2.describe_security_group_rules(Filters = filters)

        all_rules = response['SecurityGroupRules']
    
        offending_ingress_rules = []
    
        if all_rules != []:

            for rule in all_rules:
                # Only flag ingress rules 
                if rule['IsEgress'] == False:
                 
                    print(f"Processing ingress rule: {rule['SecurityGroupRuleId']}")
                    # with either CidrIpv4 or CidrIpv6 range of anywhere
                    if (('CidrIpv4' in rule) and (rule['CidrIpv4'] == '0.0.0.0/0')) or (( 'CidrIpv6' in rule) and (rule['CidrIpv6'] == '::/0')):
        
                        # that allows RDP or SSH access
                        if (rule['FromPort'] == 3389) or (rule['FromPort'] == 22):
                            print(f"Ingress rule {rule['SecurityGroupRuleId']} opens port {rule['FromPort']} from anywhere!" )
                            offending_ingress_rules.append(rule)

            return offending_ingress_rules
    
        elif all_rules == []:
            print(f"No ingress rules found on security group {groupId}")
            return []
    except ClientError as err:
        print("Error connecting to the EC2 client: " + err.response['Error']['Code'] + ', Message: ' + str(err))
        return []

def secure_remote_access(groupId):
    '''
    Description: Modifies the ingress security rules that allow remote access from anywhere by replacing the 0.0.0.0/0 or ::/0 Cidr ranges with particular IPv4 or IPv6 values. 
    '''
sg_id = 'sg-09d0c55a2a08dcadb'

offending_ingress_rules = flag_remote_access(sg_id)

if len(offending_ingress_rules) > 0:
    print(f"The following ingress rules require remediation: {offending_ingress_rules}")
else:
    print('No offending ingress rules found.')
