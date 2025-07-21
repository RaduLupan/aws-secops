# SQS Queue Security Tester

A comprehensive Python tool for auditing AWS SQS queues for security issues, encryption status, and generating detailed markdown reports.

## 🚀 Features

- **🔍 Security Analysis**: Detect anonymous access, public access, and policy issues
- **🔐 Encryption Assessment**: Check SSE-SQS and KMS encryption status
- **📊 Risk-Based Prioritization**: Categorize queues by risk level (Critical, High, Medium, Low)
- **📄 Markdown Reports**: Generate professional security audit reports
- **🔧 Encryption Enabler**: Safely enable encryption on existing queues
- **✅ Functionality Testing**: Test message sending/receiving capabilities

## 📋 Prerequisites

- **Python 3.7+**
- **AWS CLI** configured with appropriate credentials
- **boto3** and **botocore** packages

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd SQS-Queue-Tester
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure AWS credentials:**
```bash
aws configure
# or
aws configure sso
```

## 🔧 Usage

### Basic Security Audit

```bash
# Test all queues in your account
python sqs_queue_tester.py

# Test specific queues
python sqs_queue_tester.py --queues "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"

# Test in different region
python sqs_queue_tester.py --region us-west-2
```

### Generate Markdown Reports

```bash
# Generate report with timestamp
python sqs_queue_tester.py

# Save to specific file
python sqs_queue_tester.py --output security_audit_report.md

# Test specific queues and generate report
python sqs_queue_tester.py --queues "https://sqs.us-east-1.amazonaws.com/123456789012/queue1" --output focused_report.md
```

### Enable Encryption

```bash
# Enable SSE-SQS encryption on a queue
python enable_sqs_encryption.py --queues "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"

# Enable KMS encryption on a queue
python enable_sqs_encryption.py --queues "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue" --encryption-type kms --kms-key-id alias/my-key

# Interactive setup for multiple queues
python enable_sqs_encryption.py --queues "https://sqs.us-east-1.amazonaws.com/123456789012/queue1" "https://sqs.us-east-1.amazonaws.com/123456789012/queue2"
```

## 📊 Risk Assessment

The tool categorizes queues by risk level:

- **🔴 Critical Risk**: Anonymous access + no encryption
- **🟠 High Risk**: Public access or no encryption
- **🟡 Medium Risk**: Blank policies
- **🟢 Low Risk**: Properly configured

## 📄 Report Features

Generated markdown reports include:

- **Executive Summary** with key metrics
- **Risk Assessment** breakdown
- **Encryption Status** analysis
- **Policy Analysis** details
- **Detailed Queue Analysis** for each queue
- **Actionable Recommendations** prioritized by risk
- **Action Plan** with phased approach

## 🔐 Encryption Types

- **SSE-SQS**: AWS managed encryption (no additional cost)
- **KMS**: Customer managed encryption (for sensitive data)

## 📁 Files

- `sqs_queue_tester.py` - Main security testing script
- `enable_sqs_encryption.py` - Encryption enabler script
- `test_sqs_example.py` - Example usage script
- `requirements.txt` - Python dependencies
- `ENHANCED_SQS_GUIDE.md` - Comprehensive usage guide
- `SQS_POLICY_GUIDE.md` - Policy security guide
- `sample_report.md` - Example markdown report

## 🎯 Use Cases

- **Security Audits**: Comprehensive SQS security assessment
- **Compliance Reporting**: Generate detailed security reports
- **Risk Management**: Prioritize security improvements
- **Encryption Migration**: Safely enable encryption on existing queues
- **Documentation**: Create security documentation for stakeholders

## 🚨 Security Recommendations

### Phase 1: Critical Issues (Immediate)
1. Disable anonymous access on all queues
2. Enable encryption on queues with sensitive data
3. Review public access permissions

### Phase 2: High Priority (This Week)
1. Enable encryption on remaining queues
2. Upgrade to KMS for sensitive data
3. Implement explicit policies where needed

### Phase 3: Medium Priority (This Month)
1. Review IAM permissions for blank policy queues
2. Monitor access patterns using CloudTrail
3. Document security configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: Create an issue in the repository
- **AWS Documentation**: [SQS Security](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-security.html)
- **AWS KMS**: [KMS Documentation](https://docs.aws.amazon.com/kms/latest/developerguide/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for security assessment purposes. Always test in non-production environments first and ensure you have proper AWS permissions before running security modifications.

---

*Built with ❤️ for AWS security best practices* 