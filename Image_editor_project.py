from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename

import os
import shutil

import numpy as np
from PIL import Image, ImageFilter

from img_funct import img_class

app = Flask(__name__)
app.config['SECRET_KEY'] = 'P@$$w0rda'


class FileForm(FlaskForm):
    cover = FileField("Send me a pic (only jpg, png need to show off validation skills)", validators=[FileRequired(),
                                                                                                      FileAllowed(
                                                                                                          ['jpg',
                                                                                                           'png'],
                                                                                                          "Sorry, only png and jpg")])


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
            img = np.array(Image.open(path).resize((1024, 1024)))
            img_class.save_img(img, path)

            # making copy of img
            shutil.copyfile(path, path.replace('modified', 'original'))

            # saving values to dict, so they won't be refreshed
            d['filename'] = filename
        filename = d['filename']

        return render_template('work_page.html', file_name=filename)
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


# color filters
@app.route('/<color>/<file_name>')
def only_color(file_name,color):
    path = os.path.join(app.root_path, 'static', 'download', 'original', file_name)

    color = color[1:-1].split(',')
    color = [int(i.strip()) for i in color]

    lower = (color[0], color[1], color[2])
    upper = (color[3], color[4], color[5])

    result = img_class.display_color(path, lower, upper)
    img_class.save_img(result, path.replace('original', 'modified'))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
