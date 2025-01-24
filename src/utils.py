import os
import re
import sys

from datetime import datetime

class LogsTee():
    def __init__(self, name, mode='a+'):
        self.file = open(name, mode)
        self.stdout = sys.stdout
    
    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)
        self.flush()

    def flush(self):
        self.stdout.flush()
        self.file.flush()

def get_logs_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"logs_{timestamp}.txt"

def is_directory(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)
    
def list_files(path):
    return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def list_directories(path):
    return [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

def input_confirmation(message):
    return input(message + ' [y/n]: ').lower() == 'y'

def input_positive_number(message):
    message = message + ': '
    validate_input = lambda x: x.isdigit() and 0 <= int(x) <= 9999
    user_input = input(message)
    while not validate_input(user_input):
        print('Invalid input. ', end='')
        user_input = input(message)
    return int(user_input)

def ensure_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)