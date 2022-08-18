from MainLib import video_to_glo, Metadata
from moviepy.editor import VideoFileClip, vfx  
import FileLib, os

#configurations
metadata = Metadata(
    width = 80,
    height = 80,
    maintain_ratio = True,
    max_value = 7,
    fps = 5
)

def main():
    #chose the video path
    VIDEO_PATH = FileLib.chose_input(True) 
    #open the video using moviepy
    video = VideoFileClip(VIDEO_PATH) 
    #force the video aspect ratio if set
    if metadata.MAINTAIN_ASPECT_RATIO: metadata.WIDTH = round(metadata.HEIGHT*video.aspect_ratio)
    #set the video properties
    video = video.set_fps(metadata.FPS).resize((metadata.WIDTH, round(metadata.HEIGHT/2))).fx(vfx.blackwhite)
    #store the name for later use
    metadata.name = os.path.basename(VIDEO_PATH) 
    #convert the video to a .glo array
    result = video_to_glo(video, metadata)
    #chose the output
    output = FileLib.chose_output(os.path.splitext(metadata.name)[0]+str(metadata.FPS), True)
    #write to the output
    FileLib.write_output(output, result, metadata)

if __name__ == "__main__":
    main()
