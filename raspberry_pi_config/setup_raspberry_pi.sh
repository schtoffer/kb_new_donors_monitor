#!/bin/bash
# Setup script for KB FG Monitor Flask application on Raspberry Pi
# Run this script with sudo: sudo bash setup_raspberry_pi.sh

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up KB FG Monitor Flask application...${NC}"

# 1. Install required packages
echo -e "${GREEN}Installing required packages...${NC}"
apt update
apt install -y python3-pip python3-venv chromium-browser unclutter cron

# 2. Create application directory if it doesn't exist
echo -e "${GREEN}Setting up application directory...${NC}"
mkdir -p /home/pi/kb_fg_monitor
chown -R pi:pi /home/pi/kb_fg_monitor

# 3. Create startup scripts
echo -e "${GREEN}Creating startup scripts...${NC}"

# Create improved Flask app startup script
cat > /home/pi/kb_fg_monitor/test_flask.sh << 'EOF'
#!/bin/bash
cd ~/kb_fg_monitor
# Check if virtual environment exists
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
else
  echo "Creating virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
fi

# Always install/update dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the app
echo "Starting Flask app..."
python app.py > ~/flask.log 2>&1
EOF

# Create display control scripts
cat > /home/pi/kb_fg_monitor/display_off.sh << 'EOF'
#!/bin/bash
vcgencmd display_power 0
EOF

cat > /home/pi/kb_fg_monitor/display_on.sh << 'EOF'
#!/bin/bash
vcgencmd display_power 1
EOF

# Make scripts executable
chmod +x /home/pi/kb_fg_monitor/test_flask.sh
chmod +x /home/pi/kb_fg_monitor/hide_cursor.sh
chmod +x /home/pi/kb_fg_monitor/display_off.sh
chmod +x /home/pi/kb_fg_monitor/display_on.sh
chown pi:pi /home/pi/kb_fg_monitor/*.sh

# 4. Set up cron jobs
echo -e "${GREEN}Setting up cron jobs...${NC}"

# Add cron job to start Flask app at boot and hide cursor
cat > /tmp/flask_cron << 'EOF'
@reboot sleep 30 && /home/pi/kb_fg_monitor/test_flask.sh &
@reboot sleep 10 && /home/pi/kb_fg_monitor/hide_cursor.sh &
# Turn display off at 5 PM (17:00)
0 17 * * * /home/pi/kb_fg_monitor/display_off.sh
# Turn display on at 7 AM (07:00)
0 7 * * * /home/pi/kb_fg_monitor/display_on.sh
EOF

# Install cron job for pi user
crontab -u pi /tmp/flask_cron
rm /tmp/flask_cron

# 5. Set up browser autostart
echo -e "${GREEN}Setting up browser autostart...${NC}"

# Create autostart directory if it doesn't exist
mkdir -p /home/pi/.config/autostart
chown pi:pi /home/pi/.config/autostart

# Create browser autostart entry
cat > /home/pi/.config/autostart/kb-browser.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=KB Browser
Exec=/bin/bash -c "sleep 45 && chromium-browser --noerrdialogs --disable-infobars --kiosk http://localhost:5000"
X-GNOME-Autostart-enabled=true
EOF

# Create improved cursor hiding script
cat > /home/pi/kb_fg_monitor/hide_cursor.sh << 'EOF'
#!/bin/bash
# Kill any existing unclutter processes
pkill unclutter || true
# Start unclutter with aggressive settings
DISPLAY=:0 unclutter -idle 0 -root &
EOF

# Create hide cursor autostart entry
cat > /home/pi/.config/autostart/hide-cursor.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Hide Cursor
Exec=/home/pi/kb_fg_monitor/hide_cursor.sh
X-GNOME-Autostart-enabled=true
EOF

chown pi:pi /home/pi/.config/autostart/*.desktop

# 6. Disable screen blanking
echo -e "${GREEN}Disabling screen blanking...${NC}"

# Create or modify LXDE autostart file
mkdir -p /etc/xdg/lxsession/LXDE-pi
cat > /etc/xdg/lxsession/LXDE-pi/autostart << 'EOF'
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0 -root
EOF

# 7. Open firewall port if ufw is active
if command -v ufw &> /dev/null; then
    echo -e "${GREEN}Opening port 5000 in firewall...${NC}"
    ufw allow 5000/tcp
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}Your Flask application will start automatically after reboot.${NC}"
echo -e "${GREEN}The dashboard will be accessible at http://[YOUR-PI-IP]:5000${NC}"
echo -e "${GREEN}The display will turn off at 5 PM and turn on at 7 AM.${NC}"
echo -e "${GREEN}Please reboot your Raspberry Pi to apply all changes:${NC}"
echo -e "${GREEN}sudo reboot${NC}"
