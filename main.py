import random
import string
import os
import shutil
from io import BytesIO
import base64

from flask import Flask, render_template, url_for, request, redirect, send_file, session, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

from wtforms.validators import InputRequired, Email
from wtforms import StringField, PasswordField

from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename

import numpy as np
from PIL import Image

import cv2

from python.img_funct import save_img, performance, get_nick_id, deleting_image

from python.session_image_class import SessionImageClass
from python.image_class import ImageClass
from python.user_class import UserClass
from colorize.colorize_filter import colorize

app = Flask(__name__)
app.config.from_pyfile('db/config.py')
db = SQLAlchemy(app)

print('-',os.environ.get('SECRET_KEY'))
# Form to send image
class FileForm(FlaskForm):
    cover = FileField("Send me a pic (only jpg, png need to show off validation skills)",
                      validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Sorry, only png and jpg")])


# Form to log in
class LoginForm(FlaskForm):
    name = StringField('Enter login', validators=[InputRequired()])
    password = PasswordField('Enter password', validators=[InputRequired()])


# Form to register
class RegisterForm(FlaskForm):
    name = StringField('Enter login', validators=[InputRequired()])
    password = PasswordField('Enter password', validators=[InputRequired()])
    repeat_password = PasswordField('Enter password again', validators=[InputRequired()])
    email = StringField('Enter email', validators=[InputRequired(), Email('Invalid email')])


# Table for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(20))
    password = db.Column(db.String)
    email = db.Column(db.String)

    premium = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)

    def __repr__(self):
        return f'User data: [{self.id}]: {self.nick} - {self.admin}'


# Table for images
class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(200))
    size = db.Column(db.Integer)
    category = db.Column(db.String(20))
    created_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Creating relations
    user = db.relationship('User', backref=db.backref('images', lazy=True))

    def __repr__(self):
        return f'Image data: [{self.id}] - {self.file_name} - {self.size} - {self.category}\n' \
               f'User ID: {self.user_id}'


# color ranges
color_floor_top = ([150, 100, 100, 174, 255, 255], [130, 100, 100, 150, 255, 255],
                   [119, 100, 100, 129, 255, 255], [100, 50, 50, 118, 255, 255],
                   [91, 50, 50, 99, 255, 255], [40, 50, 50, 90, 255, 255],
                   [0, 50, 50, 38, 255, 255], [0, 0, 0, 180, 25, 230])

# class instance (app, access, file_name)
img_instance = SessionImageClass(app, 0, 0)

# Page to create tables and admin on first run
@app.route('/init')
def init():
    # Creating tables
    db.create_all()

    if not User.query.filter(User.admin == True).count():
        # Generating password for admin
        password_admin = ''.join(random.choice(string.ascii_lowercase) for i in range(3))

        # Data for first Admin
        admin = User(
            nick=''.join(random.choice(string.ascii_lowercase) for i in range(3)),
            password=password_admin,
            email="",
            premium=True,
            admin=True
        )

        print('Admin was created add email to admin account')
        # Displaying password if admin is generated because in db there is hashed password
        print(password_admin)

        # Creating admin
        db.session.add(admin)
        db.session.commit()

    print('App is configured!')
    return redirect(url_for('index'))


# Starting page
@app.route('/', methods=['POST', 'GET'])
def index():
    # Checking if user is logged if not redirecting him to login
    if not session.get('user'): return redirect(url_for('login'))

    # Checking if there is temporary file, if there is function to delete files will be called
    if len(img_instance.temp_file) > 0:
        img_instance.delete_temp()

    # Generating form
    form = FileForm()

    # Checking if user have access (bypass validation earlier with same file) or bypass the validation
    if img_instance.access == 1 or form.validate_on_submit():
        img_instance.access = 1  # access to edit

        # Checking if there is no filename or given filename is not the same as saved one
        if not img_instance.file_name or (form.cover.data and form.cover.data.filename != img_instance.file_name):
            # Saving file from form
            f = form.cover.data
            filename = secure_filename(f.filename)

            # Checking if name is not default.png
            if filename == 'default.png':
                flash('You can use file with default.png name change it and try again!')
                img_instance.access = 0
                return redirect(url_for('index'))

            path = os.path.join(app.root_path, 'static', 'download', 'modified', filename)
            f.save(path)

            # Opening file as array and saving file
            img = np.array(Image.open(path))
            save_img(img, path)

            # Making copy of img
            shutil.copyfile(path, path.replace('modified', 'original'))

            # Saving values to class to have access to it later
            img_instance.file_name = filename
        filename = img_instance.file_name

        # Getting user nick and then id of user
        user_nick = session.get('user')
        id = get_nick_id(user_nick, User)

        # Getting 5 newest created images by user
        latest_images = Images.query.filter_by(user_id=id).order_by(Images.created_date.desc())
        latest_images = latest_images.limit(5).all()

        path_to_dir = 'db' + '/' + user_nick
        context = {
            'file_name': filename,
            'url_download': url_for('download', file_name=filename),
            'latest_images': latest_images,
            'path_to_dir': path_to_dir
        }

        # Giving access to page
        return render_template('Main_page/work_page.html', **context)

    # Giving form to send img again
    return render_template('Main_page/index.html', form=form)


