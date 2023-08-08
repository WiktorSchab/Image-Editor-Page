from PIL import Image

import os
from skimage import io
import cv2
import numpy as np
from scipy import ndimage as nd


class img_class:
    @staticmethod
    def save_img(img, path):
        """Function to save img in delivered path"""
        pil_img = Image.fromarray(img)
        pil_img.save(path)

    @staticmethod
    def get_image_size(app, file_name, extension):
        """Function that creates file in temp and returning size of it in specific format

        app - app = Flask(__name__)
        file_name = name of file
        extension = extension of file

        Function returns string with size of image in MB"""

        path_input = os.path.join(app.root_path, 'static', 'download', 'modified', file_name)

        # Spliting file extension and file name
        file_without_ex = file_name.split('.')[0]

        # Creating desire path with specific extension
        path_output = os.path.join(app.root_path, 'static', 'download', 'temp', file_without_ex + '.' + extension)


        # Opening file and saving in in temporary directory
        img = Image.open(path_input)
        img.save(path_output)

        # Calculating size in Mega byte
        file_size_bytes = os.path.getsize(path_output)
        file_size_mb = file_size_bytes / (1024 * 1024)
        return f'{file_size_mb:.2}MB'

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