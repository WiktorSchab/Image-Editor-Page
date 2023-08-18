import numpy as np
import cv2
import os

def colorize(file_name, app):
    # Path to models and data (they are from https://github.com/richzhang/colorization)
    prototxt_path = 'colorize/models/colorization_deploy_v2.prototxt'
    model_path = 'colorize/models/colorization_release_v2.caffemodel'
    kernel_path = 'colorize/models/pts_in_hull.npy'

    # Path to image and path where to save image
    path_input = os.path.join(app.root_path, 'static', 'download', 'original', file_name)
    path_output = path_input.replace('original','modified')
    image_path = path_input

    # Loading pretrain modal
    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    points = np.load(kernel_path)

    # Configuration of model
    points = points.transpose().reshape(2, 313, 1, 1)
    net.getLayer(net.getLayerId('class8_ab')).blobs = [points.astype(np.float32)]
    net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, dtype='float32')]

    # Loading image in grayscale and converting it to LAB
    bw_image = cv2.imread(image_path)
    normalized = bw_image.astype('float32') / 255.0
    lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)

    # Preparing image for transformation (image must be 244x244)
    resized = cv2.resize(lab, (244, 244))
    L = cv2.split(resized)[0]
    L -= 50

    # Calling neural model and processing result
    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    ab = cv2.resize(ab, (bw_image.shape[1], bw_image.shape[0]))
    L = cv2.split(lab)[0]

    # Joining L channels and transmitting img into BGR
    colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)
    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = (255.0 * colorized).astype('uint8')

    # Saving image
    cv2.imwrite(path_output, colorized)