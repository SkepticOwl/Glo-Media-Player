from tkinter import filedialog, Tk  
from PrintLib import display_message 
import os

#prompts the user to chose an image or video file(using tkinter) and returns the input path
def chose_input(is_video = False):
    if not os.path.isdir("INPUTS"): os.mkdir("INPUTS")
    if is_video: extensions = ("*.mp4", "*.mov", "*.wmv", "*.webm", "*.avi", "*.flv", "*.mkv") 
    else: extensions = ("*.jpeg", "*.jpg", "*.png", "*.tiff", "*.svg", "*.webp")
    file_type = is_video and "video" or "image"
    tk_ui = Tk() 
    tk_ui.withdraw()
    INPUT_PATH = filedialog.askopenfilename(title = "Open", initialdir = "INPUTS", filetypes = [(f"All {file_type} types", extensions), ("All types", "*.")])
    tk_ui.destroy() 
    if INPUT_PATH == "":
        print(f"No {file_type} location given!")
        exit() 
    return INPUT_PATH 

#prompts the user to create a text file and returns it
def chose_output(output_name, is_video = False):
    if not os.path.isdir("OUTPUTS"): os.mkdir("OUTPUTS")
    OUTPUT_NAME = f"{output_name}({is_video and 'video' or 'image'})"
    tk_ui = Tk() 
    #tk_ui.withdraw()
    types = [("Πρόγραμμα σε ΓΛΩΣΣΑ", "*.glo"), ("Μόνο δεδομένα", "*.txt")]
    OUTPUT_FILE = filedialog.asksaveasfile(mode = "w", title = "Save As", initialdir = "OUTPUTS", initialfile = OUTPUT_NAME, defaultextension = ".glo", filetypes = types)
    tk_ui.destroy() 
    return OUTPUT_FILE 

#receives the encoded .glo array and metadata
#returns a .glo program made out of a template
def data_to_glo(data, metadata):
    template_name = metadata.is_video and "video" or metadata.REQUIRES_CONCAT and "image" or "image_without_concat"
    with open(f"TEMPLATES/{template_name}.glo", "r", encoding = "utf-16") as file: program = file.read() 
    #remove the comment at the top of the program
    if program[0] == "!": program = program.split("\n", 1)[1] 
    to_replace = {
        "[rows]": f"[{metadata.rows}]",
        "[average]": str(round(metadata.iterations/metadata.times)+1),
        "[data]": data.replace("\n", "\n  ")
    }
    if metadata.is_video:
        to_replace["[max_value]"] = f"[{metadata.MAX_VALUE}]"
        to_replace["[frames]"] = f"[{metadata.frames+1}]"
        to_replace["[average]"] = str(metadata.WIDTH*round(metadata.HEIGHT/2)+1)
    for key, value in to_replace.items(): program = program.replace(key, value)
    return program  

#writes the result to the output file
def write_output(output, result, metadata):
    func = metadata.is_video and display_message or print 
    if output: 
        if os.path.splitext(output.name)[1] == ".glo": result = data_to_glo(result, metadata)
        output.write(result) 
        output.close() 
        func(f"Glwssa {metadata.name} array saved to {os.path.basename(output.name)}!")
    else: func("No output location was given!")