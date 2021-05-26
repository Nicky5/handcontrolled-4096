import math
import threading

import cv2
import time
import os
import mediapipe as mp
import pygame as pg

import main

dir = None
end = False

def awake():

    wCam, hCam = 640, 480

    camera = cv2.VideoCapture(0)
    camera.set(3, wCam)
    camera.set(4, hCam)

    folderPath = "FingerImages"
    # myList = os.listdir(folderPath)
    # print(myList)
    overlayList = []
    # for imPath in myList:
    #     image = cv2.imread(f'{folderPath}/{imPath}')
    #     print(f'{folderPath}/{imPath}')
    #     overlayList.append(image)

    print(len(overlayList))
    pTime = 0

    detector = handDetector(detectionCon=0.75)

    tipIds = [4, 8, 12, 16, 20]

    runs = 0
    prev_pos = 0
    while main.set.loop_on:
        success, img = camera.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        img = cv2.flip(img, 1)
        frm = img.swapaxes(0, 1)
        frm = cv2.cvtColor(frm, cv2.COLOR_BGR2RGB)
        pg.surfarray.blit_array(main.cam, frm)

        totalFingers = 0
        hand_open = False
        if len(lmList) != 0:
            fingers = []
            for id in range(1, 5):
                if math.sqrt(((lmList[tipIds[id]][1] - lmList[tipIds[id] - 3][1]) ** 2) + (
                        (lmList[tipIds[id]][2] - lmList[tipIds[id] - 3][2]) ** 2)) > 60:
                    fingers.append(1)
                else:
                    fingers.append(0)

            totalFingers = fingers.count(1)
            if totalFingers == 4:
                hand_open = True

            main.Hand_open = hand_open

        cTime = time.time()
        fps = 1 / (cTime - pTime) * 1
        pTime = cTime

        main.cam_fps = fps

        # cv2.imshow("Image", img)
        cv2.waitKey(1)

        positions = []
        print('hand detector')
        if hand_open:
            points = []
            for id in range(1, 5):
                if math.sqrt(((lmList[tipIds[id]][1] - lmList[tipIds[id] - 3][1]) ** 2) + (
                        (lmList[tipIds[id]][2] - lmList[tipIds[id] - 3][2]) ** 2)) > 60:
                    points.append(lmList[tipIds[id]][1:])
            positions.append(points)
            if runs % 10 == 0:
                x_poses = []
                y_poses = []
                for frame in positions:
                    x_poses.append(average([i[0] for i in frame]))
                    y_poses.append(average([i[1] for i in frame]))

                current_pos = average(x_poses), average(y_poses)

                print(current_pos)

                if not prev_pos == 0:
                    offset = 100
                    if prev_pos[0] > current_pos[0] + offset:
                        main.animation_start = time.time()
                        main.move_piece(pg.K_RIGHT)
                        threading.Thread(target=main.after_animation).start()

                    if prev_pos[0] < current_pos[0] - offset:
                        main.animation_start = time.time()
                        main.move_piece(pg.K_LEFT)
                        threading.Thread(target=main.after_animation).start()

                    if prev_pos[1] > current_pos[1] + offset:
                        main.animation_start = time.time()
                        main.move_piece(pg.K_UP)
                        threading.Thread(target=main.after_animation).start()

                    if prev_pos[1] < current_pos[1] - offset:
                        main.animation_start = time.time()
                        main.move_piece(pg.K_DOWN)
                        threading.Thread(target=main.after_animation).start()

                prev_pos = current_pos

        else:
            runs = 0
            positions.clear()
        runs += 1

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList

def average(lst):
    try:
        return sum(lst) / len(lst)
    except ZeroDivisionError:
        return 0

if main.hand_detection:
    threading.Thread(target=awake).start()
    threading.Thread(target=main.game_loop).start()
