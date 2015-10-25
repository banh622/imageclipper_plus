import Tkinter as tk
import math
# TODO: Probably a simple way to not need opencv
import cv2
import PIL
import csv
import re
from PIL import Image, ImageTk


class ImageCrop(tk.Tk):
    """
    This is the Image CropClass. It produces a Tkinter canvas that lets you draw boxes from various object
    classes. It will save them in a directory that is provided in its cropped form as well as with a csv that
    has the coordinates of the boxes on the original image. It is initalized
    """
    def __init__(self, objects, object_list, colors, images, output_dir, image_dir):
        """
        The initialization of the ImageCrop object.

        :param objects: A itertools cycle of the objects that will be found int he images
        :param object_list: A list of the objects that create the cycle mentioned above
        :param colors: A itertools cycle of the colors that correspond with the objects cycle
        :param images: A list of images to be edited
        :param output_dir: The output directory to put the cropped files and .csv files
        :return:
        """
        tk.Tk.__init__(self)
        # Initialize various parameters that need to be tracked during the session
        self.x = self.y = self.image_index = 0
        self.scale_ratio = 1.0

        # Initialize various iterables to be used
        self.object = objects.next()
        color = colors.next()
        image = images[self.image_index]

        # This dictionary is used to keep track of an item being dragged
        self._drag_data = {"x1": 0, "x2": 0, "y1": 0, "y2": 0, "x": 0, "y": 0, "item": None}

        # Setting the canvas to its max
        self.canvas = tk.Canvas(self, width=self.winfo_screenwidth(), height=self.winfo_screenheight(), cursor="cross")

        # Creating the functionality of the canvas.
        self.canvas.bind("<Tab>", lambda event, args=(objects, colors): self.on_tab(event, args))
        self.canvas.bind(".", lambda event, args=images: self.next_picture(event, args))
        self.canvas.bind(",", lambda event, args=images: self.previous_picture(event, args))
        self.canvas.bind("<space>",
                         lambda event, args=(images, object_list, output_dir, image_dir): self.save_all(event, args))
        self.canvas.bind("<BackSpace>", self.delete_all)
        self.canvas.bind("<Right>", self.move_all_right)
        self.canvas.bind("<Left>", self.move_all_left)
        self.canvas.bind("<Up>", self.move_all_up)
        self.canvas.bind("<Down>", self.move_all_down)
        self.canvas.bind("<ButtonPress-2>", self.create_rectangle)
        self.canvas.bind("<B2-Motion>", self.expand_rectangle)
        self.canvas.bind("<ButtonPress-1>", self.on_rect_button_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_rect_button_release)
        self.canvas.bind("<B1-Motion>", self.on_rect_move_press)
        self.canvas.bind("<Double-Button-1>", self.on_double_press)
        self.canvas.pack()

        # Draw the picture and initialize variables needed for drawing the rectangles
        self.rect = None
        self.rect_outline_color = color
        self.start_x = None
        self.start_y = None
        self._draw_image(image)
        self.text = self.canvas.create_text(10, 10, text=self.object, anchor='nw')

    def _draw_image(self, image_path):
        """
        Draws the image on the Canvas. It uses some logic to scale the image and keep its aspect ratio while
        also fitting all of the image on the screen.
        :param image_path: Path of the image to be drawn on the canvas.
        :return: Drawn image on the canvas
        """
        # Get the shape of the image and the shape of the canvas
        im = cv2.imread(image_path)
        image_width = im.shape[1]
        image_height = im.shape[0]
        canvas_width = self.winfo_screenwidth()
        canvas_height = self.winfo_screenheight()

        # Open the Image
        self.im = Image.open(image_path)

        # This is the logic used to scale the image and set the scale_ratio used. It will look at the minimum ratio
        # needed to scale the image to fit on the screen. At the end it will resize the image.
        if image_width > canvas_width or image_height > canvas_height:
            if float(canvas_width) / image_width >= float(canvas_height) / image_height:

                if math.floor((float(canvas_width) / image_width) * image_height) <= canvas_height:
                    imheight = int(math.floor((float(canvas_width) / image_width) * image_height))
                    imwidth = int(math.floor((float(canvas_width) / image_width) * image_width))
                    self.scale_ratio = float(canvas_width) / image_width
                else:
                    imheight = int(math.floor((float(canvas_height) / image_height) * image_height))
                    imwidth = int(math.floor((float(canvas_height) / image_height) * image_width))
                    self.scale_ratio = float(canvas_height) / image_height

            elif float(canvas_width) / image_width < float(canvas_height) / image_height:

                if math.floor((float(canvas_height) / image_height) * image_width) <= canvas_width:
                    imheight = int(math.floor((float(canvas_height) / image_height) * image_height))
                    imwidth = int(math.floor((float(canvas_height) / image_height) * image_width))
                    self.scale_ratio = float(canvas_height) / image_height
                else:
                    imheight = int(math.floor((float(canvas_width) / image_width) * image_height))
                    imwidth = int(math.floor((float(canvas_width) / image_width) * image_width))
                    self.scale_ratio = float(canvas_width) / image_width

            self.im = self.im.resize((imwidth, imheight), PIL.Image.ANTIALIAS)
        else:
            self.scale_ratio = 1

        # Draw the image
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im, state='disabled')

    def create_rectangle(self, event):
        """
        Creates a rectangle.
        :param event: Button 2 press (right click)
        :return: Rectangle object
        """
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        # create rectangle if not yet exist
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline=self.rect_outline_color,
                                                 fill=None,
                                                 width=2,
                                                 tags=['rectdrag', self.object])

    def expand_rectangle(self, event):
        """
        Expands the rectangle
        :param event: Drag after button 2 press (right click)
        :return: Scaled rectangle
        """
        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def next_picture(self, event, args):
        """
        Go to the next image in the directory. If you are at the end, keep showing the last image in the
        directory
        :param event: Right arrow press.
        :param args: The image array.
        :return: Draw the next image on the canvas.
        """
        # Iterate through the image array. If at the end, keep showing the last image.
        images = args
        if self.image_index + 1 < len(images):
            self.image_index += 1
        else:
            self.image_index = self.image_index

        image = images[self.image_index]
        self._draw_image(image)
        self.text = self.canvas.create_text(10, 10, text=self.object, anchor='nw')
        drawn_recs = self.canvas.find_withtag('rectdrag')
        for rect in drawn_recs:
            self.canvas.tag_raise(rect)

    def previous_picture(self, event, args):
        """
        Go to the previous image in the directory. If you are at the beginning, keep showing the first image in the
        directory
        :param event: Left arrow press.
        :param args: The image array.
        :return: Draw the previous image on the canvas.
        """
        # Iterate through the image array. If at the beginning, keep showing the first image.
        images = args
        if self.image_index - 1 >= 0:
            self.image_index -= 1
        else:
            self.image_index = self.image_index

        image = images[self.image_index]
        self._draw_image(image)
        self.text = self.canvas.create_text(10, 10, text=self.object, anchor='nw')
        drawn_recs = self.canvas.find_withtag('rectdrag')
        for rect in drawn_recs:
            self.canvas.tag_raise(rect)

    def save_all(self, event, args):
        """
        Iterates over all the object types and all the boxes drawn to create the cropped images and
        the csv with box coordinates. It will scale the image back up to the original size before cropping.
        :param event: Space bar
        :param args: images, object_list, output_dir = the list of images, the list of objects, the output directory
        :return: Writes all the info to the directory provided
        """
        images, object_list, output_dir, image_dir = args
        image = images[self.image_index]
        # Open the full image
        full_image = Image.open(image)
        # Iterate over the possible objects
        for object in object_list:
            # Find all the boxes with the object tag and set the directory
            object_rects = self.canvas.find_withtag(object)
            object_out_dir = output_dir + object + '/'
            # Iterate through the boxes and rescale/crop/save them
            for rect_num, rect in enumerate(object_rects):
                x1, y1, x2, y2 = self.canvas.bbox(rect)
                x1 = int(math.floor(float(x1) * 1/self.scale_ratio))
                y1 = int(math.floor(float(y1) * 1/self.scale_ratio))
                x2 = int(math.ceil(float(x2) * 1/self.scale_ratio))
                y2 = int(math.ceil(float(y2) * 1/self.scale_ratio))
                cropped_test = full_image.crop((x1, y1, x2, y2))
                cropped_test.save(object_out_dir + image.replace('.jpg', '').replace(image_dir, '') +
                                  '-' + object + '-box-' + str(rect_num) + '.jpg')
                self.write_coords(object_out_dir, image, x1, y1, x2, y2)

    def delete_all(self, event):
        """
        Deletes all the boxes drawn
        :param event: Backspace/delete pressed
        :return: Image without all the boxes
        """
        rectangle_objects = self.canvas.find_withtag('rectdrag')
        for rect in rectangle_objects:
            self.canvas.delete(rect)

    def move_all_left(self, event):
        """
        Moves all the boxes drawn left
        :param event: Left key pressed
        :return: All boxes moved a pixel to the left
        """
        rectangle_objects = self.canvas.find_withtag('rectdrag')
        for rect in rectangle_objects:
            self.canvas.move(rect, -1, 0)

    def move_all_right(self, event):
        """
        Moves all the boxes drawn right
        :param event: Right key pressed
        :return: All boxes moved a pixel to the right
        """
        rectangle_objects = self.canvas.find_withtag('rectdrag')
        for rect in rectangle_objects:
            self.canvas.move(rect, 1, 0)

    def move_all_up(self, event):
        """
        Moves all the boxes drawn up
        :param event: Up key pressed
        :return: All boxes moved a pixel up
        """
        rectangle_objects = self.canvas.find_withtag('rectdrag')
        for rect in rectangle_objects:
            self.canvas.move(rect, 0, -1)

    def move_all_down(self, event):
        """
        Moves all the boxes drawn down
        :param event: Down key pressed
        :return: All boxes moved a pixel down
        """
        rectangle_objects = self.canvas.find_withtag('rectdrag')
        for rect in rectangle_objects:
            self.canvas.move(rect, 0, 1)

    def on_rect_button_press(self, event):
        """
        Finds the box closest to the click. It can be a few pixels outside the border.
        :param event: Button 1 click (regular click)
        :return: Stores the object that is closest.
        """
        # record the item and its location
        rects = self.canvas.find_withtag('rectdrag')
        for rect in rects:
            x1, y1, x2, y2 = self.canvas.bbox(rect)
            if x1 - 3 < event.x < x2 + 3 and y1 - 3 < event.y < y2 + 3:
                self._drag_data['item'] = rect
                self._drag_data['x'] = event.x
                self._drag_data['y'] = event.y
                self._drag_data['x1'] = x1 + 1
                self._drag_data['x2'] = x2 - 1
                self._drag_data['y1'] = y1 + 1
                self._drag_data['y2'] = y2 - 1

    # This clears the dictionary once the mouse button has been released
    def on_rect_button_release(self, event):
        """
        Resets the stored box info from the original click.
        :param event: Release button 1
        """
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["x1"] = 0
        self._drag_data["y1"] = 0
        self._drag_data["x2"] = 0
        self._drag_data["y2"] = 0

    def on_rect_move_press(self, event):
        """
        This handles dragging around the box. If the cursor was clicked close to the border, the box will be
        resized. If the cursor was clicked close to the center it will move the box.
        :param event: Cursor movement after click
        :return: Moved or resized box
        """
        # This logic is used to determine if the box should be resized or moved. If the cursor is clicked
        # within 10 pixels of the line it will resize that line.
        if self._drag_data["x1"] - 3 < event.x < self._drag_data["x1"] + 3:
            self.canvas.coords(self._drag_data["item"],
                               event.x, self._drag_data["y1"],
                               self._drag_data["x2"], self._drag_data["y2"])
            self._drag_data["x1"] = event.x
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
        elif self._drag_data["x2"] + 3 > event.x > self._drag_data["x2"] - 3:
            self.canvas.coords(self._drag_data["item"],
                               self._drag_data["x1"], self._drag_data["y1"],
                               event.x, self._drag_data["y2"])
            self._drag_data["x2"] = event.x
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
        elif self._drag_data["y1"] - 3 < event.y < self._drag_data["y1"] + 3:
            self.canvas.coords(self._drag_data["item"],
                               self._drag_data["x1"], event.y,
                               self._drag_data["x2"], self._drag_data["y2"])
            self._drag_data["y1"] = event.y
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
        elif self._drag_data["y2"] + 3 > event.y > self._drag_data["y2"] - 3:
            self.canvas.coords(self._drag_data["item"],
                               self._drag_data["x1"], self._drag_data["y1"],
                               self._drag_data["x2"], event.y)
            self._drag_data["y2"] = event.y
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
        elif self._drag_data['y1'] < event.y < self._drag_data['y2'] and \
                                self._drag_data['x1'] < event.x < self._drag_data['x2']:
            # compute how much this object has moved
            delta_x = event.x - self._drag_data["x"]
            delta_y = event.y - self._drag_data["y"]
            # move the object the appropriate amount
            self.canvas.move(self._drag_data["item"], delta_x, delta_y)
            # record the new position
            self._drag_data["x"] = event.x
            self._drag_data["y"] = event.y
            self._drag_data['x1'] = self._drag_data['x1'] + delta_x
            self._drag_data['x2'] = self._drag_data['x2'] + delta_x
            self._drag_data['y1'] = self._drag_data['y1'] + delta_y
            self._drag_data['y2'] = self._drag_data['y2'] + delta_y

    def on_double_press(self, event):
        """
        Double click used to delete one box.
        :param event: Double click in a box object
        """
        rects = self.canvas.find_withtag('rectdrag')
        for rect in rects:
            x1, y1, x2, y2 = self.canvas.bbox(rect)
            if x1 < event.x < x2 and y1 < event.y < y2:
                self.canvas.delete(rect)

    def on_tab(self, event, args):
        """
        Iterate through the objects that are in the images.
        :param event: Tab button pressed on the keyboard
        :param args: objects, colors = object cycle and color cycle
        :return: Next object and color associated with it as well as updated text on the canvas
        """
        objects, colors = args
        self.object = objects.next()
        color = colors.next()
        self.canvas.itemconfig(self.text, text=self.object)
        self.rect_outline_color = color

    def write_coords(self, file_path, image, x, y, width, height):
        """
        Write the given parameters to a csv
        TODO: Check this out. I think opencv uses start x, start y, width, height, but currently I have
        it as x1, y1, x2, y2.
        :param file_path: The path to the file
        :param image: The image path
        :param x: The x coordinate
        :param y: The y coordinate
        :param width: The last x coordinate
        :param height: The last y coordinate
        :return:
        """
        with open(file_path + 'positive_coords.csv', 'a') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_writer.writerow([image, x, y, width, height])