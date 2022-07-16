import numpy as np

def resizing_vector(data, width, height):
    data = list(data.values()) # to store values only of the input json string
    data = np.array(data)
    data = np.reshape(data,(height, width))
    data = data[::2,::2]
    return data
