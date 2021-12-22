import cv2
import numpy as np
from base64 import b64encode
from base64 import b64decode
import json

# Extract base64 from JSON
b64_r = input("give binary64 image\n")

# Extract JPEG-encoded image from base64-encoded string
JPEG_r = b64decode(b64_r)

# Decode JPEG back into Numpy array
na_r = cv2.imdecode(np.frombuffer(JPEG_r,dtype=np.uint8), cv2.IMREAD_COLOR)
cv2.imshow('Image',na_r)
