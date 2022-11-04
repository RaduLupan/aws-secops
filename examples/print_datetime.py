'''
Example: How to print the datetime stamp. 
'''

from datetime import datetime

now=datetime.now()

# See the Python strftime cheatsheet https://strftime.org/ for more formatting options.
now_str=now.strftime("%Y-%m-%d-%H-%M-%S")

print(f"Today's date and time: {now_str}")
