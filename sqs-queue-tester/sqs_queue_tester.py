#!/usr/bin/env python3
"""
SQS Queue Security Tester
Tests SQS queues for anonymous access and message sending capabilities.
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any

class SQSQueueTester:
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize the SQS queue tester."""
        self.region_name = region_name
        self.sqs_client = None
        self.sts_client = None
        
    def initialize_clients(self):
        """Initialize AWS clients."""
        try:
            self.sqs_client = boto3.client('sqs', region_name=self.region_name)
            self.sts_client = boto3.client('sts', region_name=self.region_name)
            print(f"✅ AWS clients initialized successfully in region: {self.region_name}")
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS CLI or set environment variables.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {e}")
            sys.exit(1)
    
    def get_current_identity(self) -> Dict[str, Any]:
        """Get current AWS identity information."""
        try:
            if self.sts_client:
                response = self.sts_client.get_caller_identity()
                return response
            return {}
        except Exception as e:
            print(f"❌ Error getting caller identity: {e}")
            return {}
    
    def list_queues(self) -> List[str]:
        """List all SQS queues in the account."""
        try:
            if self.sqs_client:
                response = self.sqs_client.list_queues()
                queues = response.get('QueueUrls', [])
                print(f"📋 Found {len(queues)} SQS queues")
                return queues
            return []
        except Exception as e:
            print(f"❌ Error listing queues: {e}")
            return []
    
    def get_queue_attributes(self, queue_url: str) -> Dict[str, Any]:
        """Get queue attributes including policy."""
        try:
            if self.sqs_client:
                response = self.sqs_client.get_queue_attributes(
                    QueueUrl=queue_url,
                    AttributeNames=['All']
                )
                return response.get('Attributes', {})
            return {}
        except Exception as e:
            print(f"❌ Error getting attributes for {queue_url}: {e}")
            return {}
    
    def analyze_queue_policy(self, queue_url: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze queue policy for security issues."""
        policy = attributes.get('Policy', '{}')
        queue_name = queue_url.split('/')[-1]
        
        analysis = {
            'queue_name': queue_name,
            'queue_url': queue_url,
            'has_policy': bool(policy and policy != '{}'),
            'anonymous_access': False,
            'public_access': False,
            'blank_policy': False,
            'policy_issues': [],
            'recommendations': []
        }
        
        # Check for blank policy
        if not policy or policy == '{}' or policy.strip() == '':
            analysis['blank_policy'] = True
            analysis['recommendations'].append("Blank policy - using default SQS permissions")
            analysis['recommendations'].append("Security depends on IAM roles/policies of accessing users")
            analysis['recommendations'].append("Consider adding explicit queue policy for better control")
            return analysis
        
        try:
            policy_json = json.loads(policy)
            statements = policy_json.get('Statement', [])
            
            for statement in statements:
                # Check for anonymous access
                principal = statement.get('Principal', {})
                if principal == '*' or principal.get('AWS') == '*':
                    analysis['anonymous_access'] = True
                    analysis['policy_issues'].append("Anonymous access allowed (Principal: *)")
                
                # Check for public access
                effect = statement.get('Effect', '')
                action = statement.get('Action', '')
                if effect == 'Allow' and ('*' in action or 'sqs:*' in action):
                    analysis['public_access'] = True
                    analysis['policy_issues'].append("Public access allowed (Action: *)")
        
        except json.JSONDecodeError:
            analysis['policy_issues'].append("Invalid JSON in policy")
        
        return analysis
    
    def analyze_queue_encryption(self, queue_url: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze queue encryption status and provide risk assessment."""
        queue_name = queue_url.split('/')[-1]
        
        # Get encryption attributes
        sse_enabled = attributes.get('SqsManagedSseEnabled', 'false').lower() == 'true'
        kms_master_key_id = attributes.get('KmsMasterKeyId', '')
        
        analysis = {
            'queue_name': queue_name,
            'queue_url': queue_url,
            'encryption_enabled': sse_enabled,
            'kms_key_id': kms_master_key_id,
            'encryption_type': 'KMS' if kms_master_key_id else ('SSE-SQS' if sse_enabled else 'None'),
            'risk_level': 'Low',
            'risk_factors': [],
            'recommendations': []
        }
        
        # Assess risk based on encryption and policy
        policy_analysis = self.analyze_queue_policy(queue_url, attributes)
        
        # Calculate risk level
        risk_score = 0
        
        # Encryption risk factors
        if not sse_enabled:
            risk_score += 3
            analysis['risk_factors'].append("No encryption enabled")
            analysis['recommendations'].append("Enable server-side encryption (SSE)")
        
        # Policy risk factors
        if policy_analysis['anonymous_access']:
            risk_score += 5
            analysis['risk_factors'].append("Anonymous access enabled")
            analysis['recommendations'].append("Remove anonymous access immediately")
        
        if policy_analysis['public_access']:
            risk_score += 4
            analysis['risk_factors'].append("Public access enabled")
            analysis['recommendations'].append("Restrict public access")
        
        if policy_analysis['blank_policy']:
            risk_score += 1
            analysis['risk_factors'].append("Blank policy - depends on IAM")
            analysis['recommendations'].append("Review IAM permissions")
        
        # Determine risk level
        if risk_score >= 5:
            analysis['risk_level'] = 'Critical'
        elif risk_score >= 3:
            analysis['risk_level'] = 'High'
        elif risk_score >= 1:
            analysis['risk_level'] = 'Medium'
        else:
            analysis['risk_level'] = 'Low'
        
        # Add encryption-specific recommendations
        if sse_enabled:
            if kms_master_key_id:
                analysis['recommendations'].append("✅ KMS encryption enabled")
            else:
                analysis['recommendations'].append("✅ SSE-SQS encryption enabled")
                analysis['recommendations'].append("Consider upgrading to KMS encryption for better key management")
        else:
            analysis['recommendations'].append("🔴 Enable server-side encryption immediately")
            analysis['recommendations'].append("Consider KMS encryption for sensitive data")
        
        return analysis
    
    def test_message_sending(self, queue_url: str) -> Dict[str, Any]:
        """Test sending a message to the queue."""
        test_message = {
            'test': True,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Security test message - please delete if found'
        }
        
        try:
            response = self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(test_message),
                MessageAttributes={
                    'TestMessage': {
                        'StringValue': 'Security test',
                        'DataType': 'String'
                    }
                }
            )
            
            return {
                'success': True,
                'message_id': response.get('MessageId'),
                'md5': response.get('MD5OfMessageBody')
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            return {
                'success': False,
                'error_code': error_code,
                'error_message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error_code': 'Unknown',
                'error_message': str(e)
            }
    
    def test_message_receiving(self, queue_url: str) -> Dict[str, Any]:
        """Test receiving messages from the queue."""
        try:
            response = self.sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5
            )
            
            messages = response.get('Messages', [])
            return {
                'success': True,
                'messages_received': len(messages),
                'messages': messages
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            return {
                'success': False,
                'error_code': error_code,
                'error_message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error_code': 'Unknown',
                'error_message': str(e)
            }
    
    def test_queue(self, queue_url: str) -> Dict[str, Any]:
        """Comprehensive test of a single queue."""
        print(f"\n🔍 Testing queue: {queue_url}")
        
        # Get queue attributes
        attributes = self.get_queue_attributes(queue_url)
        
        # Analyze policy
        policy_analysis = self.analyze_queue_policy(queue_url, attributes)
        
        # Analyze encryption
        encryption_analysis = self.analyze_queue_encryption(queue_url, attributes)
        
        # Test message sending
        send_result = self.test_message_sending(queue_url)
        
        # Test message receiving
        receive_result = self.test_message_receiving(queue_url)
        
        return {
            'queue_url': queue_url,
            'attributes': attributes,
            'policy_analysis': policy_analysis,
            'encryption_analysis': encryption_analysis,
            'send_test': send_result,
            'receive_test': receive_result
        }
    
    def run_security_audit(self, specific_queues: List[str] = None, output_file: str = None):
        """Run a comprehensive security audit on SQS queues."""
        print("🚀 Starting SQS Queue Security Audit")
        print("=" * 50)
        
        # Initialize clients
        self.initialize_clients()
        
        # Get current identity
        identity = self.get_current_identity()
        print(f"👤 Current AWS Identity: {identity.get('Arn', 'Unknown')}")
        print(f"📊 Account ID: {identity.get('Account', 'Unknown')}")
        
        # Get queues to test
        if specific_queues:
            queues_to_test = specific_queues
            print(f"🎯 Testing specific queues: {len(queues_to_test)}")
        else:
            queues_to_test = self.list_queues()
            print(f"🔍 Testing all queues: {len(queues_to_test)}")
        
        if not queues_to_test:
            print("❌ No queues found to test")
            return
        
        # Test each queue
        results = []
        for queue_url in queues_to_test:
            result = self.test_queue(queue_url)
            results.append(result)
        
        # Generate report
        self.generate_report(results, output_file)
    
    def generate_report(self, results: List[Dict[str, Any]], output_file: str = None):
        """Generate a comprehensive security report."""
        print("\n" + "=" * 50)
        print("📊 SECURITY AUDIT REPORT")
        print("=" * 50)
        
        # Generate markdown report
        markdown_report = self.generate_markdown_report(results)
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_report)
                print(f"\n📄 Markdown report saved to: {output_file}")
            except Exception as e:
                print(f"❌ Error saving report to {output_file}: {e}")
        
        # Also save with timestamp if no specific file
        if not output_file:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"sqs_security_audit_{timestamp}.md"
            try:
                with open(default_filename, 'w', encoding='utf-8') as f:
                    f.write(markdown_report)
                print(f"\n📄 Markdown report saved to: {default_filename}")
            except Exception as e:
                print(f"❌ Error saving report: {e}")
        
        total_queues = len(results)
        queues_with_issues = 0
        queues_with_anonymous_access = 0
        queues_with_blank_policies = 0
        queues_without_encryption = 0
        queues_accepting_messages = 0
        
        # Risk level counters
        critical_risk = 0
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        for result in results:
            policy_analysis = result['policy_analysis']
            encryption_analysis = result['encryption_analysis']
            send_test = result['send_test']
            
            if policy_analysis['anonymous_access'] or policy_analysis['policy_issues']:
                queues_with_issues += 1
            
            if policy_analysis['anonymous_access']:
                queues_with_anonymous_access += 1
            
            if policy_analysis['blank_policy']:
                queues_with_blank_policies += 1
            
            if not encryption_analysis['encryption_enabled']:
                queues_without_encryption += 1
            
            # Count by risk level
            risk_level = encryption_analysis['risk_level']
            if risk_level == 'Critical':
                critical_risk += 1
            elif risk_level == 'High':
                high_risk += 1
            elif risk_level == 'Medium':
                medium_risk += 1
            else:
                low_risk += 1
            
            if send_test['success']:
                queues_accepting_messages += 1
        
        print(f"📈 Summary:")
        print(f"   • Total queues tested: {total_queues}")
        print(f"   • Queues with security issues: {queues_with_issues}")
        print(f"   • Queues with anonymous access: {queues_with_anonymous_access}")
        print(f"   • Queues with blank policies: {queues_with_blank_policies}")
        print(f"   • Queues without encryption: {queues_without_encryption}")
        print(f"   • Queues accepting messages: {queues_accepting_messages}")
        
        print(f"\n🚨 Risk Assessment:")
        print(f"   • 🔴 Critical Risk: {critical_risk}")
        print(f"   • 🟠 High Risk: {high_risk}")
        print(f"   • 🟡 Medium Risk: {medium_risk}")
        print(f"   • 🟢 Low Risk: {low_risk}")
        
        print(f"\n🔍 Detailed Results:")
        for result in results:
            policy_analysis = result['policy_analysis']
            encryption_analysis = result['encryption_analysis']
            send_test = result['send_test']
            
            queue_name = policy_analysis['queue_name']
            risk_level = encryption_analysis['risk_level']
            
            # Determine status icon based on risk level
            if risk_level == 'Critical':
                status = "🔴"
            elif risk_level == 'High':
                status = "🟠"
            elif risk_level == 'Medium':
                status = "🟡"
            else:
                status = "🟢"
            
            print(f"\n{status} Queue: {queue_name} ({risk_level} Risk)")
            print(f"   URL: {result['queue_url']}")
            
            # Policy information
            if policy_analysis['anonymous_access']:
                print(f"   ⚠️  ANONYMOUS ACCESS ENABLED!")
            
            if policy_analysis['blank_policy']:
                print(f"   📝 BLANK POLICY - Using default SQS permissions")
            
            if policy_analysis['policy_issues']:
                print(f"   ⚠️  Policy issues: {', '.join(policy_analysis['policy_issues'])}")
            
            # Encryption information
            if encryption_analysis['encryption_enabled']:
                if encryption_analysis['kms_key_id']:
                    print(f"   🔐 Encryption: KMS ({encryption_analysis['kms_key_id']})")
                else:
                    print(f"   🔐 Encryption: SSE-SQS (AWS managed)")
            else:
                print(f"   🔓 Encryption: DISABLED")
            
            # Risk factors
            if encryption_analysis['risk_factors']:
                print(f"   ⚠️  Risk factors: {', '.join(encryption_analysis['risk_factors'])}")
            
            # Message sending test
            if send_test['success']:
                print(f"   ✅ Message sending: SUCCESS (ID: {send_test['message_id']})")
            else:
                print(f"   ❌ Message sending: FAILED ({send_test['error_code']})")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if critical_risk > 0:
            print(f"   🔴 CRITICAL RISK - IMMEDIATE ACTION REQUIRED:")
            print(f"      • {critical_risk} queue(s) with critical security issues")
            print(f"      • Disable anonymous access immediately")
            print(f"      • Enable encryption on all queues")
            print(f"      • Review and update queue policies")
        
        if high_risk > 0:
            print(f"   🟠 HIGH RISK - PRIORITY ACTION REQUIRED:")
            print(f"      • {high_risk} queue(s) with high security risk")
            print(f"      • Enable encryption on unencrypted queues")
            print(f"      • Review public access permissions")
            print(f"      • Consider upgrading to KMS encryption")
        
        if medium_risk > 0:
            print(f"   🟡 MEDIUM RISK - REVIEW RECOMMENDED:")
            print(f"      • {medium_risk} queue(s) with medium security risk")
            print(f"      • Review IAM permissions for blank policy queues")
            print(f"      • Consider adding explicit queue policies")
            print(f"      • Monitor access patterns")
        
        if queues_without_encryption > 0:
            print(f"   🔐 ENCRYPTION RECOMMENDATIONS:")
            print(f"      • Enable encryption on {queues_without_encryption} unencrypted queue(s)")
            print(f"      • Use KMS encryption for sensitive data")
            print(f"      • Consider SSE-SQS for non-sensitive data")
            print(f"      • Test encryption on a few queues first")
        
        if low_risk > 0:
            print(f"   🟢 LOW RISK - MONITORING RECOMMENDED:")
            print(f"      • {low_risk} queue(s) with low security risk")
            print(f"      • Continue monitoring access patterns")
            print(f"      • Regular security reviews")
            print(f"      • Keep encryption and policies up to date")
        
        print(f"\n✅ Audit completed!")
    
    def generate_markdown_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive markdown security report."""
        from datetime import datetime
        
        # Calculate statistics
        total_queues = len(results)
        queues_with_issues = 0
        queues_with_anonymous_access = 0
        queues_with_blank_policies = 0
        queues_without_encryption = 0
        queues_accepting_messages = 0
        
        # Risk level counters
        critical_risk = 0
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # Encryption statistics
        sse_sqs_encrypted = 0
        kms_encrypted = 0
        unencrypted = 0
        
        for result in results:
            policy_analysis = result['policy_analysis']
            encryption_analysis = result['encryption_analysis']
            send_test = result['send_test']
            
            if policy_analysis['anonymous_access'] or policy_analysis['policy_issues']:
                queues_with_issues += 1
            
            if policy_analysis['anonymous_access']:
                queues_with_anonymous_access += 1
            
            if policy_analysis['blank_policy']:
                queues_with_blank_policies += 1
            
            if not encryption_analysis['encryption_enabled']:
                queues_without_encryption += 1
                unencrypted += 1
            else:
                if encryption_analysis['kms_key_id']:
                    kms_encrypted += 1
                else:
                    sse_sqs_encrypted += 1
            
            # Count by risk level
            risk_level = encryption_analysis['risk_level']
            if risk_level == 'Critical':
                critical_risk += 1
            elif risk_level == 'High':
                high_risk += 1
            elif risk_level == 'Medium':
                medium_risk += 1
            else:
                low_risk += 1
            
            if send_test['success']:
                queues_accepting_messages += 1
        
        # Generate markdown content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        markdown = f"""# SQS Security Audit Report

