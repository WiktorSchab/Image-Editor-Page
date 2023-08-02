from flask import Flask, render_template, url_for, request, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
import os
from matplotlib.image import imread
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from img_funct import img_class

app = Flask(__name__)
app.config['SECRET_KEY'] = 'P@$$w0rda'


class FileForm(FlaskForm):
    cover = FileField("Send me a pic (only jpg, png need to show off validation skills)", validators=[FileRequired(),
                                                            FileAllowed(['jpg', 'png'], "Sorry, only png and jpg")])


# starting page
@app.route('/', methods=['POST', 'GET'])
def index(d={'access': 0, 'path': None, 'filename': None}):
    form = FileForm()

    if d['access'] == 1 or form.validate_on_submit():
        d['access'] = 1  # access to edit

        if not d['path']:
            f = form.cover.data
            filename = secure_filename(f.filename)
            path = os.path.join(app.root_path, 'static', 'download', filename)
            f.save(path)

            # saving values to dict, so they won't be refreshed
            d['filename'] = filename
            d['path'] = path

        path = d['path']
        filename = d['filename']

        img = np.array(Image.open(path).resize((256, 256)))
        img_class.save_img(img, path)

        return render_template('work_page.html', file_name=filename, path=os.path.join('download', filename))
    return render_template('index.html', form=form)

#Black & white filter
@app.route('/bw_filter/<file_name>')
def bw_filter(file_name):
    path = os.path.join(app.root_path, 'static', 'download', file_name)

    img = np.array(Image.open(path).convert('L'))
    img_class.save_img(img, path)
    return redirect(url_for('index'))

#Real black & white filter
@app.route('/op_filter/<file_name>')
def rbw_filter(file_name):
    path = os.path.join(app.root_path, 'static', 'download', file_name)

    img = np.array(Image.open(path).convert('1'))
    img_class.save_img(img, path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
