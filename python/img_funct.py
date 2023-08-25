# Modul needed to accurate measuring time
from time import perf_counter

import os
from flask import session

# Modul needed to convert array into img
from PIL import Image


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


# Function to give id of nick
def get_nick_id(nick, table):
    """Function to get user id of nick in given table
    Function returns id of nick in table"""

    user = table.query.filter(table.nick == nick).first()
    return user.id


# Function to delete image form db
def deleting_image(file_name, user_table, image_table, db):
    # Getting username from session
    user_nick = session.get('user')

    # Deleting saved image
    path = os.path.join(r'static\db', user_nick, file_name)
    os.remove(path)

    # Getting id
    user_id = get_nick_id(user_nick, user_table)

    # Deleting record from table
    image_to_delete = image_table.query.filter_by(file_name=file_name, user_id=user_id).first()
    db.session.delete(image_to_delete)
    db.session.commit()
