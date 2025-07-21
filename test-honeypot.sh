#!/bin/bash
# Test script for verifying honeypot setup after EC2 launch

echo "🔍 Testing Honeypot Setup..."
echo "================================"

# Test 1: Check if Cowrie is running
echo "1. Checking Cowrie status..."
sudo -u cowrie /home/cowrie/cowrie/bin/cowrie status

# Test 2: Check cron job
echo -e "\n2. Checking cron job..."
crontab -l

# Test 3: Check AWS permissions
echo -e "\n3. Checking AWS permissions..."
aws sts get-caller-identity

# Test 4: Check log files
echo -e "\n4. Checking log files..."
sudo ls -la /home/cowrie/cowrie/var/log/cowrie/

# Test 5: Generate test logs
echo -e "\n5. Generating test logs..."
echo "Connect to honeypot with: ssh -p 2222 root@localhost"
echo "Try passwords like 'password', '123456', then exit"
read -p "Press Enter after testing the honeypot..."

# Test 6: Check if logs were created
echo -e "\n6. Checking generated logs..."
sudo cat /home/cowrie/cowrie/var/log/cowrie/cowrie.json | tail -5

# Test 7: Test S3 upload
echo -e "\n7. Testing S3 upload..."
sudo python3 /home/ubuntu/upload_to_s3.py

# Test 8: Check S3 bucket
echo -e "\n8. Checking S3 bucket..."
aws s3 ls s3://creditcardd/cowrie-logs/ | grep $(date +%Y-%m-%d)

# Test 9: Check upload logs
echo -e "\n9. Checking upload logs..."
cat /var/log/upload_to_s3.log 2>/dev/null || echo "No upload logs yet (cron hasn't run)"

echo -e "\n✅ Test complete!"
echo "If all tests passed, your honeypot is working correctly!"