from datetime import datetime
import os
import shutil

from flask import flash

from projekt.python.img_funct import get_nick_id


# Class for images on server
class ImageClass:
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

            except Exception as error:
                flash(f"Error while creating dir for user: {error}")

    # Function to check size of image that will be saved on server
    def get_size_dir(self):
        """"Class function that returns size of image in mb"""

        # Checking size of file and converting it to mb
        file_size_bytes = os.path.getsize(self.path_temp)
        file_size_mb = file_size_bytes / (1024 * 1024)

        # Returning size of img in MB and with 2 numbers after coma
        return f'{file_size_mb:.2f}'

    # Function to save image on server
    def saving_image_server(self, db, table_img, table_user):
        """ Function that send record about saved image in Images table on server
        db - database
        table_img - Table with images
        table_user - Table with user (for checking what id have user)

        Function gives flash message about status of creating images and creating record
        """

        try:
            # Creating path to save
            save_path = os.path.join(f'static/db/{self.user}/{self.file_name}')

            # Copying image that is displayed to user dir on server
            shutil.copy(self.path_temp, save_path)

            # Getting user id
            user_id = get_nick_id(self.user, table_user)

            # Checking if user don't have filed with the same name saved on dir
            if not self.check_unique_file_name(user_id, table_img):
                new_image = table_img(
                    file_name=self.file_name,
                    size=self.size,
                    category=self.category,
                    created_date=self.created_date,
                    user_id= user_id
                )

                db.session.add(new_image)
                db.session.commit()

                flash('File was saved on server!')
            else:
                flash('You cant have two files with same name, change file name!')

        except Exception as error:
            flash(f'Error: {error}')

    # Function to check if user have filed with same name
    def check_unique_file_name(self, user_id, table_img):
        """ Function that checks if file can be saved on server
        function checks if user don't have already file saved with that name

        if user don't have none will be returned
        if he has record will be returned"""
        
        # Getting first record with same file name and same user id
        duplicate_file_name = table_img.query.filter(table_img.file_name == self.file_name and table_img.user_id == user_id).first()

        return duplicate_file_name

    # Function to change file name
    def change_file_name(self, new_file_name):
        """ Function that change file name (not in user dir).
        Function use os.rename to change name for file in original and download

        new_file_name - new name of file
        """

        # Creating paths
        old_file_path = os.path.join(r'static', 'download', 'original', self.file_name)
        new_file_path = os.path.join(r'static', 'download', 'original', new_file_name)

        # Renaming file saved in user dir
        os.rename(old_file_path, new_file_path)

        # Copying image that is displayed to user dir on server
        os.rename(old_file_path.replace('original', 'modified'), new_file_path.replace('original', 'modified'))

    def __repr__(self):
        """Returning info about instance"""
        return f'[Owner: {self.user}]\n' \
               f'Img: {self.file_name}\n' \
               f'Size: {self.size}MB\n' \
               f'Created: {self.created_date}\n' \
               f'Category: {self.category}'