# Changing name of the file
@app.route('/change_file_name',methods=['POST'])
def change_file_name():
    # New name of file
    new_name = request.form.get('name_file')

    # Checking if new name isn't default (if file is png)
    if new_name == 'default.png':
        flash('You cant set default as name of png file. Please choose different name.')
        return redirect(url_for('index'))

    # Creating instance of file
    image_change_name = ImageClass(img_instance.file_name, session.get('user'))

    # Calling function to change name of file
    image_change_name.change_file_name(new_name)

    # Changing value of instance that contains file_name
    img_instance.file_name = new_name

    return redirect(url_for('index'))


# Confirmation of image change
@app.route('/reset_change_confirm/<file_name>')
def img_change_confirm(file_name):
    # Passing arguments needed to generate confirm_window
    context = {
        'file_name_arg': file_name,
        'file_name': file_name,
        'title': 'Confirm',
        'text': 'Are you sure you want to change image? It will be lost.',
        'positive_answer': {'text': 'Confirm', 'link': 'img_change'},
        'negative_answer': {'text': 'Close'}
    }
    return render_template('Main_page/confirm_window.html', **context)


# Changing image
@app.route('/deleting_image/<file_name>')
def img_change(file_name):
    path = os.path.join(app.root_path, 'static', 'download', 'modified', file_name)

    # Deleting old images
    os.remove(path)
    os.remove(path.replace('modified', 'original'))
    img_instance.file_name = 0

    # Rendering form and changing access to 0, user will need to send image again
    form = FileForm()
    img_instance.access = 0
    return render_template('Main_page/index.html', form=form)


# Reset img
@app.route('/reset_image/<file_name>')
def img_reset(file_name):
    # Replacing image in modified to image original.
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)
    shutil.copyfile(path, path.replace('original', 'modified'))
    return redirect(url_for('index'))


# Generating confirm window if user wants to change displaying image
@app.route('/history_restore_confirm/<file_name>')
def history_restore_confirm(file_name):

    # Setting file_name in instance as default.png if user didn't give any file
    if img_instance.file_name == 0:
        img_instance.file_name = 'default.png'

    # Passing arguments needed to generate confirm_window
    context = {
        'file_name_arg': file_name,
        'file_name': img_instance.file_name,
        'title': 'Confirm',
        'text': 'Are you sure you want to change image? It will be lost.',
        'positive_answer': {'text': 'Confirm', 'link': 'history_restore'},
        'negative_answer': {'text': 'Close'}
    }
    return render_template('Main_page/confirm_window.html', **context)


# Setting image from history as active one
@app.route('/history_restore/<file_name>')
def history_restore(file_name):
    # Getting username from session
    user_nick = session.get('user')

    # Creating input and output path
    input_path = os.path.join(r'static\db', user_nick, file_name)
    output_path = input_path.replace(fr'db\{user_nick}', r'download\original')

    # Copying file from input path to static/download/original/
    shutil.copyfile(input_path, output_path)

    # Copying static/download/original/ from input path to static/download/modified/
    shutil.copyfile(output_path, output_path.replace('original', 'modified'))

    # Changing image name saved in img_instance
    img_instance.file_name = file_name

    # Changing access to 1 (if user didn't give any file it will be necessary to work)
    img_instance.access = 1
    return redirect(url_for('index'))


# Generating confirm window if user wants to delete image from server
@app.route('/history_delete_confirm/<file_name>')
def history_delete_confirm(file_name):
    
    # Setting file_name in instance as default.png if user didn't give any file
    if img_instance.file_name == 0:
        img_instance.file_name = 'default.png'

    # Passing arguments needed to generate confirm_window
    print(img_instance.file_name)
    context = {
        'file_name_arg': file_name,
        'file_name': img_instance.file_name,
        'title': 'Confirm',
        'text': 'Are you sure you want to delete image? It will be lost.',
        'positive_answer': {'text': 'Confirm', 'link': 'history_delete'},
        'negative_answer': {'text': 'Close'},
    }
    return render_template('Main_page/confirm_window.html', **context)


# Using image from history as the one that is displaying for user
@app.route('/history_delete/<file_name>')
def history_delete(file_name):
    # Calling function to delete certain image from Images table in db
    deleting_image(file_name, User, Images, db)

    return redirect(url_for('index'))


