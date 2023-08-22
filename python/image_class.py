from flask import flash

from datetime import datetime
import os
import shutil

from projekt.python.img_funct import get_nick_id


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
