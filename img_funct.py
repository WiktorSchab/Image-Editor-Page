from PIL import Image, ImageFilter
from flask import session, flash

from skimage import io
import cv2
import numpy as np
from scipy import ndimage as nd

import os
import shutil
from time import perf_counter
from datetime import datetime


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

        save_img(img, path.replace('original', 'modified'))

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


def save_img(img, path):
    """Function to save img in delivered path

            img - image obj to save
            path - path where to save image
            """

    pil_img = Image.fromarray(img)
    pil_img.save(path)


# Function to measure time
def performance():
    """Function to measure time
    Function is using yield, so to use it there is need to use next.
    First yield have messaged 'Counting started'
    second one return time needed to perform action """

    while 1:
        start = perf_counter()
        yield 'Counting started'

        stop = perf_counter()
        yield f'The script needed 10 {stop - start:.2f} seconds to perform this action'


# Class to user of program
class user_class:
    def __init__(self, nick, password):
        """init of user_class takes nick and password to create instance of class.
        Other parameters will be updated in other function.

        nick - identification od user
        password - key that allows to verify user
        email - Contact email to user
        isPremium - True/False user have account with height priority
        isAdmin - True/False user have account with higher authority
        """
        self.nick = nick
        self.password = password
        self.email = ''
        self.isPremium = ''
        self.isAdmin = ''

    def verify_user(self, User):
        """Function that verifies if user with certain combination of password and login exists
        User - table in database

        Function return info about process"""

        user_login = User.query.filter(User.nick == self.nick).first()
        if user_login:
            if self.password == user_login.password:
                message = 'Login process is successful'
                session['user'] = user_login.nick
            else:
                message = 'Invalid password'
        else:
            message = 'There is no user with that login'

        # Passing message about status of login
        flash(message)
        return message

    def verify_register(self, User, repeat_password, email):
        """ Function that verifies if data given in registry is correct
        User - table in database
        repeat_password - second field with password in registry form
        email - email given in registry form

        Function returns 1 if verification was successful and none if not"""
        # Checking if nick is unique
        nick_exist = User.query.filter(User.nick == self.nick).first()
        if nick_exist:
            flash('There is user with that nick registered already!')
            return

        # Checking if email is unique
        email_exist = User.query.filter(User.email == email).first()
        if email_exist:
            flash('There is user with that email registered already!')
            return

        # Checking passwords are the same
        if repeat_password != self.password:
            flash('Both passwords should be the same!')
            return

        flash('You have been registered successfully!')
        self.email = email
        return 1

    def creating_user(self, db, User):
        """Function that creates user in database
        db - database
        User - Table in database"""

        # Assigning data for new account
        newUser = User(
            nick=self.nick,
            password=self.password,
            email=self.email,
            premium=False,
            admin=False
        )

        # Creating new user
        db.session.add(newUser)
        db.session.commit()


# Class for images on server
class image_class:
    def __init__(self, file_name, user):
        """Init function of image_class takes file_name and nick of user that wants to save file

        Attributes of instance:
        path_temp - path to image that is currently used as display image
        file_name - name of file
        size - size of image in path temp (size is in MB)
        category - category of image, currently undefined
        Later there will be auto-categorization of image based on what is on image
        created_date - date of creating instance in format default format of datetime.now()
        user - nick of user that wants to save image

        After creating attributes function create_dir() will be called
        """
        self.path_temp = os.path.join('static', 'download', 'modified', file_name)

        self.file_name = file_name
        self.size = self.get_size_dir()
        self.category = 'undefined'
        self.created_date = datetime.now()
        self.user = user

        # Calling function to create dir user doesn't have one
        self.create_dir()

    # Function to create dir for user if he doesn't have one
    def create_dir(self):
        """Class function that creates dir if user in instance doesn't have any directory.
        Function gives communicates to the flash if there was need of creating new dir"""

        # Creating path to user dir
        path_to_dir = os.path.join(f'static/db/{self.user}')

        # Checking if path exists, if not creating dir
        if not os.path.exists(path_to_dir):
            try:
                # Creating dir for user
                os.mkdir(path_to_dir)
                flash(f"Created dir for user {self.user}.")

            except Exception as e:
                flash(f"Error while creating dir for user: {e}")

    # Function to check size of image that will be saved on server
    def get_size_dir(self):
        """"Class function that returns size of image in mb"""

        # Checking size of file and converting it to mb
        file_size_bytes = os.path.getsize(self.path_temp)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Returning size of img in MB and with 2 numbers after coma
        return f'{file_size_mb:.2f}'

    # Function to save image on server
    def saving_image_server(self, db, Images, User):
        """ Function that send record about saved image in Images table on server
        db - database
        Images - Table for Images
        User - Table with user (for checking what id have user)

        Function gives flash message about status of creating images and creating record
        """

        try:
            # Creating path to save
            save_path = os.path.join(f'static/db/{self.user}/{self.file_name}')

            # Copying image that is displayed to user dir on server
            shutil.copy(self.path_temp, save_path)

            newImage = Images(
                file_name=self.file_name,
                size=self.size,
                category=self.category,
                created_date=self.created_date,
                user_id=get_nick_id(self.user, User)
            )

            db.session.add(newImage)
            db.session.commit()

            flash('File was saved on server!')

        except Exception as e:
            flash(f'Error: {e}')

    def __repr__(self):
        """Returning info about instance"""
        return f'[Owner: {self.user}]\n' \
               f'Img: {self.file_name}\n' \
               f'Size: {self.size}MB\n' \
               f'Created: {self.created_date}\n' \
               f'Category: {self.category}'


# Function to give id of nick
def get_nick_id(nick, User):
    # getting id of user
    user = User.query.filter(User.nick == nick).first()
    return user.id
