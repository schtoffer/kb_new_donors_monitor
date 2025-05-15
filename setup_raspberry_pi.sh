#!/bin/bash
# Setup script for KB FG Monitor Flask application on Raspberry Pi
# Run this script with sudo: sudo bash setup_raspberry_pi.sh

# Default IP address - change this if needed
IP_ADDRESS="192.168.4.248"
GATEWAY="192.168.4.1"
DNS="8.8.8.8"
INTERFACE="eth0"  # Change to wlan0 if using WiFi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up KB FG Monitor Flask application...${NC}"

# 1. Configure static IP
echo -e "${GREEN}Configuring static IP address: $IP_ADDRESS${NC}"

# Backup the original dhcpcd.conf file
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup

# Add static IP configuration
cat << EOF >> /etc/dhcpcd.conf

# Static IP configuration for KB FG Monitor
interface $INTERFACE
static ip_address=$IP_ADDRESS/24
static routers=$GATEWAY
static domain_name_servers=$GATEWAY $DNS
EOF

echo -e "${GREEN}Static IP configuration added to /etc/dhcpcd.conf${NC}"

# 2. Copy the systemd service file
echo -e "${GREEN}Setting up systemd service...${NC}"
cp flask-monitor.service /etc/systemd/system/

# 3. Enable and start the service
echo -e "${GREEN}Enabling and starting the service...${NC}"
systemctl enable flask-monitor.service
systemctl start flask-monitor.service

# 4. Open firewall port if ufw is active
if command -v ufw &> /dev/null; then
    echo -e "${GREEN}Opening port 5000 in firewall...${NC}"
    ufw allow 5000/tcp
fi

# 5. Check service status
echo -e "${GREEN}Checking service status:${NC}"
systemctl status flask-monitor.service

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}Your Flask application should now be accessible at http://$IP_ADDRESS:5000${NC}"
echo -e "${GREEN}You will need to reboot for the static IP configuration to take effect:${NC}"
echo -e "${GREEN}sudo reboot${NC}"
