#!/usr/bin/env python3
"""
Simple example to test specific SQS queues for security issues.
"""

from sqs_queue_tester import SQSQueueTester

def main():
    # Create tester instance
    tester = SQSQueueTester(region_name='us-east-1')  # Change region as needed
    
    # Example: Test specific queues
    specific_queues = [
        # Add your queue URLs here
        # 'https://sqs.us-east-1.amazonaws.com/123456789012/my-queue',
        # 'https://sqs.us-east-1.amazonaws.com/123456789012/another-queue',
    ]
    
    if specific_queues:
        print("Testing specific queues...")
        tester.run_security_audit(specific_queues=specific_queues)
    else:
        print("Testing all queues in the account...")
        tester.run_security_audit()

if __name__ == "__main__":
    main() 