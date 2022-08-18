from sys import stdout
import os 

def clear_console(): os.system(os.name == "nt" and "cls" or "clear")

last_message_length = 0 
def display_message(text):
    global last_message_length 
    stdout.write("\b"*last_message_length+text)
    stdout.write(" "*(last_message_length-len(text)-1))
    last_message_length = len(text)+1