**Generated:** {timestamp}  
**Account:** {self.get_current_identity().get('Account', 'Unknown')}  
**Region:** {self.region_name}  
**Total Queues Analyzed:** {total_queues}

---

## 📊 Executive Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Queues** | {total_queues} | 100% |
| **Queues with Issues** | {queues_with_issues} | {round(queues_with_issues/total_queues*100, 1) if total_queues > 0 else 0}% |
| **Queues Accepting Messages** | {queues_accepting_messages} | {round(queues_accepting_messages/total_queues*100, 1) if total_queues > 0 else 0}% |

## 🚨 Risk Assessment

| Risk Level | Count | Description |
|------------|-------|-------------|
| 🔴 **Critical Risk** | {critical_risk} | Anonymous access + no encryption |
| 🟠 **High Risk** | {high_risk} | Public access or no encryption |
| 🟡 **Medium Risk** | {medium_risk} | Blank policies |
| 🟢 **Low Risk** | {low_risk} | Properly configured |

## 🔐 Encryption Status

| Encryption Type | Count | Percentage |
|-----------------|-------|------------|
| **KMS Encryption** | {kms_encrypted} | {round(kms_encrypted/total_queues*100, 1) if total_queues > 0 else 0}% |
| **SSE-SQS Encryption** | {sse_sqs_encrypted} | {round(sse_sqs_encrypted/total_queues*100, 1) if total_queues > 0 else 0}% |
| **No Encryption** | {unencrypted} | {round(unencrypted/total_queues*100, 1) if total_queues > 0 else 0}% |

