Image Clipper Plus
-------------

This is a variation of the [imageclipper](https://code.google.com/p/imageclipper/)
program initially written by Naotoshi Seo.

I made this program so that I could draw many boxes on one image as well as boxes from
different types. For example I want to draw a box for a persons face and eyes at the same
time.

## Building

To build you need [OpenCV](http://opencv.org/) and [Python]
on your system. I created using opencv 3.0, but it doesnt use anything new from previous versions.
TODO: Remove the packages dependency on opencv

### Install

And then build:

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

Once the program is run from the command line, a window will open with the first image. 
The following commands and their usage are found both in the help function and summarized below:

**Right Click:** Draw a box<br />
**Left Click:** If inside a box, moves the box; if close to the border, re-sizes the box.<br />
**Tab:** Iterates through the object types.<br />
**Space:** Saves all the drawn boxes for the image displayed.<br />
**Right Arrow:** Go to the next image in the directory.<br />
**Left Arrow:** Go to the previous image in the directory.<br />
**Delete:** Removes all drawn boxes.