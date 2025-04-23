#!/bin/bash
# Update the package index
sudo yum update -y

# Install Python3 and pip
sudo yum install -y python3

# Ensure pip in installed
python3 -m ensurepip --upgrade

# Create a directory for the Python script and environment file
mkdir -p /home/ec2-user/app

# Copy the Python script
cat <<EOF > /home/ec2-user/app/discordbot.py
${discordbot}
EOF

cat <<EOF > /home/ec2-user/app/.env
${env_file}
EOF

# Copy the requirements.txt file
cat <<EOF > /home/ec2-user/app/requirements.txt
${requirements}
EOF
## Copy the Any additional files similarly
# Install required Python packages
sudo pip3 install -r /home/ec2-user/app/requirements.txt

# Run the Python script
python3 /home/ec2-user/app/discordbot.py

cat <<EOF > /etc/systemd/system/discord.service
${[Unit]
Description=discord bot

[Service]
ExecStart=/usr/bin/python3 /home/ec2-user/app/discordbot.py

[Install]
WantedBy=multi-user.target}
EOF
