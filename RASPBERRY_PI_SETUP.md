# Setting Up KB FG Monitor on Raspberry Pi

This guide explains how to set up your KB FG Monitor Flask application to run automatically at startup on a Raspberry Pi with a fixed IP address.

## Prerequisites

- Raspberry Pi with Raspberry Pi OS installed
- Your KB FG Monitor application files transferred to the Pi
- Python and virtual environment set up on the Pi

## Setup Instructions

### Option 1: Using the Automated Setup Script

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
