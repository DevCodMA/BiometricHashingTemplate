import cv2
import face_recognition
import sqlite3
import base64
import numpy as np
import pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import io

#Converting base64 to image
b2i = (lambda img: cv2.imdecode(np.frombuffer(base64.b64decode(img.split(',')[1]), np.uint8), cv2.IMREAD_COLOR))

#Encrypting image data
encrypt_data = (lambda data, key: AES.new(str(key).ljust(16, '0').encode('utf-8'), AES.MODE_ECB).encrypt(pad(data, AES.block_size)))

#Decrypting image data
decrypt_data = (lambda data, key: unpad(AES.new(str(key).ljust(16, '0').encode('utf-8'), AES.MODE_ECB).decrypt(data), AES.block_size))

#Checking the image contains only one person
def checkPerson(img):
   
    face_cascade = cv2.CascadeClassifier(os.path.join(os.path.dirname(os.path.realpath(__file__)), "res", "haarcascade_frontalface_default.xml"))
    try:
        gscale = cv2.cvtColor(b2i(img), cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gscale, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        if len(faces) == 1:
            return (True, 1)
        elif len(faces) > 1:
            return (False, 2)
        else:
            return (False, 3)
    except:
        return (False, 0)
    
#Converting image into face_locations
def getFaceEncodings(img):
    if checkPerson(img):
        try:
            img = cv2.cvtColor(cv2.resize(b2i(img), (0, 0), None, 0.25, 0.25), cv2.COLOR_BGR2RGB)
            floc = face_recognition.face_locations(img)
            encodings = face_recognition.face_encodings(img, floc)[0]
            return encodings
        except:
            return None
    else:
        return None

#Comparing faces
def recognize_face(img, phone):
    try:
        if checkPerson(img):
            try:
                conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "user_information.db"))
                res = conn.execute(f"SELECT IMAGE, EMAILID FROM USER_INFORMATION WHERE PHONENO='{phone}'").fetchone()
                ref_img = pickle.loads(decrypt_data(res[0], phone))
                img = getFaceEncodings(img)
                conn.close()
                if face_recognition.compare_faces([ref_img], img, 0.4)[0]:
                    return True, True
                else:
                    return False, False
            except Exception as ex:
                return (False, False)
    except:
        return (False, 0)

#Registering a new user 
def register(fname, emailid, accno, phoneno, img):
    try:
        img = getFaceEncodings(img)
        imdata = io.BytesIO()
        pickle.dump(img, imdata)
        img = encrypt_data(imdata.getvalue(), phoneno)
        conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "user_information.db"))
        res = conn.execute("INSERT INTO USER_INFORMATION VALUES (?, ?, ?, ?, ?)", (fname, emailid, phoneno, accno, img))
        conn.commit()
        conn.close()
        return "User registration successfull!"
    except Exception as ex:
        return f"{ex}"


def test(phonenum):
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", "user_information.db"))
    res = conn.execute(f"SELECT IMAGE, EMAILID FROM USER_INFORMATION WHERE PHONENO='{phonenum}'").fetchall()
    # ref_img = pickle.loads(decrypt_data(res[0], phonenum))
    print(res)