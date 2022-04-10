# ![alt text](https://sites.google.com/site/aeppbasikesepexergasiespinakon/_/rsrc/1543077082805/diermeneutes-tes-glossas/867519228d1d5325856fc61d710ded0e_XL.jpg?height=28&width=28) Glo-Media-Player

Glo Media Player is a list of scripts used to visualize video and image files in [Διερμηνευτής της ΓΛΩΣΣΑΣ](https://alkisg.mysch.gr/)(a Greek pseudo-language environment). Visualization is done by converting the file to ascii text based on the brightness of each pixel, then encoding it in a way ΓΛΩΣΣΑ understands. 

## How does encoding work?
The file encoding is based on [Run-length encoding](https://en.wikipedia.org/wiki/Run-length_encoding) getting advantage of the fact a lot of pixels are going to repeat due to the small amount of different characters supported(7 characters). Because ΓΛΩΣΣΑ doesn't support text manipulation(such as indexing text, splitting text, etc.) the only way of storing data I found was inside numbers that have a length of 19 digits(64 bit). The numbers are then stored in sequence inside an array.

### data encoding:
**image sep** = **9** (used to split images)  
**pixel sep** = **8** (used to split pixels)  

**value** = **1-7** (based on pixel brightness)  
**streak** = **a base-8 number** (amount of times the value repeats in a row)  

**pixel** = **value...reverse(streak)...pixel sep** (a sep isn't added between value and streak because value always has a length of 1)  
**image** = **pixel...pixel...pixel**  
**video** = **image...image sep...image**

Then the video/image string is cut into 19 digit numbers that are getting stored reversed. The reason the numbers with a length greater than 1 get reversed is to avoid calculating their length when using **8^current power** to decode them(since they get read from left to right). The other two rules applied to the current encoding is that **in the rare case of a 9 being at the start of a number(inside the array), an extra 8 is added infront of it(to avoid hitting the 64 bit number cap, causing the code to error)** and that **if 2 images in sequence are the same, no data is stored for the second one(just an extra 9)**. 

## How does decoding work?
The array gets read from left to right using basic div/mod operators. Then using common logic(based on the way the data is stored) values and streaks are calculated in a loop, slowly rendering the file. After the file is rendered(if it's an image it should be instant) it either shows instantly in the user console(image) or the user gets a prompt to start the animation and select the desired speed(video). 

## Tips 
If you're using the program to record a video, you should set the speed to a small amount(such as 0.2, 0.5) then speed up the video during editing, to avoid blinking of the window and text. Else if you're using the program to watch the results live you should set the speed to an amount such as 2 or 4 and increase it as the fps go up(for example 30 fps should be 10). Sadly the wait time can't be accurate due to how the pseudo-language works.
