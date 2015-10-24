import random
import os
import sys
import shutil
import itertools as it
from imagecrop import ImageCrop
import argparse


def main(argv):

    parser = argparse.ArgumentParser(
        description='This is a tool put together for the use of cropping and tagging images to be used in\n'
                    'training image recognition algorithms. It is especially useful for sequential images\n'
                    'produced from video. The software lets the user draw multiple boxes for multiple object\n'
                    'types. The boxes will be drawn in different colors.\n'
                    '\n'
                    'Basic Usage:\n'
                    'Right Click: Draw a box\n'
                    'Left Click: If inside a box, moves the box; if close to the border, re-sizes the box\n'
                    'Tab: Iterates through the object types.\n'
                    'Space: Saves all the drawn boxes for the image displayed.\n'
                    'Right Arrow: Go to the next image in the directory.\n'
                    'Left Arrow: Go to the previous image in the directory.\n'
                    'Delete: Removes all drawn boxes',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        'image_dir',
        help='Location of the directory with the images to be cropped.'
    )
    parser.add_argument(
        '--output_dir',
        default='cropped_output',
        help='Directory where the cropped images should be output. It defaults to an extension of the supplied\n'
             'image directory'
    )
    parser.add_argument(
        '--object_list',
        default='Object',
        help='List of objects that the images may contain.'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Option to overwrite the output directory completely.'
    )

    args = parser.parse_args()

    # Convert the string input argument into an array.
    object_list = [s for s in args.object_list.split(',')]

    # Create the default directory or take in the input directory.
    if args.output_dir == 'cropped_output':
        output_directory = os.path.join(args.image_dir, 'cropped_output/')
    else:
        output_directory = args.output_dir

    # If overwrite is an option, remove the output directory that currently exists
    if args.overwrite:
        shutil.rmtree(output_directory)

    # Parse through the images in the directory provided
    images = []
    for file in os.listdir(args.image_dir):
        if file.endswith(".jpg"):
            images.append(args.image_dir + file)

    # Create a random color for each object to use while drawing boxes.
    r = lambda: random.randint(0, 255)
    color_list = []
    for i in range(0, len(object_list)):
        color_list.append('#%02X%02X%02X' % (r(), r(), r()))

    # Create the cycle iterables for objects and colors
    objects = it.cycle(object_list)
    colors = it.cycle(color_list)

    # Iterates through the objects and makes a folder in the output directory
    for file in object_list:
        if not os.path.exists(output_directory + '/' + file):
            os.makedirs(output_directory + '/' + file)

    app = ImageCrop(objects, object_list, colors, images, output_directory)
    app.mainloop()

if __name__ == '__main__':
    main(sys.argv)