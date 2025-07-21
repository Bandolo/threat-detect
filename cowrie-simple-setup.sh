#!/bin/bash
set -e

# -------- 1. Update and install dependencies --------
apt update && apt install -y python3 python3-pip python3-venv git awscli

# -------- 2. Create cowrie user --------
useradd -m -s /bin/bash cowrie

# -------- 3. Clone and set up Cowrie --------
cd /home/cowrie
sudo -u cowrie git clone https://github.com/cowrie/cowrie
cd cowrie
sudo -u cowrie python3 -m venv cowrie-env
sudo -u cowrie cowrie-env/bin/pip install --upgrade pip
sudo -u cowrie cowrie-env/bin/pip install -r requirements.txt
sudo -u cowrie cowrie-env/bin/pip install -e .

# -------- 4. Configure Cowrie on port 2222 --------
sudo -u cowrie cp etc/cowrie.cfg.dist etc/cowrie.cfg
sudo -u cowrie sed -i 's/hostname = svr04/hostname = honeypot/' etc/cowrie.cfg

# Enable JSON logging
sudo -u cowrie sed -i 's/^#\[output_jsonlog\]/[output_jsonlog]/' etc/cowrie.cfg
sudo -u cowrie sed -i '/^\[output_jsonlog\]/,/^\[/ s/^#enabled = false/enabled = true/' etc/cowrie.cfg

# -------- 5. Start Cowrie --------
sudo -u cowrie /home/cowrie/cowrie/bin/cowrie start

# -------- 5.1. Fix log file permissions for S3 uploads --------
sleep 5  # Wait for Cowrie to create log files
chmod 755 /home/cowrie/cowrie/var/log/cowrie/
chmod 644 /home/cowrie/cowrie/var/log/cowrie/cowrie.json 2>/dev/null || true

# -------- 6. Create systemd service --------
cat > /etc/systemd/system/cowrie.service << 'EOF'
[Unit]
Description=Cowrie SSH Honeypot
After=network.target

[Service]
Type=forking
User=cowrie
Group=cowrie
WorkingDirectory=/home/cowrie/cowrie
ExecStart=/home/cowrie/cowrie/bin/cowrie start
ExecStop=/home/cowrie/cowrie/bin/cowrie stop
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cowrie

# -------- 7. Install boto3 and S3 upload script --------
pip3 install boto3

cat > /home/ubuntu/upload_to_s3.py << 'PYEOF'
import os, boto3
from datetime import datetime

s3 = boto3.client("s3")
bucket = "creditcardd"
log_file = "/home/cowrie/cowrie/var/log/cowrie/cowrie.json"

if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    s3_key = f"cowrie-logs/cowrie_{timestamp}.json"
    try:
        s3.upload_file(log_file, bucket, s3_key)
        print(f"Uploaded to s3://{bucket}/{s3_key}")
        # Don't clear the file - preserve logs for multiple uploads
    except Exception as e:
        print(f"Upload failed: {e}")
else:
    print("No log file to upload.")
PYEOF

chmod +x /home/ubuntu/upload_to_s3.py

# -------- 8. Set up cron job with sudo for file access --------
# Set up cron job for ubuntu user (user data runs as root, so we need to specify user)
sudo -u ubuntu bash -c '(crontab -l 2>/dev/null; echo "*/5 * * * * sudo /usr/bin/python3 /home/ubuntu/upload_to_s3.py >> /var/log/upload_to_s3.log 2>&1") | crontab -'

# -------- 8.1. Allow ubuntu user to run upload script with sudo without password --------
echo "ubuntu ALL=(ALL) NOPASSWD: /usr/bin/python3 /home/ubuntu/upload_to_s3.py" >> /etc/sudoers.d/cowrie-upload
chmod 440 /etc/sudoers.d/cowrie-upload

echo "✅ Cowrie honeypot setup complete!"
echo "✅ SSH admin access: port 22 (normal SSH)"
echo "✅ Honeypot listening: port 2222"
echo "✅ Logs uploading to S3 every 5 minutes"
echo "✅ Test honeypot: ssh -p 2222 root@instance-ip"