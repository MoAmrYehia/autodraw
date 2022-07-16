from PIL import Image
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
import numpy as np
import pandas as pd

import time

file_name = "data.csv"
weights = "vgg16_weights_tf_dim_ordering_tf_kernels.h5"

class FeatureExtractor:
    def __init__(self):
        
        # Use VGG-16 as the architecture and ImageNet for the weight
        base_model = VGG16(weights=weights)
        # Customize the model to return features from fully-connected layer
        self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)
        
    def extract(self, img):
        
        # Resize the image
        img = img.resize((224, 224))
        # Convert the image color space
        img = img.convert('RGB')
        
        # Reformat the image
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        # Extract Features
        feature = self.model.predict(x)[0]
        return feature / np.linalg.norm(feature)


    
def perdict_img(file):
    
       
    fe = FeatureExtractor()
    img = Image.fromarray(file, mode='L')
    
    # Extract its features
    query = fe.extract(img)
    
    start =time.time()
    
    features = pd.read_csv(file_name).drop(columns=["Unnamed: 0", "Unnamed: 0.1", "Unnamed: 0.1.1"])
    end =time.time()
    print("totall = " + str(end - start))

    # Calculate the similarity (distance) between images
    features_data = features.drop(columns = ['image'])
    features_data = features_data.values
    
    dists = np.linalg.norm(features_data - query, axis=1)
    
    
    # Extract 30 images that have lowest distance
    
    ids = np.argsort(dists)[:10]
    
    lookalike_imgs = features.iloc[ids,:]['image']

    
    scores = pd.DataFrame({'image': lookalike_imgs})

    scores = scores.reset_index(drop=True) 
    scores = scores.to_json(orient='index')
    

    return scores

