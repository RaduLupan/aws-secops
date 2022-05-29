from datetime import datetime

now=datetime.now()

now_str=now.strftime("%Y-%m-%d-%H-%M-%S")

print(f"Today's date and time: {now_str}")
