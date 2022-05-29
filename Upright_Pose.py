import cv2 as cv
import numpy as np
import dlib
import time
from tkinter import messagebox
import os
import Upright_DB
import tensorflow.keras
from scipy.spatial import distance as dist
from imutils import face_utils
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
classes = ['fine', 'turtle']
model = tensorflow.keras.models.load_model('keras_model.h5')

# For static images:
IMAGE_FILES = []
size = (224, 224)
BG_COLOR = (192, 192, 192) # gray
ear = 0
start = time.time()
setTime = 0
middleTime = time.time()
def Save_Cam():
    now = time.localtime()
    name = str(now.tm_year)+str(now.tm_mon)+str(now.tm_mday)+str("_") + \
        str(now.tm_hour)+str("_")+str(now.tm_min)+str("_")+str(now.tm_sec)
    return name
# # For webcam input--------------------------------------------------------------------------
def camStart():

# eye function------------------------------------------------------------------------------
    def eye_aspect_ratio(eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    EYE_AR_THRESH = 0.25
    EYE_AR_CONSEC_FRAMES = 2
    COUNTER = 0
    TOTAL = 0
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    lStart, lEnd = (42, 48)
    rStart, rEnd = (36, 42)
# ------------------------------------------------------------------------------------------
    cap = cv.VideoCapture(0)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 900)
    turtle_Count=0
    while cap.isOpened():
# turtle ----------------------------------------------------------------------------------
        ret, img = cap.read()
        if not ret:
            break

        h, w, _ = img.shape
        cx = h / 2
        img = img[:, 200:200+img.shape[0]]
        img = cv.flip(img, 1)

        img_input = cv.resize(img, size)
        img_input = cv.cvtColor(img_input, cv.COLOR_BGR2RGB)
        img_input = (img_input.astype(np.float32) / 127.0) - 1
        img_input = np.expand_dims(img_input, axis=0)

        prediction = model.predict(img_input)
        idx = np.argmax(prediction)
        if idx==1:
            turtle_Count+=1
        if idx==1 and turtle_Count>100:
            # messagebox.showinfo("경고", "거북목입니다!")
            # -------------------------알림 로직-----------------------------
            print("-------------------------------------------")
            global start, middleTime, setTime
            start = time.time()  # 시작 시간 저장

            if((time.time() - middleTime) > setTime):
                MsgBox = messagebox.askquestion(
                    "알림", "거북목입니다.(no 누를시 무시시간 연장)")
               # Upright_DB.Count_Habit("turtle")
                path = "png_files/" + str("habit_") + Save_Cam() + ".png"
                cv.imwrite(path, img)
                Upright_DB.insertBLOB(path)

                if MsgBox == 'yes':
                    print('----------yes click-----------')
                    print("time :", time.time() - start)
                    print("setTime : ", setTime)
                else:
                    print('----------no click------------')
                    setTime = setTime + \
                        (time.time() - start) * 5
                    middleTime = time.time()
                    print("setTime :", setTime)
                    print("middleTime : ", middleTime)
            # ——————————————————————————
            else:
                print(
                    "—————————거북목 감지했으나 알림은 ㄴㄴ——————————")
                print(time.time() - middleTime, '<=', setTime)
            turtle_Count=0
            
# eye---------------------------------------------------------------------------------------
        success, image = cap.read()
        image = cv.flip(image, 1)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for rect in rects:
            global ear
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv.convexHull(leftEye)
            rightEyeHull = cv.convexHull(rightEye)

            cv.drawContours(image, [leftEyeHull], -1, (0, 255, 0), 1)
            cv.drawContours(image, [rightEyeHull], -1, (0, 255, 0), 1)
            if ear < EYE_AR_THRESH:
                COUNTER += 1
            else:
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL += 1
                COUNTER = 0

        cv.putText(image, "Blinks: {}".format(TOTAL), (10, 30),
                cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv.putText(image, "EAR: {:.2f}".format(ear), (250, 30),
                cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)        
        cv.putText(image, text=classes[idx], org=(500, 30),
         fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=(0, 0, 255), thickness=2)    
# ------------------------------------------------------------------------------------------
        cv.imshow('Pose', image)
        if cv.waitKey(5) & 0xFF == 27:
            break
        if cv.getWindowProperty("Pose", cv.WND_PROP_VISIBLE) <1:  # X버튼을 누르면 창 닫기 -> 창이 닫혔는지 감지하면 종료, 다시 실행되는 것을 방지
            break
    cap.release()