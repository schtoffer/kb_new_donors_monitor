# Raspberry Pi Quick Start Guide

This guide provides simplified instructions for getting the KB FG Monitor running on a Raspberry Pi.

## Quick Setup

1. Clone the repository (or pull the latest changes):
   ```bash
   cd ~
   git clone https://github.com/schtoffer/kb_new_donors_monitor.git kb_fg_monitor
   # OR if already cloned:
   # cd ~/kb_fg_monitor
   # git pull
   ```

2. Make the scripts executable:
   ```bash
   cd ~/kb_fg_monitor
   chmod +x test_flask.sh hide_cursor.sh
   ```

3. Set up cron jobs for auto-start:
   ```bash
   crontab -e
   ```
   
   Add these lines:
   ```
   @reboot sleep 30 && /home/pi/kb_fg_monitor/test_flask.sh &
   @reboot sleep 10 && /home/pi/kb_fg_monitor/hide_cursor.sh &
   ```

4. Set up browser autostart:
   ```bash
   mkdir -p ~/.config/autostart
   nano ~/.config/autostart/kb-browser.desktop
   ```
   
   Add this content:
   ```
   [Desktop Entry]
   Type=Application
   Name=KB Browser
   Exec=/bin/bash -c "sleep 45 && chromium-browser --noerrdialogs --disable-infobars --kiosk http://localhost:5000"
   X-GNOME-Autostart-enabled=true
   ```

5. Disable screen blanking:
   ```bash
   sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
   ```
   
   Add these lines at the end:
   ```
   @xset s off
   @xset -dpms
   @xset s noblank
   ```

6. Reboot:
   ```bash
   sudo reboot
   ```

## Troubleshooting

If the application doesn't start:

1. Check if the Flask app is running:
   ```bash
   ps aux | grep python
   ```

2. Check the log file:
   ```bash
   cat ~/flask.log
   ```

3. Try running the Flask app manually:
   ```bash
   cd ~/kb_fg_monitor
   source venv/bin/activate
   python app.py
   ```

4. If the cursor is still visible, run:
   ```bash
   DISPLAY=:0 unclutter -idle 0 -root &
   ```

## Display Schedule

The display will turn off at 5 PM and turn on at 7 AM. To set this up:

```bash
nano ~/kb_fg_monitor/display_off.sh
```
Add: `vcgencmd display_power 0`

```bash
nano ~/kb_fg_monitor/display_on.sh
```
Add: `vcgencmd display_power 1`

Make them executable:
```bash
chmod +x ~/kb_fg_monitor/display_*.sh
```

Add to crontab:
```
0 17 * * * /home/pi/kb_fg_monitor/display_off.sh
0 7 * * * /home/pi/kb_fg_monitor/display_on.sh
```
