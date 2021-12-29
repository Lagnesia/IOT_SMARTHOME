import cv2
import numpy as np
import boto3

Access_key_id = 'YourIdHere'
Access_secret_key = 'YourKeyHere'
bucket_id = 'family-face'

face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


def face_extractor(img):

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray,1.3,5)

    if faces is():
        return None

    for(x,y,w,h) in faces:
        cropped_face = img[y:y+h, x:x+w]

    return cropped_face

def handle_upload_img(f):
    s3_client = boto3.client('s3',
                             aws_access_key_id = Access_key_id,
                             aws_secret_access_key = Access_secret_key)
    response = s3_client.upload_file('faces/'+ f + '.jpg', bucket_id,  f + '.jpg')
    
    
def face_capture():
    cap = cv2.VideoCapture(0)
    count = 0
    
    while True:
        ret, frame = cap.read()
        if face_extractor(frame) is not None:
            count+=1
            face = cv2.resize(face_extractor(frame),(200,200))
            temp_face = cv2.resize(face_extractor(frame),(200,200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    
            file_name_path = 'faces/User'+str(count)+'.jpg'
            cv2.imwrite(file_name_path,temp_face)
            handle_upload_img('User'+str(count))
    
            cv2.putText(face,str(count),(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
            cv2.imshow('Face Cropper',face)
        else:
            print("Face not Found")
            pass
    
        if cv2.waitKey(1)==13 or count==1:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print('Colleting Samples Complete!!!')    
    
face_capture()
