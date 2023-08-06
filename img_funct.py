from PIL import Image

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

    @staticmethod
    def display_color2(path, lower, upper):
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