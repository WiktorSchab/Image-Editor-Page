from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename

import os
import shutil

import numpy as np
from PIL import Image, ImageFilter

import cv2

from io import BytesIO
import base64

from img_funct import img_class

app = Flask(__name__)
app.config['SECRET_KEY'] = 'P@$$w0rda'


# Form to send image
class FileForm(FlaskForm):
    cover = FileField("Send me a pic (only jpg, png need to show off validation skills)",
                      validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Sorry, only png and jpg")])


# color ranges
color_floor_top = ([150, 100, 100, 174, 255, 255], [130, 100, 100, 150, 255, 255], [119, 100, 100, 129, 255, 255],
                   [100, 50, 50, 118, 255, 255], [91, 50, 50, 99, 255, 255], [40, 50, 50, 90, 255, 255],
                   [0, 50, 50, 38, 255, 255], [0, 0, 0, 180, 25, 230])

# class instance (app, access, file_name)
img_instance = img_class(app, 0, 0)


# starting page
@app.route('/', methods=['POST', 'GET'])
def index():
    form = FileForm()

    # checking if user have access (bypass validation earlier with same file) or bypass the validation
    if img_instance.access == 1 or form.validate_on_submit():
        img_instance.access = 1  # access to edit

        # checking if there is no filename or given filename is not the same as saved one
        if not img_instance.file_name or (form.cover.data and form.cover.data.filename != img_instance.file_name):
            # saving file from form
            f = form.cover.data
            filename = secure_filename(f.filename)

            path = os.path.join(app.root_path, 'static', 'download', 'modified', filename)
            f.save(path)

            # opening file as array and saving file
            img = np.array(Image.open(path))
            img_class.save_img(img, path)

            # making copy of img
            shutil.copyfile(path, path.replace('modified', 'original'))

            # saving values to class to have access to it later
            img_instance.file_name = filename
        filename = img_instance.file_name

        # Giving access to page
        return render_template('work_page.html', file_name=filename,
                               url_download=url_for('download', file_name=filename))

    # Giving form to send img again
    return render_template('index.html', form=form)


# Confirmation of image change
@app.route('/reset_change_confirm/<file_name>')
def img_change_confirm(file_name):
    return render_template('confirm_window.html', file_name=file_name)


# Changing image
@app.route('/deleting_image')
def img_change():
    # Rendering form and changing access to 0, user will need to send image again
    form = FileForm()
    img_instance.access = 0
    return render_template('index.html', form=form)


# Reset img
@app.route('/reset_image/<file_name>')
def img_reset(file_name):
    # Replacing image in modified to image original.
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)
    shutil.copyfile(path, path.replace('original', 'modified'))
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


# Color filter
@app.route('/color/<file_name>')
def only_color(file_name):
    # Getting cookie with Color_buttons name
    cookie = request.cookies.get('Color_buttons')

    # Checking if cookie exist
    if cookie is not None:
        # Deleting useless syntax's from cookie value
        cookie = cookie[3:]
        cookie = cookie.strip()

        # Making list from id numbers from cookie file
        color = [color_floor_top[i] for i in range(0, len(color_floor_top)) if str(i) in cookie]

        path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

        # Declaring image
        img = None

        # Iteration by every chosen color by user
        for i in color:
            lower = (int(i[0]), int(i[1]), int(i[2]))
            upper = (int(i[3]), int(i[4]), int(i[5]))

            result = img_class.display_color(path, lower, upper)

            # It goes to if it is for only start iteration
            if img is None:
                img = result
            # It goes to else every time except first time
            else:
                img = cv2.add(img, result)

        # checking if img is not none (img will none if there will be 0 colors chosen)
        if img is not None:
            path = path.replace('original', 'modified')
            img_class.save_img(img, path.replace('original', 'modified'))

    return redirect(url_for('index'))


# Page with download window
@app.route('/download/<file_name>', methods=['POST', 'GET'])
def download(file_name):
    # Showing form with extension to choose
    if request.method == 'GET':
        # Checking with function in img_class size of file with certain extension, by creating file in temp.
        jpg = img_instance.get_image_size(file_name, 'jpg')
        png = img_instance.get_image_size(file_name, 'png')
        tiff = img_instance.get_image_size(file_name, 'tiff')
        gif = img_instance.get_image_size(file_name, 'gif')

        file_sizes = [jpg, png, tiff, gif]

        return render_template('download_window.html', file_name=file_name, url_download='#', file_sizes=file_sizes)
    else:
        # Getting chosen extension from format
        format_file = request.form['format']

        # Creating path to created file in temp with that extension
        path = os.path.join(app.root_path, 'static', 'download', 'temp', file_name.split('.')[0] + '.' + format_file)

        return send_file(path, as_attachment=True)


# draw mode
@app.route('/draw_mode/<file_name>')
def draw_mode(file_name):
    return render_template('draw.html', file_name=file_name)


# temp page to save canvas as file in modified
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


if __name__ == '__main__':
    app.run(debug=True)