# Black & white filter
@app.route('/bw_filter/<file_name>')
def bw_filter(file_name):
    img_instance.filter_funct("convert('L')", file_name)
    return redirect(url_for('index'))


# Real black & white filter
@app.route('/rbw_filter/<file_name>')
def rbw_filter(file_name):
    img_instance.filter_funct("convert('1')", file_name)
    return redirect(url_for('index'))


# Contur filter
@app.route('/con_filter/<file_name>')
def con_filter(file_name):
    img_instance.filter_funct("filter(ImageFilter.CONTOUR)", file_name)
    return redirect(url_for('index'))


# Blur filter
@app.route('/blur_filter/<file_name>')
def blur_filter(file_name):
    img_instance.filter_funct("filter(ImageFilter.GaussianBlur(radius=4))", file_name)
    return redirect(url_for('index'))


# Emboss filter
@app.route('/emb_filter/<file_name>')
def emb_filter(file_name):
    img_instance.filter_funct("filter(ImageFilter.EMBOSS)", file_name)
    return redirect(url_for('index'))


@app.route('/colorize_filter/confirm/<file_name>')
def colorize_filter_confirm(file_name):
    # Passing arguments needed to generate confirm_window
    context = {
        'file_name': file_name,
        'file_name_arg': file_name,
        'title': 'Confirm',
        'text': 'Are you sure you want to use that filter? Original image will be lost.',
        'positive_answer': {'text': 'Confirm', 'link': 'colorize_filter'},
        'negative_answer': {'text': 'Close'}
    }

    return render_template('Main_page/confirm_window.html', **context)


# Colorize image filter
@app.route('/colorize_filter/<file_name>')
def colorize_filter(file_name):
    # Using generator to measurer time
    perf_gen = performance()

    # Starting counting time
    print(next(perf_gen))

    # Calling function to colorize image
    colorize(file_name, app)

    # Printing time
    print(next(perf_gen))
    return redirect(url_for('index'))


# Color filter
@app.route('/color/<file_name>')
def only_color(file_name):
    # Getting cookie with colorButtons name
    cookie = request.cookies.get('colorButtons')

    input_path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)
    output_path = input_path.replace('original', 'modified')

    # Checking if cookie exist
    if cookie is not None and len(cookie) > 3:
        # Deleting useless syntax's from cookie value
        cookie = cookie[3:]
        cookie = cookie.strip()

        # Making list from id numbers from cookie file
        color = [color_floor_top[i] for i in range(0, len(color_floor_top)) if str(i) in cookie]

        # Declaring image
        img = None

        # Iteration by every chosen color by user
        for i in color:
            lower = (int(i[0]), int(i[1]), int(i[2]))
            upper = (int(i[3]), int(i[4]), int(i[5]))

            result = SessionImageClass.display_color(input_path, lower, upper)

            # It goes to if it is for only start iteration
            if img is None:
                img = result
            # It goes to else every time except first time
            else:
                img = cv2.add(img, result)

        # checking if img is not none (img will none if there will be 0 colors chosen)
        if img is not None:
            save_img(img, output_path)
    else:
        # taking original image and putting it in displaying place
        print('a')
        shutil.copyfile(input_path, output_path)

    return redirect(url_for('index'))


# Page with download window
@app.route('/download/<file_name>', methods=['POST', 'GET'])
def download(file_name):
    # Checking if user is logged if not redirecting him to login
    if not session.get('user'): return redirect(url_for('login'))

    # Showing form with extension to choose
    if request.method == 'GET':
        # Checking with function in img_class size of file with certain extension
        # Function creates files in download/temp that will be later deleted
        jpg = img_instance.get_image_size(file_name, 'jpg')
        png = img_instance.get_image_size(file_name, 'png')
        tiff = img_instance.get_image_size(file_name, 'tiff')
        gif = img_instance.get_image_size(file_name, 'gif')

        file_sizes = [jpg, png, tiff, gif]

        return render_template('Main_page/download_window.html', file_name=file_name, url_download='#',
                               file_sizes=file_sizes)
    else:
        # Getting chosen extension from format
        format_file = request.form['format']

        # Creating path to created file in temp with that extension
        path = os.path.join(app.root_path, 'static/download/temp', file_name.split('.')[0] + '.' + format_file)

        return send_file(path, as_attachment=True)


@app.route('/save_on_server/<file_name>')
def save_on_server(file_name):
    # Checking if user is logged if not redirecting him to login
    if not session.get('user'): return redirect(url_for('login'))

    image_to_server = ImageClass(file_name, session.get('user'))

    # Creating image on user dir in server by using info in instance
    image_to_server.saving_image_server(db, Images, User)

    # Redirecting to index after saving it
    return redirect(url_for('index'))


# Draw mode
@app.route('/draw_mode/<file_name>')
def draw_mode(file_name):
    # Checking if user is logged if not redirecting him to login
    if not session.get('user'): return redirect(url_for('login'))

    return render_template('Draw_page/draw.html', file_name=file_name)


