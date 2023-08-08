from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename

import os
import shutil

import numpy as np
from PIL import Image, ImageFilter

import cv2

from img_funct import img_class

app = Flask(__name__)
app.config['SECRET_KEY'] = 'P@$$w0rda'


class FileForm(FlaskForm):
    cover = FileField("Send me a pic (only jpg, png need to show off validation skills)", validators=[FileRequired(),
                                                                                                      FileAllowed(
                                                                                                          ['jpg',
                                                                                                           'png'],
                                                                                                          "Sorry, only png and jpg")])

color_floor_top = ([150,100,100, 174,255,255],[130,100,100, 150,255,255],[119,100,100, 129,255,255],
                [100,50,50, 118,255,255], [91,50,50, 99,255,255],[40,50,50, 90,255,255],
                [0,50,50, 38,255,255], [0,0,0, 180,25,230])




# starting page
@app.route('/', methods=['POST', 'GET'])
def index(d={'access': 0, 'filename': None}):
    form = FileForm()
    if d['access'] == 1 or form.validate_on_submit():
        d['access'] = 1  # access to edit

        if not d['filename'] or (form.cover.data and form.cover.data.filename != d['filename']):
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
            d['filename'] = filename
        filename = d['filename']
        return render_template('work_page.html', file_name=filename, url_download = url_for('download',file_name=filename))
    return render_template('index.html', form=form)


# Changing image
@app.route('/deleting_image')
def img_change():
    form = FileForm()
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
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

    img = np.array(Image.open(path).convert('L'))

    img_class.save_img(img, path.replace('original', 'modified'))
    return redirect(url_for('index'))


# Real black & white filter
@app.route('/rbw_filter/<file_name>')
def rbw_filter(file_name):
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

    img = np.array(Image.open(path).convert('1'))
    img_class.save_img(img, path.replace('original', 'modified'))
    return redirect(url_for('index'))


# Contur filter
@app.route('/con_filter/<file_name>')
def con_filter(file_name):
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

    img = np.array(Image.open(path).filter(ImageFilter.CONTOUR))
    img_class.save_img(img, path.replace('original', 'modified'))
    return redirect(url_for('index'))


# Blur filter
@app.route('/blur_filter/<file_name>')
def blur_filter(file_name):
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

    img = np.array(Image.open(path).filter(ImageFilter.GaussianBlur(radius=4)))
    img_class.save_img(img, path.replace('original', 'modified'))
    return redirect(url_for('index'))


# Emboss filter
@app.route('/emb_filter/<file_name>')
def emb_filter(file_name):
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

    img = np.array(Image.open(path).filter(ImageFilter.EMBOSS))
    img_class.save_img(img, path.replace('original', 'modified'))
    return redirect(url_for('index'))


# color filter
@app.route('/color/<file_name>')
def only_color(file_name,a=1):
    cookie = request.cookies.get('Color_buttons')
    if cookie is not None:
        cookie = cookie[3:]
        cookie = cookie.strip() #making list from id numers from cookie file

        color = [color_floor_top[i] for i in range(0,len(color_floor_top)) if str(i) in cookie]

        path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

        img = None
        for i in color:
            lower = (int(i[0]), int(i[1]), int(i[2]))
            upper = (int(i[3]), int(i[4]), int(i[5]))

            print(lower,upper)
            result = img_class.display_color(path, lower, upper)
            if img is None:
                img = result
            else:
                img = cv2.add(img,result)

        if img is not None:
            path = path.replace('original', 'modified')
            img_class.save_img(img, path.replace('original', 'modified'))

    return redirect(url_for('index'))

# Page with download window
@app.route('/download/<file_name>', methods=['POST', 'GET'])
def download(file_name):
    if request.method == 'GET':
        path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

        # Checking with function in img_class size of file with certain extension, by creating file in temp.
        jpg = img_class.get_image_size(app, file_name, 'jpg')
        png = img_class.get_image_size(app, file_name, 'png')
        tiff = img_class.get_image_size(app, file_name, 'tiff')
        gif = img_class.get_image_size(app, file_name, 'gif')

        file_sizes = [jpg, png, tiff, gif]

        return render_template('download_window.html', file_name=file_name, url_download='#', file_sizes=file_sizes)
    else:
        format = request.form['format']



        return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
