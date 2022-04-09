#The data encoding is based on Run-length encoding(see https://en.wikipedia.org/wiki/Run-length_encoding)
from PIL import Image, ImageFilter, ImageOps 
from moviepy.editor import VideoFileClip 
from numpy import asarray 
from math import floor 
from sys import stdout 
from tkinter import filedialog, Tk  
import os

#CONFIGURATIONS
fps = 5 #frames per second 
height = 80 #result height
width = 80 #result width
maintainAspectRatio = True #if set to true the shape of the video wont change
maxValue = 7 #number of different characters used for video visualization(max is 7), for a black-white result use 2

TkUI = Tk() 
TkUI.withdraw() #remove tk gui

video_extensions = ("*.mp4", "*.mov", "*.wmv", "*.webm", "*.avi", "*.flv", "*.mkv")
if not os.path.isdir("INPUTS"): os.mkdir("INPUTS") #create the inputs folder if it doesn't exist
VIDEO_PATH = filedialog.askopenfilename(title = "Open", initialdir = "INPUTS", filetypes = [("All video types", video_extensions), ("All types", "*.")])

if VIDEO_PATH == "": #if a video isn't given, exit early
    print("No video location given!")
    exit()
else:
    clip = VideoFileClip(VIDEO_PATH).set_fps(fps) #open the video using moviepy

if maintainAspectRatio: #with respect to height
    width = height*clip.aspect_ratio

#round the values to integers
width = round(width) 
height = round(height/2) #set the height to half because glwssa console text ratio is 2:1

#clear the console
if os.name == "nt":
    os.system("cls") #windows 
else:
    os.system("clear") #mac/linux

lastMessageLength = 0 
def displayMessage(text):
    global lastMessageLength
    #using stdout.write("\b") instead of os.system("cls") to avoid flickering/blinking of text
    stdout.write("\b"*lastMessageLength+text)
    diff = lastMessageLength-len(text)
    stdout.write(" "*(diff-1))
    lastMessageLength = len(text)+1

VIDEO_NAME = os.path.basename(VIDEO_PATH) #get video name from full path
print("Converting: "+VIDEO_NAME+" [WIDTH = "+str(width)+" | HEIGHT = "+str(height*2)+" | FPS = "+str(fps)+" | CHARS = "+str(maxValue)+"]")

clip = clip.resize((width, height)) #resize the clip

#modified from https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base
def reverseNumberToBase(n, b):
    if n == 0: return "0"
    digits = ""
    while n:
        digits += str(n % b) 
        n //= b 
    return digits

#round the number to an integer between 1 and maxValue 
def getValue(pixel):
    return round(pixel*(maxValue-1)/255)+1 

#used to calculate the average iterations
iterations = 0 
times = 0

frames_appr = int(clip.fps*clip.duration) #frames approximation(used for the loading bar) 
encodedData = "" #stores the large string of data which will be cut to smaller ones later on
lastImage = "" #stores the previous image string data
current_frame = 0
for image in clip.iter_frames(): #looping through each frame 
    #open the image using pillow, convert it to grayscale because only use the pixels brightness is used and apply sharpen to remove unnecessary details 
    image = ImageOps.grayscale(Image.fromarray(image)).filter(ImageFilter.SHARPEN)
    data = asarray(image.getdata()) #grabbing the pixel data
   
    lastvalue = getValue(data[0]) #temporary variable to store the value of the last checked pixel(so we can calculate streaks)
    index = 0 #index for the streaks array

    encodedImageData = "" #stores the current image string data

    values = [lastvalue] #values is a number between 1 and 7 depending on the pixel brightness
    streaks = [1] #streaks are the amount of the same pixel in a row 
    for pixel in data[1:]: #loop through every pixel
        value = getValue(pixel)
        if value == lastvalue: 
            streaks[index] += 1 
        else:
            index += 1 #incrementing the streaks index(basically start a new streak)
            lastvalue = value #updating the old pixel value
            values.append(value) 
            streaks.append(1)

    #converting the streaks and values data into a large sequence of numbers
    for index, streak in enumerate(streaks):
        #updating the average iteration values
        iterations += streak 
        times += 1
        encodedImageData += str(values[index])
        #a separator value(8) between value and streaks isn't needed(because the value length is always equal to 1) 
        #converting the number from base-10 to base-8 to filter out magic characters(8, 9)
        encodedImageData += reverseNumberToBase(streak, 8) #the result is reversed to avoid calculating the number length during unpack
        #adding a separator(8) after the streak, because streaks can have any length and we need to know where the next pixel is
        encodedImageData += "8"
    #only include the image data if it's different than the last, else just add a 9
    if encodedImageData != lastImage: 
        encodedData += encodedImageData  
    #if the 19 digit number starts with a 9, we add an 8 infront to avoid hitting the number cap(9,223,372,036,854,775,807)
    if len(encodedData) % 19 == 18: 
        encodedData += "8"
    encodedData += "9" #9 is used to split each image 
    lastImage = encodedImageData 
    #update the loading bar state once per 10 frames
    if current_frame % 10 == 0 or current_frame >= frames_appr:
        percentage = current_frame/frames_appr
        bar_length = 50
        current = round(percentage*bar_length)
        displayMessage("finished: ["+"#"*current+"-"*(bar_length-current)+"] "+str(round(percentage*10000)/100)+"%")
    current_frame += 1 

#add the metadata used by the .glo file
result = "σειρές <- "+str(floor(len(encodedData)/19)+1)+"\n"
result += "συνολικές_εικόνες <- "+str(current_frame)+"\n"
result += "φπσ <- "+str(fps)+"\n"
result += "ύψος <- "+str(height)+"\n"
result += "μήκος <- "+str(width)+"\n"
result += "ΜΟεπαναλήψεων <- "+str(round(iterations/times))+"\n"
result += "σχ <- "+str(maxValue)+" !σύνολο χαρακτήρων\n\n" 

#loop through the text containing all the digits
for i in range(0, len(encodedData), 19): 
    chunk = encodedData[i:i+19] #cut it into 19 digit numbers
    #the numbers get reversed to remove complexity of power calculations(^) during unpack
    result += "Α["+str(floor(i/19)+1)+"]<-"+chunk[::-1]+"\n"

#open the output file
TkUI.deiconify() #unhide the tkUI due to a bug where sometimes the save prompt wont show
OUTPUT_NAME = os.path.splitext(VIDEO_NAME)[0]+str(fps)+"(video)"
if not os.path.isdir("OUTPUTS"): os.mkdir("OUTPUTS") #create the outputs folder if it doesn't exist
OUTPUT_FILE = filedialog.asksaveasfile(mode = "w", title = "Save As", initialdir = "OUTPUTS", initialfile = OUTPUT_NAME, defaultextension = ".txt", filetypes = [("Text Document", "*.txt")])
TkUI.withdraw() #after the user selects the save path, hide it again


#write result to the output file
if OUTPUT_FILE: 
    OUTPUT_FILE.write(result) 
    OUTPUT_FILE.close() 
    displayMessage("Glwssa "+VIDEO_NAME+" array saved to "+os.path.basename(OUTPUT_FILE.name)+"!")
else:
    displayMessage("No output location was given!")
    exit() 