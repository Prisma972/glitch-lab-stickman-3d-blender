"""python gpulock.py cmd args... : one render at a time on the graphics card (two at once run out of video memory).
Waits for the lock out/.gpu.lock. The holder touches the lock every minute, so only a lock left by a crashed run
(untouched for 15 min) is broken."""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kitpath

os.makedirs(kitpath.OUT, exist_ok=True)
LOCK = kitpath.OUT + '/.gpu.lock'
while True:
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        break
    except FileExistsError:
        try:
            if time.time() - os.path.getmtime(LOCK) > 900:
                os.remove(LOCK)
        except OSError:
            pass
        time.sleep(2)
try:
    p = subprocess.Popen(sys.argv[1:])
    while True:
        try:
            code = p.wait(timeout=60)
            break
        except subprocess.TimeoutExpired:
            os.utime(LOCK)
finally:
    os.close(fd)
    os.remove(LOCK)
sys.exit(code)
