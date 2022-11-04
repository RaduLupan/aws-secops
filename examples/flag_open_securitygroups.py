'''
Example: How to flag the ingress rules that open remote access ports to the whole Internet.
'''

import boto3

def flag_remote_access(groupId):
    '''
    Description: Returns a list of ingress security rules that allow access to port 3389 (RDP)/22 (SSH) from anywhere.
    '''

    # Get the client for the EC2 service.
    ec2 = boto3.client('ec2')

    filters=[{'Name': 'group-id', 'Values': [groupId]}]

    response = ec2.describe_security_group_rules(Filters = filters)

    offending_ingress_rules = []

    all_rules = response['SecurityGroupRules']

    for rule in all_rules:
    # Only flag ingress rules with CidrIpv4 equal to anywhere.
        if (rule['IsEgress'] == False) and (rule['CidrIpv4'] == '0.0.0.0/0'):
        
            # Flag the rules that allow RDP or SSH access from anywhere.
            if (rule['FromPort'] == 3389) or (rule['FromPort'] == 22):
                print(f"Ingress rule {rule['SecurityGroupRuleId']} opens port {rule['FromPort']} from anywhere!" )
                offending_ingress_rules.append(rule)

    return offending_ingress_rules
