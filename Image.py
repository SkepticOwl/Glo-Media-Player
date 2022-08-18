from MainLib import image_to_glo, Metadata 
from PIL import Image, ImageFilter, ImageOps 
import FileLib, os

#configurations
metadata = Metadata(
    width = 80,
    height = 80,
    maintain_ratio = True,
    max_value = 7,
    requires_string_concat = True  
)

def main():
    #chose the image path
    IMAGE_PATH = FileLib.chose_input() 
    #open the image using pillow
    image = ImageOps.grayscale(Image.open(IMAGE_PATH))
    #force the image aspect ratio if set
    if metadata.MAINTAIN_ASPECT_RATIO: metadata.WIDTH = round(metadata.HEIGHT*image.width/image.height)
    #set the image properties
    image = image.resize((metadata.WIDTH, round(metadata.HEIGHT/2)), Image.LANCZOS).filter(ImageFilter.SHARPEN)
    #store the name for later use
    metadata.name = os.path.basename(IMAGE_PATH)
    #convert the image to a .glo array
    result = image_to_glo(image, metadata)
    #chose the output
    output = FileLib.chose_output(f"{os.path.splitext(metadata.name)[0]}{metadata.MAX_VALUE}({metadata.REQUIRES_CONCAT and 'concat' or 'no_concat'})")
    #write to the output
    FileLib.write_output(output, result, metadata)

if __name__ == "__main__":
    main()