## 🔍 Policy Analysis

| Policy Type | Count | Percentage |
|-------------|-------|------------|
| **Anonymous Access** | {queues_with_anonymous_access} | {round(queues_with_anonymous_access/total_queues*100, 1) if total_queues > 0 else 0}% |
| **Blank Policies** | {queues_with_blank_policies} | {round(queues_with_blank_policies/total_queues*100, 1) if total_queues > 0 else 0}% |
| **Restrictive Policies** | {total_queues - queues_with_anonymous_access - queues_with_blank_policies} | {round((total_queues - queues_with_anonymous_access - queues_with_blank_policies)/total_queues*100, 1) if total_queues > 0 else 0}% |

---

## 📋 Detailed Queue Analysis

"""
        
        # Add detailed queue information
        for result in results:
            policy_analysis = result['policy_analysis']
            encryption_analysis = result['encryption_analysis']
            send_test = result['send_test']
            
            queue_name = policy_analysis['queue_name']
            risk_level = encryption_analysis['risk_level']
            
            # Determine status icon
            if risk_level == 'Critical':
                status_icon = "🔴"
            elif risk_level == 'High':
                status_icon = "🟠"
            elif risk_level == 'Medium':
                status_icon = "🟡"
            else:
                status_icon = "🟢"
            
            markdown += f"### {status_icon} {queue_name} ({risk_level} Risk)\n\n"
            markdown += f"**Queue URL:** `{result['queue_url']}`\n\n"
            
            # Policy information
            if policy_analysis['anonymous_access']:
                markdown += "⚠️ **ANONYMOUS ACCESS ENABLED**\n\n"
            
            if policy_analysis['blank_policy']:
                markdown += "📝 **BLANK POLICY** - Using default SQS permissions\n\n"
            
            if policy_analysis['policy_issues']:
                markdown += f"**Policy Issues:** {', '.join(policy_analysis['policy_issues'])}\n\n"
            
            # Encryption information
            if encryption_analysis['encryption_enabled']:
                if encryption_analysis['kms_key_id']:
                    markdown += f"🔐 **Encryption:** KMS ({encryption_analysis['kms_key_id']})\n\n"
                else:
                    markdown += f"🔐 **Encryption:** SSE-SQS (AWS managed)\n\n"
            else:
                markdown += f"🔓 **Encryption:** DISABLED\n\n"
            
            # Risk factors
            if encryption_analysis['risk_factors']:
                markdown += f"**Risk Factors:** {', '.join(encryption_analysis['risk_factors'])}\n\n"
            
            # Message sending test
            if send_test['success']:
                markdown += f"✅ **Message Sending:** SUCCESS (ID: `{send_test['message_id']}`)\n\n"
            else:
                markdown += f"❌ **Message Sending:** FAILED ({send_test['error_code']})\n\n"
            
            markdown += "---\n\n"
        
        # Add recommendations section
        markdown += """## 💡 Recommendations

