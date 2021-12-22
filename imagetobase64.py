import cv2
import numpy as np
from base64 import b64encode
from base64 import b64decode
import json


# Get any old image, 640x480 pixels - corresponds to your "frame"
na = cv2.imread('../image-12-1030x579.png', cv2.IMREAD_COLOR)
print(f'DEBUG: Size as Numpy array: {na.nbytes}')

# Convert to "in-memory" JPEG
_, JPEG = cv2.imencode(".jpg", na, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
print(f'DEBUG: Size as JPEG: {JPEG.nbytes}')
JPEG.tofile('DEBUG-original.jpg')

# Base64 encode
b64 = b64encode(JPEG)
print(f'DEBUG: Size as base64: {len(b64)}')
print(f'DEBUG: Start of base64: {b64[:32]}...')

# JSON-encode
message = { "image": b64.decode("utf-8") }
messageJSON = json.dumps(message)
print(f'DEBUG: Start of JSON: {messageJSON[:32]}')

# Extract base64 from JSON
b64_r = json.loads(messageJSON)

# Extract JPEG-encoded image from base64-encoded string
JPEG_r = b64decode(b64_r["image"])

# Decode JPEG back into Numpy array
na_r = cv2.imdecode(np.frombuffer(JPEG_r,dtype=np.uint8), cv2.IMREAD_COLOR)
cv2.imshow('Image',na_r)
