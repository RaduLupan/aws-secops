#!/usr/bin/env python3
"""
SQS Queue Encryption Enabler
Helps enable encryption on SQS queues safely.
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any

class SQSEncryptionEnabler:
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize the SQS encryption enabler."""
        self.region_name = region_name
        self.sqs_client = None
        self.kms_client = None
        
    def initialize_clients(self):
        """Initialize AWS clients."""
        try:
            self.sqs_client = boto3.client('sqs', region_name=self.region_name)
            self.kms_client = boto3.client('kms', region_name=self.region_name)
            print(f"✅ AWS clients initialized successfully in region: {self.region_name}")
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please configure AWS CLI or set environment variables.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error initializing AWS clients: {e}")
            sys.exit(1)
    
    def get_queue_attributes(self, queue_url: str) -> Dict[str, Any]:
        """Get queue attributes including encryption status."""
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
    
    def list_available_kms_keys(self) -> List[Dict[str, Any]]:
        """List available KMS keys for encryption."""
        try:
            if self.kms_client:
                response = self.kms_client.list_keys()
                keys = []
                
                for key in response.get('Keys', []):
                    key_id = key['KeyId']
                    try:
                        key_info = self.kms_client.describe_key(KeyId=key_id)
                        key_metadata = key_info.get('KeyMetadata', {})
                        
                        if key_metadata.get('KeyState') == 'Enabled':
                            keys.append({
                                'key_id': key_id,
                                'key_arn': key_metadata.get('Arn', ''),
                                'description': key_metadata.get('Description', 'No description'),
                                'key_usage': key_metadata.get('KeyUsage', 'Unknown')
                            })
                    except Exception:
                        continue
                
                return keys
            return []
        except Exception as e:
            print(f"❌ Error listing KMS keys: {e}")
            return []
    
    def enable_sse_sqs_encryption(self, queue_url: str) -> Dict[str, Any]:
        """Enable SSE-SQS encryption on a queue."""
        try:
            if self.sqs_client:
                response = self.sqs_client.set_queue_attributes(
                    QueueUrl=queue_url,
                    Attributes={
                        'SqsManagedSseEnabled': 'true'
                    }
                )
                return {
                    'success': True,
                    'encryption_type': 'SSE-SQS',
                    'message': 'SSE-SQS encryption enabled successfully'
                }
            return {'success': False, 'error': 'SQS client not initialized'}
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
    
    def enable_kms_encryption(self, queue_url: str, kms_key_id: str) -> Dict[str, Any]:
        """Enable KMS encryption on a queue."""
        try:
            if self.sqs_client:
                response = self.sqs_client.set_queue_attributes(
                    QueueUrl=queue_url,
                    Attributes={
                        'SqsManagedSseEnabled': 'true',
                        'KmsMasterKeyId': kms_key_id
                    }
                )
                return {
                    'success': True,
                    'encryption_type': 'KMS',
                    'kms_key_id': kms_key_id,
                    'message': f'KMS encryption enabled successfully with key: {kms_key_id}'
                }
            return {'success': False, 'error': 'SQS client not initialized'}
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
    
    def test_queue_after_encryption(self, queue_url: str) -> Dict[str, Any]:
        """Test if queue still works after enabling encryption."""
        test_message = {
            'test': True,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Encryption test message'
        }
        
        try:
            if self.sqs_client:
                # Test sending
                send_response = self.sqs_client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(test_message)
                )
                
                # Test receiving
                receive_response = self.sqs_client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=5
                )
                
                messages = receive_response.get('Messages', [])
                
                return {
                    'success': True,
                    'send_success': True,
                    'receive_success': len(messages) > 0,
                    'message_id': send_response.get('MessageId'),
                    'messages_received': len(messages)
                }
            return {'success': False, 'error': 'SQS client not initialized'}
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def enable_encryption_on_queue(self, queue_url: str, encryption_type: str = 'sse-sqs', kms_key_id: str = None) -> Dict[str, Any]:
        """Enable encryption on a single queue with testing."""
        print(f"\n🔐 Enabling encryption on: {queue_url}")
        
        # Get current attributes
        attributes = self.get_queue_attributes(queue_url)
        current_encryption = attributes.get('SqsManagedSseEnabled', 'false')
        
        if current_encryption.lower() == 'true':
            return {
                'success': True,
                'message': 'Encryption already enabled',
                'encryption_type': 'Already encrypted'
            }
        
        # Enable encryption
        if encryption_type.lower() == 'kms' and kms_key_id:
            result = self.enable_kms_encryption(queue_url, kms_key_id)
        else:
            result = self.enable_sse_sqs_encryption(queue_url)
        
        if not result['success']:
            return result
        
        # Test the queue after encryption
        print(f"   Testing queue functionality after encryption...")
        test_result = self.test_queue_after_encryption(queue_url)
        
        if test_result['success']:
            print(f"   ✅ Queue test successful after encryption")
            result['test_result'] = test_result
        else:
            print(f"   ⚠️  Queue test failed after encryption: {test_result.get('error_message', 'Unknown error')}")
            result['test_result'] = test_result
        
        return result
    
    def interactive_encryption_setup(self, queue_urls: List[str]):
        """Interactive setup for enabling encryption on multiple queues."""
        print("🔐 SQS Queue Encryption Setup")
        print("=" * 50)
        
        self.initialize_clients()
        
        # List available KMS keys
        print("\n📋 Available KMS Keys:")
        kms_keys = self.list_available_kms_keys()
        
        if kms_keys:
            for i, key in enumerate(kms_keys):
                print(f"   {i+1}. {key['key_id']} - {key['description']}")
            print(f"   {len(kms_keys)+1}. Use SSE-SQS (AWS managed)")
        else:
            print("   No KMS keys found. Will use SSE-SQS (AWS managed)")
        
        # Ask for encryption preference
        print(f"\n🔧 Encryption Options:")
        print("   1. SSE-SQS (AWS managed) - Recommended for most cases")
        print("   2. KMS (Customer managed) - For sensitive data")
        
        try:
            choice = input("\nSelect encryption type (1 or 2): ").strip()
            
            encryption_type = 'sse-sqs'
            kms_key_id = None
            
            if choice == '2' and kms_keys:
                key_choice = input(f"Select KMS key (1-{len(kms_keys)}): ").strip()
                try:
                    key_index = int(key_choice) - 1
                    if 0 <= key_index < len(kms_keys):
                        kms_key_id = kms_keys[key_index]['key_id']
                        encryption_type = 'kms'
                        print(f"Selected KMS key: {kms_key_id}")
                    else:
                        print("Invalid key selection. Using SSE-SQS.")
                except ValueError:
                    print("Invalid input. Using SSE-SQS.")
            
            # Process queues
            results = []
            for queue_url in queue_urls:
                result = self.enable_encryption_on_queue(queue_url, encryption_type, kms_key_id)
                results.append({
                    'queue_url': queue_url,
                    'result': result
                })
            
            # Generate report
            self.generate_encryption_report(results)
            
        except KeyboardInterrupt:
            print("\n\n❌ Operation cancelled by user")
            sys.exit(1)
    
    def generate_encryption_report(self, results: List[Dict[str, Any]]):
        """Generate a report of encryption enablement results."""
        print("\n" + "=" * 50)
        print("📊 ENCRYPTION ENABLEMENT REPORT")
        print("=" * 50)
        
        successful = 0
        failed = 0
        already_encrypted = 0
        
        for result in results:
            queue_url = result['queue_url']
            encryption_result = result['result']
            
            if encryption_result['success']:
                if 'Already encrypted' in encryption_result.get('encryption_type', ''):
                    already_encrypted += 1
                    print(f"🟢 {queue_url.split('/')[-1]}: Already encrypted")
                else:
                    successful += 1
                    print(f"✅ {queue_url.split('/')[-1]}: {encryption_result.get('encryption_type', 'Encrypted')}")
                    
                    # Show test results
                    test_result = encryption_result.get('test_result', {})
                    if test_result.get('success'):
                        print(f"   ✅ Test: Send/Receive working")
                    else:
                        print(f"   ⚠️  Test: {test_result.get('error_message', 'Failed')}")
            else:
                failed += 1
                print(f"❌ {queue_url.split('/')[-1]}: {encryption_result.get('error_message', 'Failed')}")
        
        print(f"\n📈 Summary:")
        print(f"   • Successfully encrypted: {successful}")
        print(f"   • Already encrypted: {already_encrypted}")
        print(f"   • Failed: {failed}")
        
        if successful > 0:
            print(f"\n✅ Encryption setup completed successfully!")
        if failed > 0:
            print(f"\n⚠️  Some queues failed encryption setup. Check the errors above.")

def main():
    """Main function to run the SQS encryption enabler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enable encryption on SQS queues')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--queues', nargs='+', required=True, help='Queue URLs to enable encryption on')
    parser.add_argument('--encryption-type', choices=['sse-sqs', 'kms'], default='sse-sqs', 
                       help='Encryption type (default: sse-sqs)')
    parser.add_argument('--kms-key-id', help='KMS key ID (required if encryption-type is kms)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.encryption_type == 'kms' and not args.kms_key_id:
        print("❌ KMS key ID is required when using KMS encryption")
        sys.exit(1)
    
    # Create enabler instance
    enabler = SQSEncryptionEnabler(region_name=args.region)
    
    if len(args.queues) == 1:
        # Single queue - direct enablement
        enabler.initialize_clients()
        result = enabler.enable_encryption_on_queue(args.queues[0], args.encryption_type, args.kms_key_id)
        
        if result['success']:
            print(f"✅ Encryption enabled successfully: {result.get('message', '')}")
        else:
            print(f"❌ Failed to enable encryption: {result.get('error_message', '')}")
    else:
        # Multiple queues - interactive setup
        enabler.interactive_encryption_setup(args.queues)

if __name__ == "__main__":
    main() 