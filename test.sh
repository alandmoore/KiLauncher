Xephyr -ac :1 &
export DISPLAY=:1
sleep 2

DISPLAY=:1 xrandr  --output default --mode 1024x768
DISPLAY=:1 openbox &
DISPLAY=:1 tint2 
#DISPLAY=:1 python kilauncher.py