"""
        
        if critical_risk > 0:
            markdown += f"""### 🔴 Critical Risk - Immediate Action Required

{critical_risk} queue(s) with critical security issues:

- **Disable anonymous access immediately**
- **Enable encryption on all queues**
- **Review and update queue policies**
- **Audit for any unauthorized access**

"""
        
        if high_risk > 0:
            markdown += f"""### 🟠 High Risk - Priority Action Required

{high_risk} queue(s) with high security risk:

- **Enable encryption on unencrypted queues**
- **Review public access permissions**
- **Consider upgrading to KMS encryption**
- **Implement explicit access controls**

"""
        
        if medium_risk > 0:
            markdown += f"""### 🟡 Medium Risk - Review Recommended

{medium_risk} queue(s) with medium security risk:

- **Review IAM permissions for blank policy queues**
- **Consider adding explicit queue policies**
- **Monitor access patterns**
- **Document intended access patterns**

"""
        
        if queues_without_encryption > 0:
            markdown += f"""### 🔐 Encryption Recommendations

{queues_without_encryption} unencrypted queue(s) found:

- **Enable encryption on all unencrypted queues**
- **Use KMS encryption for sensitive data**
- **Consider SSE-SQS for non-sensitive data**
- **Test encryption on a few queues first**
- **Monitor applications after enabling encryption**

