import sys
import time

def animate(text="Loading..."):
    for _ in range(4):
        for ch in "|/-\\":
            sys.stdout.write(f"\r{text} {ch}")
            sys.stdout.flush()
            time.sleep(0.1)
    print("\r", end="")