# Receiving canvas from ajax and saving it as png
@app.route('/draw_mode/saving', methods=['GET', 'POST'])
def draw_mode_saving():
    try:
        # Getting data uri data from request
        image_data_uri = request.form['image_data_uri']
        path = os.path.join(app.root_path, 'static', 'download', 'modified', img_instance.file_name)

        # Clearing data and decoding it
        image_data = image_data_uri.replace('data:image/png;base64,', '')
        image_bytes = base64.b64decode(image_data)

        # Opening image that is in byes
        image = Image.open(BytesIO(image_bytes))

        # Saving image in PNG
        image.save(path, format='PNG')

    except Exception as e:
        print(f'Error occurred {e}.')
    return redirect(url_for('index'))


# Profile page
@app.route('/profile/<user_nick>')
def profile(user_nick):
    # Checking if user is logged if not redirecting him to login
    if not session.get('user'): return redirect(url_for('login'))

    id = get_nick_id(user_nick, User)

    if session.get('user') == user_nick:
        data_img = Images.query.filter_by(user_id=id).order_by(Images.created_date.desc()).all()
        print(data_img)
    else:
        print('tu')
        data_img = None

    path_to_dir = 'db' + '/' + user_nick

    path_to_profile = os.path.join(app.root_path, 'static', 'download', 'profile', user_nick)

    if os.path.exists(path_to_profile):
        prof_name = os.listdir(path_to_profile)[0]
        profile_pic = f'download/profile/{user_nick}/{prof_name}'
    else:
        profile_pic = 'download/profile/default_profile_icon.png'

    # Data to send to html
    context = {
        'user_nick': user_nick,
        'data_img': data_img,
        'path_to_dir': path_to_dir,
        'profile_pic': profile_pic
    }

    return render_template('Profile_page/profile_user.html', **context)


@app.route('/change_profile/<user_nick>', methods=['GET', 'POST'])
def change_profile(user_nick):
    form = FileForm()

    if form.validate_on_submit():
        f = form.cover.data

        # Splitting file name
        filename = secure_filename(f.filename).split('.')

        # Changing name of file while saving extension
        new_file_name = 'profile.' + filename[1]

        path_to_dir = os.path.join(app.root_path, 'static', 'download', 'profile', user_nick)
        # Creating user dir in profile if he doesn't have one
        try:
            # Removing old profile picture
            old_profile = os.listdir(path_to_dir)[0]

            os.remove(os.path.join(path_to_dir, old_profile))

            # Saving new profile picture
            f.save(os.path.join(path_to_dir, new_file_name))

        except FileNotFoundError:
            # Creating dir
            os.mkdir(path_to_dir)

            # Saving new profile picture
            f.save(os.path.join(path_to_dir, new_file_name))

        return redirect(url_for('profile', user_nick=user_nick))

    return render_template('Profile_page/change_profile.html', form=form, user_nick=user_nick)


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Getting session value of user (session var user exists if user is logged)
    isLoged = session.get('user')

    # Checking if user is already logged
    if not isLoged:
        # Generating form
        form = LoginForm()

        if request.method == 'GET':
            # Rendering forms to login
            return render_template('login.html', form=form)
        else:
            # Assigning data from user to variables
            name = form.name.data
            password = form.password.data

            # Creating instance of user_class and verifying login and password
            user_login = UserClass(name, password)
            user_login.verify_user(User)

            # Returning user again to login (if its successful he will be redirected to index)
            return redirect(url_for('login'))

    # Redirecting user to index if login was successful, or he is already logged
    return redirect(url_for('index'))


# Logout page
@app.route('/logout')
def logout():
    # Clearing session that contains username
    session.pop('user', None)
    flash('You have been logged out')

    # Clearing data in instance
    img_instance.file_name = 0
    img_instance.access = 0
    return redirect(url_for('login'))


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Getting session value of user (session var user exists if user is logged)
    isLoged = session.get('user')

    # Checking if user is logged
    if not isLoged:
        # Generating form
        form = RegisterForm()
        if request.method == 'GET':
            # Rendering forms to register
            return render_template('register.html', form=form)
        else:
            # if Email is valid and other fields are filled
            if form.validate_on_submit():

                # Assigning data from user to variables
                name = form.name.data
                password = form.password.data
                repeat_password = form.repeat_password.data
                email = form.email.data

                # Creating instance of class
                user_registry = UserClass(name, password)

                # Verifying registry data
                if user_registry.verify_register(User, repeat_password, email):
                    # Creating user in db
                    user_registry.creating_user(db, User)

                    # Redirecting to login page
                    return redirect(url_for('login'))

            # If verification of data is unsuccessful, form will be showed again
            return render_template('register.html', form=form)

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
