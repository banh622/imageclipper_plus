Image Clipper Plus
-------------

This is a variation of the [imageclipper](https://code.google.com/p/imageclipper/)
program initially written by Naotoshi Seo.

I made this program so that I could draw many boxes on one image as well as boxes for
different objects. For example I want to draw a box for a person's face and eyes at the same
time.

## Building

To build you need [OpenCV](http://opencv.org/) and [Python](https://www.python.org/)
on your system. I created using opencv 3.0, but it doesnt use anything new from previous versions.

TODO: Remove the packages dependency on opencv

### Install

Build the repo using the following command:

```bash
$ git clone <repo url>
```

### Usage

To use the code, go to the directory that it is installed, then simply run:

```bash
$ python imageclipper_plus.py 'path/to/images/'
```

You can also see how to use the program and all the options with:

```bash
$ python imageclipper_plus.py --help
```

Once the program is run from the command line, a window will open with the first image. You will have to
press tab initially for keyboard functionality. For some reason the initial tab is needed to select the canvas.
The following commands and their usage are found both in the help function and summarized below:

**Right Click:** Draw a box<br />
**Left Click:** If inside a box, moves the box; if close to the border, re-sizes the box.<br />
**Tab:** Iterates through the object types.<br />
**Space:** Saves all the drawn boxes for the image displayed.<br />
**./>:** Go to the next image in the directory.<br />
**,/<:** Go to the previous image in the directory.<br />
**Right Arrow:** Move all boxes right.<br />
**Up Arrow:** Move all boxes up.<br />
**Down Arrow:** Move all boxes down.<br />
**Left Arrow:** Move all boxes left.<br />
**Delete:** Removes all drawn boxes.