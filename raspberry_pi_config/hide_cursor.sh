#!/bin/bash
# Kill any existing unclutter processes
pkill unclutter || true
# Start unclutter with aggressive settings
DISPLAY=:0 unclutter -idle 0 -root &
