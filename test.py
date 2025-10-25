import sys
import time

def test_time_size():
    current_time = int(time.time())
    size_in_bytes = sys.getsizeof(current_time)
    print(f"time.time() value: {current_time}")
    print(f"Size needed: {size_in_bytes} bytes")
    print(f"Number type: {type(current_time)}")

test_time_size()