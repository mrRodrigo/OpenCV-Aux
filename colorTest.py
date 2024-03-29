# python color_tracking.py --video balls.mp4
# python color_tracking.py

# import the necessary packages
from collections import deque
import numpy as np
import argparse
import imutils
import cv2
import urllib  # for reading image from URL
import pyodbc

############################# B A N C O ###########
server = 'localhost\sqlexpress'
database = 'teste'
username = 'sa'
password = 'nimp2017'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
##############################


qtdframe = 0
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the colors in the HSV color space
lower = {'VERMELHO': (166, 84, 141), 'VERDE': (66, 122, 129), 'AZUL': (97, 100, 117), 'AMARELO': (23, 59, 119)
         }  # assign new item lower['blue'] = (93, 10, 0)
upper = {'VERMELHO': (186, 255, 255), 'VERDE': (86, 255, 255), 'AZUL': (117, 255, 255), 'AMARELO': (54, 255, 255)}

# define standard colors for circle around the object
colors = {'VERMELHO': (0, 0, 255), 'VERDE': (0, 255, 0), 'AZUL': (255, 0, 0), 'AMARELO': (0, 255, 217),
          'LARANJA': (0, 140, 255)}

# pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture('vid/teste1.jpg')


# otherwise, grab a reference to the video file
else:
    camera = cv2.VideoCapture(args["video"])
# keep looping

frameVermelho = 0
frameAmarelo =  0
frameVerde = 0
frameLaranja = 0
frameAzul = 0

voltasVermelho = 0
voltasAmarelo =  0
voltasVerde = 0
voltasLaranja = 0
voltasAzul = 0


while True:
    # grab the current frame
    (grabbed, frame) = camera.read()

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if args.get("video") and not grabbed:
        break

    # IP webcam image stream
    # URL = 'http://10.254.254.102:8080/shot.jpg'
    # urllib.urlretrieve(URL, 'shot1.jpg')
    # frame = cv2.imread('shot1.jpg')


    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=1080)

    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)


    # for each color in dictionary check object in frame
    for key, value in upper.items():
        # construct a mask for the color from dictionary`1, then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask

        kernel = np.ones((9, 9), np.uint8)

        mask = cv2.inRange(hsv, lower[key], upper[key]) #Aqui aplica uma mascara ignorando os pixeis que não estiverem entre
                                                        #Lower e upper

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))


            if radius > 50: # se o raio do objeto é 0.5 marca e pontua

                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                if key == "VERMELHO":
                    #if (qtdframe - frameVermelho) > 300:
                        print(key + "Pontuou")
                        frameVermelho = qtdframe
                        voltasVermelho += 1

                if key == "AMARELO":
                    #if (qtdframe - frameAmarelo) > 300:
                        print(key + "Pontuou")
                        frameAmarelo = qtdframe
                        voltasAmarelo += 1

                if key == "VERDE":
                    #if (qtdframe - frameVerde) > 300:
                        print(key + "Pontuou")
                        frameVerde = qtdframe
                        voltasVerde += 1

                if key == "AZUL":
                    #if (qtdframe - frameAzul) > 300:
                        print(key + "Pontuou")
                        frameAzul = qtdframe
                        voltasAzul += 1

                #if key == "LARANJA":
                 #   if (qtdframe - frameLaranja) > 300:
                  #      print(key + "Pontuou")
                   #     frameLaranja = qtdframe


                cv2.circle(frame, (int(x), int(y)), int(radius), colors[key], 2)
                cv2.putText(frame,  "Pontuou", (int(x - radius), int(y - radius)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors[key], 2)
                cursor.execute("INSERT INTO tabela(teste)VALUES ('ponto')")




    # show the frame to our screen
    qtdframe += 1
    cv2.putText(frame, "Voltas Vermelho: " + str(voltasVermelho) , (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8 ,colors["VERMELHO"], 4)
    cv2.putText(frame, "Voltas Amarelho: " + str(voltasAmarelo), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors["AMARELO"], 4)
    cv2.putText(frame, "Voltas Verde: "+ str(voltasVerde), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors["VERDE"], 4)
    cv2.putText(frame, "Voltas Azul: "+ str(voltasAzul), (20, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors["AZUL"], 4)

    cv2.imshow("Frame", frame)


    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()