# SQS Queue Policy Security Guide

## Understanding SQS Queue Policies

### 1. **Blank Policy (No Explicit Policy)**
```json
{}
```
**What it means:**
- No explicit IAM policy attached to the queue
- Uses default SQS permissions
- Access controlled by IAM roles/policies of users trying to access
- **NOT anonymous access** - users still need valid AWS credentials

**Security Level:** 🟡 **Medium** (depends on IAM configuration)

**Example:**
```bash
# Queue with blank policy
# Users need IAM permissions like:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sqs:SendMessage",
            "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue"
        }
    ]
}
```

### 2. **Anonymous Access Policy (DANGEROUS)**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "sqs:*",
            "Resource": "*"
        }
    ]
}
```
**What it means:**
- **Anyone on the internet** can access the queue
- No AWS account or credentials required
- **CRITICAL SECURITY RISK**

**Security Level:** 🔴 **Critical** (immediate action required)

### 3. **Restrictive Policy (RECOMMENDED)**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:role/MyAppRole"
            },
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage"
            ],
            "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue"
        }
    ]
}
```
**What it means:**
- Only specific IAM roles/users can access
- Explicit permissions defined
- **BEST PRACTICE**

**Security Level:** 🟢 **Secure**

## Security Recommendations

### For Blank Policies:
1. **Review IAM permissions** of users/roles accessing the queue
2. **Consider adding explicit policy** for better control
3. **Monitor access patterns** for unusual activity
4. **Document the intended access pattern**

### For Anonymous Access:
1. **IMMEDIATE ACTION REQUIRED**
2. **Remove or restrict the policy**
3. **Audit for any unauthorized access**
4. **Implement proper IAM-based access control**

### Best Practices:
1. **Use IAM roles** instead of queue policies when possible
2. **Principle of least privilege** - only grant necessary permissions
3. **Regular security audits** of queue policies
4. **Monitor CloudTrail logs** for access patterns

## Testing Your Queues

Use the provided Python script to test your queues:

```bash
# Test all queues
python sqs_queue_tester.py

# Test specific queues
python sqs_queue_tester.py --queues "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
```

## Common Policy Patterns

### Allow Specific Role:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:role/MyAppRole"
            },
            "Action": "sqs:SendMessage",
            "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue"
        }
    ]
}
```

### Allow Cross-Account Access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::987654321098:root"
            },
            "Action": "sqs:SendMessage",
            "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue"
        }
    ]
}
```

### Deny Anonymous Access:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "sqs:*",
            "Resource": "arn:aws:sqs:us-east-1:123456789012:my-queue",
            "Condition": {
                "StringEquals": {
                    "aws:PrincipalType": "Anonymous"
                }
            }
        }
    ]
}
```

## Quick Security Checklist

- [ ] No `"Principal": "*"` in policies
- [ ] No `"Action": "*"` or `"Action": "sqs:*"` unless necessary
- [ ] Specific IAM roles/users defined in policies
- [ ] Regular review of access patterns
- [ ] CloudTrail logging enabled
- [ ] Encryption enabled on queues
- [ ] Dead letter queues configured for failed messages 