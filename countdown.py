import time

print("Starting countdown...")
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)
print("Countdown complete!")
