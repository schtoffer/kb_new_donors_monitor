# Setting Up KB FG Monitor on Raspberry Pi

This guide explains how to set up your KB FG Monitor Flask application to run automatically at startup on a Raspberry Pi, display the interface in full-screen mode, and automatically turn the display on/off according to a schedule.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS installed (Bullseye or newer recommended)
- Your KB FG Monitor application files transferred to the Pi
- Python 3.7+ installed on the Pi
- Internet connection for the Pi
- HDMI display connected to the Pi

## Setup Instructions

### 1. Install Required Packages

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv xdotool unclutter cron
```

### 2. Set Up the Application

```bash
# Create a directory for the application
mkdir -p ~/kb_fg_monitor

# Copy your application files to the Raspberry Pi or clone from repository
# Example using scp from your computer:
# scp -r /path/to/kb_fg_monitor/* pi@raspberry_pi_ip:~/kb_fg_monitor/

# Navigate to the application directory
cd ~/kb_fg_monitor

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create Startup Script

Create a script that will start the Flask application and open it in the browser in full-screen mode:

```bash
cat > ~/kb_fg_monitor/start_dashboard.sh << 'EOF'
#!/bin/bash

# Change to the application directory
cd /home/pi/kb_fg_monitor

# Activate the virtual environment
source venv/bin/activate

# Start the Flask application in the background
python app.py &

# Wait for the server to start
sleep 5

# Start Chromium in kiosk mode (full screen)
chromium-browser --noerrdialogs --disable-infobars --kiosk http://localhost:5001 &

# Hide the mouse cursor after 3 seconds of inactivity
unclutter -idle 3 &
EOF

# Make the script executable
chmod +x ~/kb_fg_monitor/start_dashboard.sh
```

### 4. Configure Autostart at Boot

Create an autostart entry to run the dashboard at system startup:

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/kb_dashboard.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=KB Dashboard
Exec=/home/pi/kb_fg_monitor/start_dashboard.sh
X-GNOME-Autostart-enabled=true
EOF
```

### 5. Set Up Display Schedule (Off at 5 PM, On at 7 AM)

Create scripts to turn the display on and off:

```bash
# Create script to turn display off
cat > ~/kb_fg_monitor/display_off.sh << 'EOF'
#!/bin/bash
vcgencmd display_power 0
EOF

# Create script to turn display on
cat > ~/kb_fg_monitor/display_on.sh << 'EOF'
#!/bin/bash
vcgencmd display_power 1
EOF

# Make the scripts executable
chmod +x ~/kb_fg_monitor/display_off.sh
chmod +x ~/kb_fg_monitor/display_on.sh
```

Set up cron jobs to schedule display on/off times:

```bash
# Open crontab for editing
crontab -e
```

Add these lines to the crontab file:

```
# Turn display off at 5 PM (17:00)
0 17 * * * /home/pi/kb_fg_monitor/display_off.sh

# Turn display on at 7 AM (07:00)
0 7 * * * /home/pi/kb_fg_monitor/display_on.sh
```

### 6. Optional: Disable Screen Blanking

To prevent the screen from blanking during the day:

```bash
# Edit the autostart file
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add these lines:

```
@xset s off
@xset -dpms
@xset s noblank
```

### 7. Reboot to Test

```bash
sudo reboot
```

## Troubleshooting

### Common Issues and Solutions

#### Flask Application Doesn't Start

```bash
# Check the application logs
cd ~/kb_fg_monitor
cat flask_app.log

# Ensure all dependencies are installed
source venv/bin/activate
pip install -r requirements.txt
```

#### Display Doesn't Turn Off/On as Scheduled

```bash
# Check if cron is running
sudo service cron status

# Check cron logs
grep CRON /var/log/syslog

# Test the display scripts manually
~/kb_fg_monitor/display_off.sh  # Should turn display off
~/kb_fg_monitor/display_on.sh   # Should turn display on
```

#### Browser Doesn't Start in Full-Screen Mode

```bash
# Check if Chromium is installed
which chromium-browser

# If not found, install it
sudo apt install -y chromium-browser

# Try running the browser manually
chromium-browser --kiosk http://localhost:5001
```

#### Screen Goes Blank During the Day

Edit the LXDE autostart file:

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Ensure these lines are present:

```
@xset s off
@xset -dpms
@xset s noblank
```

### Alternative Setup Options

#### Option 1: Using Systemd Service

1. Transfer both the `flask-monitor.service` and `setup_raspberry_pi.sh` files to your Raspberry Pi.

2. Make the setup script executable:
   ```bash
   chmod +x setup_raspberry_pi.sh
   ```

3. Run the setup script with sudo:
   ```bash
   sudo ./setup_raspberry_pi.sh
   ```

4. Reboot your Raspberry Pi:
   ```bash
   sudo reboot
   ```

### Option 2: Manual Setup

If you prefer to set things up manually, follow these steps:

1. **Set a Static IP Address**:
   
   Edit the dhcpcd configuration file:
   ```bash
   sudo nano /etc/dhcpcd.conf
   ```
   
   Add the following at the end of the file (adjust according to your network):
   ```
   interface eth0  # or wlan0 if using WiFi
   static ip_address=192.168.4.248/24
   static routers=192.168.4.1
   static domain_name_servers=192.168.4.1 8.8.8.8
   ```

2. **Install the Systemd Service**:
   
   Copy the service file to the systemd directory:
   ```bash
   sudo cp flask-monitor.service /etc/systemd/system/
   ```

3. **Enable and Start the Service**:
   ```bash
   sudo systemctl enable flask-monitor.service
   sudo systemctl start flask-monitor.service
   ```

4. **Open the Firewall Port** (if using ufw):
   ```bash
   sudo ufw allow 5000/tcp
   ```

5. **Reboot the Raspberry Pi**:
   ```bash
   sudo reboot
   ```

## Verifying the Setup

After rebooting, your Flask application should be running and accessible at:
```
http://192.168.4.248:5000
```

To check the status of the service:
```bash
sudo systemctl status flask-monitor.service
```

## Troubleshooting

If your application isn't running properly:

1. Check the service status:
   ```bash
   sudo systemctl status flask-monitor.service
   ```

2. View the service logs:
   ```bash
   sudo journalctl -u flask-monitor.service
   ```

3. Ensure the paths in the service file match your actual installation:
   ```bash
   sudo nano /etc/systemd/system/flask-monitor.service
   ```
   
   Update the WorkingDirectory and ExecStart paths if needed, then reload:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart flask-monitor.service
   ```

## Additional Notes

- The service is configured to restart automatically if it crashes
- Make sure your app.py is configured to run on all interfaces:
  ```python
  app.run(host='0.0.0.0', port=5000, debug=False)
  ```
- For production use, consider using Gunicorn or uWSGI with Nginx instead of Flask's built-in server
