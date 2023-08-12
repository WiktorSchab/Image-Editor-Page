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


class FileForm(FlaskForm):
    cover = FileField("Send me a pic (only jpg, png need to show off validation skills)", validators=[FileRequired(),
                                                                                                      FileAllowed(
                                                                                                          ['jpg',
                                                                                                           'png'],
                                                                                                          "Sorry, only png and jpg")])


color_floor_top = ([150, 100, 100, 174, 255, 255], [130, 100, 100, 150, 255, 255], [119, 100, 100, 129, 255, 255],
                   [100, 50, 50, 118, 255, 255], [91, 50, 50, 99, 255, 255], [40, 50, 50, 90, 255, 255],
                   [0, 50, 50, 38, 255, 255], [0, 0, 0, 180, 25, 230])


img_instance = img_class(app,0,0)

# starting page
@app.route('/', methods=['POST', 'GET'])
def index():
    form = FileForm()

    if img_instance.access == 1 or form.validate_on_submit():
        img_instance.access = 1  # access to edit

        if not img_instance.file_name or (form.cover.data and form.cover.data.filename != img_instance.file_name):
            # saving file from form
            f = form.cover.data
            filename = secure_filename(f.filename)

            path = os.path.join(app.root_path, 'static', 'download', 'modified', filename)
            f.save(path)

            # resizing file for one format of display and fast operating on file
            img = np.array(Image.open(path))
            img_class.save_img(img, path)

            # making copy of img
            shutil.copyfile(path, path.replace('modified', 'original'))

            # saving values to dict, so they won't be refreshed
            img_instance.file_name = filename

        filename = img_instance.file_name
        return render_template('work_page.html', file_name=filename,
                               url_download=url_for('download', file_name=filename))
    return render_template('index.html', form=form)


# Changing image
@app.route('/reset_change_confirm/<file_name>')
def img_change_confirm(file_name):
    return render_template('confirm_window.html',file_name=file_name)

@app.route('/deleting_image')
def img_change():
    form = FileForm()
    img_instance.access = 0
    return render_template('index.html', form=form)


# Reset img
@app.route('/reset_image/<file_name>')
def img_reset(file_name):
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)
    shutil.copyfile(path, path.replace('original', 'modified'))
    return redirect(url_for('index'))

# Black & white filter
@app.route('/bw_filter/<file_name>')
def bw_filter(file_name):
    img_instance.filter_funct("convert('L')",file_name)
    return redirect(url_for('index'))


# Real black & white filter
@app.route('/rbw_filter/<file_name>')
def rbw_filter(file_name):
    img_instance.filter_funct("convert('1')",file_name)
    return redirect(url_for('index'))


# Contur filter
@app.route('/con_filter/<file_name>')
def con_filter(file_name):
    img_instance.filter_funct("filter(ImageFilter.CONTOUR)",file_name)
    return redirect(url_for('index'))


# Blur filter
@app.route('/blur_filter/<file_name>')
def blur_filter(file_name):
    img_instance.filter_funct("filter(ImageFilter.GaussianBlur(radius=4))",file_name)
    return redirect(url_for('index'))


# Emboss filter
@app.route('/emb_filter/<file_name>')
def emb_filter(file_name):
    img_instance.filter_funct("filter(ImageFilter.EMBOSS)",file_name)
    return redirect(url_for('index'))


# color filter
@app.route('/color/<file_name>')
def only_color(file_name):
    cookie = request.cookies.get('Color_buttons')
    if cookie is not None:
        cookie = cookie[3:]
        cookie = cookie.strip()  # making list from id numers from cookie file

        color = [color_floor_top[i] for i in range(0, len(color_floor_top)) if str(i) in cookie]

        path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

        img = None
        for i in color:
            lower = (int(i[0]), int(i[1]), int(i[2]))
            upper = (int(i[3]), int(i[4]), int(i[5]))

            result = img_class.display_color(path, lower, upper)
            if img is None:
                img = result
            else:
                img = cv2.add(img, result)

        if img is not None:
            path = path.replace('original', 'modified')
            img_class.save_img(img, path.replace('original', 'modified'))

    return redirect(url_for('index'))


# Page with download window
@app.route('/download/<file_name>', methods=['POST', 'GET'])
def download(file_name):
    if request.method == 'GET':
        path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)
        print(path)
        # Checking with function in img_class size of file with certain extension, by creating file in temp.
        jpg = img_instance.get_image_size(file_name, 'jpg')
        png = img_instance.get_image_size(file_name, 'png')
        tiff = img_instance.get_image_size(file_name, 'tiff')
        gif = img_instance.get_image_size(file_name, 'gif')

        file_sizes = [jpg, png, tiff, gif]

        return render_template('download_window.html', file_name=file_name, url_download='#', file_sizes=file_sizes)
    else:
        format = request.form['format']

        path = os.path.join(app.root_path, 'static', 'download', 'temp', file_name.split('.')[0] + '.' + format)

        return send_file(path, as_attachment=True)



#draw mode
@app.route('/draw_mode/<file_name>')
def draw_mode(file_name):
    return render_template('draw.html', file_name=file_name)


#temp page to save canvas as file in modified
@app.route('/draw_mode/saving',methods=['GET','POST'])
def draw_mode_saving():
    try:
        image_data_uri = request.form['image_data_uri']
        path = os.path.join(app.root_path, 'static', 'download', 'modified', img_instance.file_name)

        image_data = image_data_uri.replace("data:image/png;base64,", "")
        image_bytes = base64.b64decode(image_data)

        image = Image.open(BytesIO(image_bytes))
        image.save(path, format="PNG")
    except:
        pass


    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
