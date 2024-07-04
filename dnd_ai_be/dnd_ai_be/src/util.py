import time
from functools import wraps

CYAN = "\033[96m"
RESET = "\033[0m"  # Reset color to default

def timer():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pass
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            print(f"{func.__name__}(): {CYAN}{duration:.6f} seconds{RESET}")
            return result
        return wrapper
    return decorator

# # Usage example
# class MyClass:
#     @timer()
#     def get_context_str(self) -> str:
#         # Simulate some work
#         time.sleep(1)
#         return "Context string"

# if __name__ == '__main__':
#     # Test the decorated function
#     obj = MyClass()
#     print(obj.get_context_str())