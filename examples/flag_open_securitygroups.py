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
    Uses flag_remote_access() function to get the offending ingress rules.
    '''
    # Fake IP v4 to replace the 0.0.0.0/0 CIDR with in the offending rules.
    cidr_ip_v4 = '1.2.3.4/32'

    # Fake IP v6 to replace the ::/0 CIDR with in the offending rules.
    cidr_ip_v6 = '1234::/128'

    remediated_sg_rules = []

    offending_sg_rules = flag_remote_access(groupId)

    if len(offending_sg_rules) > 0:
        
        # Replace the open CidrIpv4 and CidrIpv6 with corresponding fake IPs to secure the rule.
        for rule in offending_sg_rules:
            if 'CidrIpv4' in rule:
                remediated_sg_rules.append({
                    'SecurityGroupRuleId': rule['SecurityGroupRuleId'], 
                    'SecurityGroupRule': {
                        'IpProtocol': rule['IpProtocol'],
                        'FromPort': rule['FromPort'],
                        'ToPort': rule['ToPort'],
                        'CidrIpv4': cidr_ip_v4,
                        'Description': 'REMEDIATED - Remote Access From Anywhere NOT Allowed'
                    }
                })
            elif 'CidrIpv6' in rule:
                remediated_sg_rules.append({
                    'SecurityGroupRuleId': rule['SecurityGroupRuleId'], 
                        'SecurityGroupRule': {
                        'IpProtocol': rule['IpProtocol'],
                        'FromPort': rule['FromPort'],
                        'ToPort': rule['ToPort'],
                        'CidrIpv6': cidr_ip_v6,
                        'Description': 'REMEDIATED - Remote Access From Anywhere NOT Allowed'
                        }
                })
        
    
        # Get the client for the EC2 service.
        ec2 = boto3.client('ec2')

        # Modify the offending rules.
        try:
            response = ec2.modify_security_group_rules(GroupId = groupId,
                                                       SecurityGroupRules = remediated_sg_rules)
            return remediated_sg_rules
        except ClientError as err:
            print("Error encountered while modifying the security group rules]: " + err.response['Error']['Code'] + ', Message: ' + str(err))
            return []
    else:
        # No offending ingress rules found.
        return []
    


sg_id = 'sg-09d0c55a2a08dcadb'

remediated_sg_rules = secure_remote_access(groupId = sg_id)

if len(remediated_sg_rules) > 0:
    print(f"The following security rules were remediated: {remediated_sg_rules}")
else:
    print("No offending ingress rules found.")
