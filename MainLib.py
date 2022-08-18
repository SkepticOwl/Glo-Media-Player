#The data encoding is based on Run-length encoding(see https://en.wikipedia.org/wiki/Run-length_encoding)
from numpy import asarray 
from math import floor 
import PrintLib

#class representing the metadata used to produce image and video text outputs(the uppercase variables are user input)
class Metadata:
    def __init__(self, width = 80, height = 80, maintain_ratio = True, max_value = 7, requires_string_concat = True, fps = 5):
        assert max_value >= 1 or max_value <= 7, "max value must be between 1 and 7"
        assert height > 0 and width > 0, "height and width must be above 0"
        self.HEIGHT = round(height) 
        self.WIDTH = round(width)
        self.MAINTAIN_ASPECT_RATIO = bool(maintain_ratio)
        self.MAX_VALUE = max_value 
        assert fps > 0, "fps must be above 0"
        self.FPS = fps 
        self.REQUIRES_CONCAT = bool(requires_string_concat) 
    is_video = False 
    iterations = 0
    times = 0
    rows = 0
    name = "" 

#class representing image pixels(made out of values and the amount of times they repeat in a row)
class Pixel: 
    def __init__(self, value): self.value = value
    repeats = 1

#modified from https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base
#all the numbers passed to the function are integers and >= 1
def reverse_number_to_base(num, base):
    digits = ""
    while num:
        digits += str(num % base)
        num //= base 
    return digits

#receives a flat array of an image that contains every pixel brightness from 0 to 255
#returns an array of pixels with values between 1 and 7 and how many times they repeat in a row
def get_pixels(pixel_data, max_value):
    last_value = None
    pixels = []
    for pixel in pixel_data:
        value = round(pixel*(max_value-1)/255)+1 
        if value == last_value: 
            pixels[len(pixels)-1].repeats += 1
        else:
            last_value = value 
            pixels.append(Pixel(value))
    return pixels 

#receives the custom Metadata class
#returns the .glo metadata as text
def add_metadata(metadata):
    result = f"σειρές <- {metadata.rows}\n"
    if metadata.is_video:
        result += f"συνολικές_εικόνες <- {metadata.frames}\n"
        result += f"φπσ <- {metadata.FPS}\n"
    result += f"ύψος <- {metadata.HEIGHT}\n"
    result += f"μήκος <- {metadata.WIDTH}\n"
    result += f"σχ <- {metadata.MAX_VALUE} !σύνολο χαρακτήρων\n\n"
    if metadata.is_video:
        for index, max_value in enumerate(metadata.max_values): 
            result += f"ΜΕΓ[{index+1}] <- {max_value}\n"
        result += "\n"
    else: result += f"ΜΟεπαναλήψεων <- {round(metadata.iterations/metadata.times)}\n"
    return result 

#receives a flat array of an image that contains every pixel brightness from 0 to 255
#returns the encoded pixel data of the image as a large string of numbers
def image_to_numbers(pixel_data, metadata):
    encoded_data = "" 
    for pixel in get_pixels(pixel_data, metadata.MAX_VALUE):
        #updating the average iteration values
        metadata.iterations += pixel.repeats
        metadata.times += 1
        #updating the max repeats of the pixel found in the image data(used for videos)
        if metadata.is_video and pixel.repeats > metadata.max_values[pixel.value-1]:
            metadata.max_values[pixel.value-1] = pixel.repeats
        #adding the new pixel to the image string
        encoded_data += f"{pixel.value}{reverse_number_to_base(pixel.repeats, 8)}8"
    return encoded_data 

#receives encoded pixel data of video/image as large string of numbers
#returns .glo metadata and encoded pixel data as an array of numbers
def to_glo_data(encoded_data, metadata):
    #add the metadata used by the .glo file
    metadata.rows = floor(len(encoded_data)/19+1)
    data = add_metadata(metadata)  
    #loop through the text containing all the digits
    for i in range(0, len(encoded_data), 19):
        data += f"Α[{floor(i/19)+1}] <- {encoded_data[i:i+19][::-1]}\n"
    #remove the last newline character and return the result
    return data[:-1]

#receives a grayscale pillow image
#returns the .glo metadata and array of the image
def image_to_glo(image, metadata):
    pixel_data = asarray(image.getdata())
    encoded_data = image_to_numbers(pixel_data, metadata) 
    return to_glo_data(encoded_data, metadata)

#receives a grayscale moviepy VideoFileClip
#returns the .glo metadata and array of the video
def video_to_glo(video, metadata):
    metadata.is_video = True 
    metadata.max_values = [0]*metadata.MAX_VALUE
    metadata.frames = 0
    frames_approximation = int(video.fps*video.duration)
    encoded_data = ""
    last_image = ""
    current_frame = 0
    PrintLib.clear_console() 
    print(f"Converting: {metadata.name} [WIDTH = {metadata.WIDTH} | HEIGHT = {metadata.HEIGHT} | FPS = {metadata.FPS} | CHARS = {metadata.MAX_VALUE}]")
    for frame in video.iter_frames():
        pixel_data = frame.flatten()[::3]
        image = image_to_numbers(pixel_data, metadata)
        #only include the frame data if it's different than the last, else just add a 9
        if image != last_image: encoded_data += image  
        last_image = image  
        #if the 19 digit number starts with a 9, we add an 8 infront to avoid hitting the number cap(9,223,372,036,854,775,807)
        if len(encoded_data) % 19 == 18: encoded_data += "8"
        encoded_data += "9" #9 is used to split each image 
        #update the loading bar state once per 10 frames
        if current_frame % 10 == 0 or current_frame >= frames_approximation:
            percentage = current_frame/frames_approximation
            bar_length = 50
            current = round(percentage*bar_length)
            PrintLib.display_message(f"finished: [{'#'*current}{'-'*(bar_length-current)}] {round(percentage*10000)/100}%")
        current_frame += 1
    metadata.frames = current_frame 
    return to_glo_data(encoded_data, metadata) 