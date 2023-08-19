from PIL import Image, ImageFilter

import os
from skimage import io
import cv2
import numpy as np
from scipy import ndimage as nd


class img_class:
    def __init__(self, app, access, file_name):
        """Init function

        app - Flask.app
        access - variable that determinate if program can generate work page without form
        file_name - variable that holds name of file
        temp_file - array that will be created automatically and will have temp file names so script can delete it after
        using it
        """

        self.app = app
        self.access = access
        self.file_name = file_name
        self.temp_file = []

    def __repr__(self):
        return f'App: {self.app}'

    def get_image_size(self, file_name, extension):
        """Function that creates file in temp and returning size of it in specific format


        file_name = name of file
        extension = extension of file

        Function returns string with size of image in MB"""

        path_input = os.path.join(self.app.root_path, 'static', 'download', 'modified', file_name)

        # Splitting file extension and file name
        file_without_ex = file_name.split('.')[0]

        # Creating desire path with specific extension
        path_output = os.path.join(self.app.root_path, 'static', 'download', 'temp', file_without_ex + '.' + extension)

        # Opening file and saving in temporary directory
        img = Image.open(path_input)

        # Checking if extension its jpg
        if extension == 'jpg':
            # Removing alpha canal for jpg
            img = img.convert("RGB")

        # Saving file and ifts jpg changing temporary name to jpeg because PIL uses that name
        img.save(path_output, format=extension.casefold().replace('jpg', 'jpeg'))

        # Calculating size in Mega byte
        file_size_bytes = os.path.getsize(path_output)
        file_size_mb = file_size_bytes / (1024 * 1024)

        self.temp_file.append(path_output)
        return f'{file_size_mb:.2}MB'

    def delete_temp(self):
        """ Function to delete temp files. Paths to that files is stored in instance of class.
        Function return nothing"""

        # Deleting every temporary file that path is saved in list
        for i in self.temp_file:
            os.remove(i)

        # clearing list with path to temp files
        self.temp_file = []


    def filter_funct(self, method, file_name):
        """Function to change appearance of image
        Function opens file in app.root_path/static/download/original/file_name and save a result in
        app.root_path/static/download/modified/file_name

        method - method of changing appearance of image, for example convert('L'), must be given as string
        file_name - name of image to metamorphose

        """

        path = os.path.join(self.app.root_path, 'static', 'download', 'original', file_name)

        string = f"np.array(Image.open(path).{method})"
        img = eval(string)

        img_class.save_img(img, path.replace('original', 'modified'))

    @staticmethod
    def save_img(img, path):
        """Function to save img in delivered path

        img - image obj to save
        path - path where to save image
        """

        pil_img = Image.fromarray(img)
        pil_img.save(path)

    @staticmethod
    def display_color(path, lower, upper):
        """Function to display only specific color in image

        path - path to image
        lower - hsv lower range for color
        upper - hsv upper range for color

        Function returns image with everything black except for specific color"""

        img = io.imread(path)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        closed_mask = nd.binary_closing(mask, np.ones((7, 7)))

        result = cv2.bitwise_and(img, img, mask=mask)
        return result
