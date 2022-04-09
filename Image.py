#The data encoding is based on Run-length encoding(see https://en.wikipedia.org/wiki/Run-length_encoding)
from PIL import Image, ImageFilter, ImageOps 
from numpy import asarray 
from math import floor 
from tkinter import filedialog, Tk  
import os

#CONFIGURATIONS
height = 80 #result height
width = 80 #result width
maintainAspectRatio = True #if set to true the shape of the image wont change
maxValue = 7 #number of different characters used for video visualization(max is 7), for a black-white result use 2

TkUI = Tk() 
TkUI.withdraw() #remove tk gui

image_extensions = ("*.jpeg", "*.jpg", "*.png", "*.tiff", "*.svg", "*.webp")
if not os.path.isdir("INPUTS"): os.mkdir("INPUTS") #create the inputs folder if it doesn't exist
IMAGE_PATH = filedialog.askopenfilename(title = "Open", initialdir = "INPUTS", filetypes = [("All image types", image_extensions), ("All types", "*.")])

if IMAGE_PATH == "": #if an image isn't given, exit early
    print("No image location given!")
    exit()

#open the image using pillow and convert it to grayscale because only use the pixels brightness
image = ImageOps.grayscale(Image.open(IMAGE_PATH))

if maintainAspectRatio: #with respect to height 
    aspect_ratio = image.width/image.height #compute the image aspect ratio
    width = height*aspect_ratio 

#round the values to integers
width = round(width) #apply aspect ratio if set to true
height = round(height/2) #set the height to half because glwssa console text ratio is 2:1

#resize the image and apply sharpen to remove unnecessary details
image = image.resize((width, height), Image.LANCZOS).filter(ImageFilter.SHARPEN)

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

encodedData = "" #used to store the large string of data which will be cut to smaller ones later on

data = asarray(image.getdata()) #grabbing the pixel data
   
lastvalue = getValue(data[0]) #temporary variable to store the value of the last checked pixel(so we can calculate streaks)
index = 0 #index for the streaks array

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
    encodedData += str(values[index])
    #a separator value(8) between value and streaks isn't needed(because the value length is always equal to 1) 
    #converting the number from base-10 to base-8 to filter out magic characters(8, 9)
    encodedData += reverseNumberToBase(streak, 8) #the result is reversed to avoid calculating the number length during unpack
    #adding a separator(8) after the streak, because streaks can have any length and we need to know where the next pixel is
    encodedData += "8"

#add the metadata used by the .glo file
result = "σειρές <- "+str(floor(len(encodedData)/19)+1)+"\n"
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
IMAGE_NAME = os.path.basename(IMAGE_PATH)
OUTPUT_NAME = os.path.splitext(IMAGE_NAME)[0]+str(maxValue)+"(image)"
if not os.path.isdir("OUTPUTS"): os.mkdir("OUTPUTS") #create the outputs folder if it doesn't exist
OUTPUT_FILE = filedialog.asksaveasfile(mode = "w", title = "Save As", initialdir = "OUTPUTS", initialfile = OUTPUT_NAME, defaultextension = ".txt", filetypes = [("Text Document", "*.txt")])

#write result to the output file
if OUTPUT_FILE: 
    OUTPUT_FILE.write(result) 
    OUTPUT_FILE.close() 
    print("Glwssa "+IMAGE_NAME+" array saved to "+os.path.basename(OUTPUT_FILE.name)+"!")
else:
    print("No output location was given!")
    exit() 
