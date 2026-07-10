import sys
import time

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "now":
        print(time.time())
    elif len(sys.argv) == 3 and sys.argv[1] == "elapsed":
        start = float(sys.argv[2])
        print(f"{time.time() - start:.4f}")
    else:
        print("Usage: python stopwatch.py now | elapsed <timestamp>")
