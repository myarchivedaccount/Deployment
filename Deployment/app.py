import os
import sys

# Flask
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import Model
from tensorflow.keras import layers
from keras.utils import to_categorical
from tensorflow.keras.layers import BatchNormalization
from keras.models import Model
from keras.layers import Dense, Dropout, Activation, BatchNormalization, Flatten
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras.optimizers import Adam
import efficientnet.keras as enet
from keras.backend import sigmoid
from keras import optimizers
from tensorflow_addons.losses import SigmoidFocalCrossEntropy
# Some utilites
import numpy as np
from util import base64_to_pil


# Declare a flask app
app = Flask(__name__)


# You can use pretrained model from Keras
# Check https://keras.io/applications/
# or https://www.tensorflow.org/api_docs/python/tf/keras/applications

# Model saved with Keras model.save()
MODEL_PATH = 'C:/Users/ADMIN/keras-flask-deploy-webapp/models/model_finetune_40epoch_Efficientnet_focalloss.h5'

class SwishActivation(Activation):
    
    def __init__(self, activation, **kwargs):
        super(SwishActivation, self).__init__(activation, **kwargs)
        self.__name__ = 'swish_act'

def swish_act(x, beta = 1):
    return (x * sigmoid(beta * x))

model =load_model(MODEL_PATH,custom_objects={"swish_act":swish_act})

#model._make_predict_function()          # Necessary

print('Model loaded. Check http://127.0.0.1:5000/')

print('Model loaded. Start serving...')


def model_predict(img, model):
    img = img.resize((224, 224))
    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    x = np.expand_dims(x, axis=0)
    x = x.astype('float32')
    x /= 255.0
    preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Get the image from post request
        img = base64_to_pil(request.json)

        # Save the image to ./uploads
        # img.save("./uploads/image.png")

        # Make prediction
        preds = model_predict(img, model)
        
        class_id=tf.argmax(preds,1)
        
        if (class_id==0):
            result='bicycle'
  
        if (class_id==1):
            result='bus'
        
        if (class_id==2):
            result='car'
  
        if (class_id==3):
            result='motor'
    
        if (class_id==4):
            result='other'

        if (class_id==5):
            result='pedestrian'

        if (class_id==6):
            result='tricycle'

        if (class_id==7):
            result='truck'
        
        if (class_id==8):
            result='van'
        
        # Serialize the result, you can add additional fields
        return jsonify(result=result)

    return None


if __name__ == '__main__':
    # app.run(port=5002, threaded=False)

    # Serve the app with gevent
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