"""
        
        if low_risk > 0:
            markdown += f"""### 🟢 Low Risk - Monitoring Recommended

{low_risk} queue(s) with low security risk:

- **Continue monitoring access patterns**
- **Regular security reviews**
- **Keep encryption and policies up to date**
- **Document security configurations**

"""
        
        # Add action plan
        markdown += """## 🎯 Action Plan

### Phase 1: Critical Issues (Immediate)
1. **Disable anonymous access** on all queues
2. **Enable encryption** on queues with sensitive data
3. **Review public access** permissions

### Phase 2: High Priority (This Week)
1. **Enable encryption** on remaining queues
2. **Upgrade to KMS** for sensitive data
3. **Implement explicit policies** where needed

### Phase 3: Medium Priority (This Month)
1. **Review IAM permissions** for blank policy queues
2. **Monitor access patterns** using CloudTrail
3. **Document security configurations**

### Phase 4: Ongoing (Continuous)
1. **Regular security audits**
2. **Monitor for new security issues**
3. **Keep encryption and policies up to date**

---

## 📞 Support & Resources

- **AWS SQS Security Documentation:** https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-security.html
- **AWS KMS Documentation:** https://docs.aws.amazon.com/kms/latest/developerguide/
- **AWS IAM Best Practices:** https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

---

*Report generated by SQS Security Audit Tool*
"""
        
        return markdown

def main():
    """Main function to run the SQS queue tester."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test SQS queues for security issues')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--queues', nargs='+', help='Specific queue URLs to test')
    parser.add_argument('--output', help='Output file for markdown report (optional)')
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = SQSQueueTester(region_name=args.region)
    
    # Run audit
    tester.run_security_audit(specific_queues=args.queues, output_file=args.output)

if __name__ == "__main__":
    main() 