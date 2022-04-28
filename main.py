import math
import os.path
import random

import cvzone
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# IDEAS :
# snake width gradient
# snake color gradient
# harry potter blanket


camer = cv2.VideoCapture(0)
camer.set(3, 1280 )
camer.set(4, 720 )

detector  = HandDetector(detectionCon=0.8 , maxHands= 1 )

class fruitclass:
    def __init__(self , imagepath ):

        self.fruit_image = cv2.imread( imagepath , cv2.IMREAD_UNCHANGED )
        self.height , self.width , _  = self.fruit_image.shape
        self.location = 0 , 0  #initially food is at 0,0
        self.change_location() # we change the food location during initialization itself

    def change_location ( self ) :  # generates a new location randomly
        self.location = random.randint(100,1000) , random.randint(100 , 600)


    def drawfood ( self , backImg ) :
        x , y = self.location
        # print(x,y)
        # print((x-self.width//2 , y - self.height//2 ))
        backImg = cvzone.overlayPNG( backImg , self.fruit_image , (x-self.width//2 , y - self.height//2 ) )

        return backImg

    def has_been_eaten ( self , valid ) :
        if valid :
            self.change_location()

class snakeclass:

    #
    def __init__(self):
        self.nodes = [] # all nodes that when joined in order , define the snake , last node is head
        self.segLen = [] # lengths of each segment formed between two succesive nodes
        self.snakeLen = 0   # the current length of the snake
        self.snakeExp = 0 # the experience of the snake, eating a fruit increases its exp
        self.levelLen = 200  # as the level increases it is allowed to grow longer
        self.prevhead = 0 , 0  # assume 0,0 as the head until the saanp starts

    #
    def refresh ( self , newhead ) : # new head is given by the index pointer


        newSeg = math.hypot( newhead[0] - self.prevhead[0] , newhead[1] - self.prevhead[1] )
        if newSeg > 5:
            self.nodes.append(newhead)
            self.segLen.append(newSeg)
            self.snakeLen += newSeg

            self.prevhead = newhead

            while (self.snakeLen > self.levelLen):
                self.nodes.pop(0)
                self.snakeLen -= self.segLen.pop(0)  # keep removing the tail elements

            # self.check_collision()
    #
    def check_collision ( self ) :
        for i,_ in enumerate( self.nodes ) :
            if i > 2 :
                ix , iy  = self.nodes[len(self.segLen)-i-2]
                # jx , jy  = self.nodes[i-1]
                px , py  = self.prevhead
                # if ( (px - jx )*(py - iy ) == (px - ix)*(py - jy ) and (px - jx )*(py - iy ) <= 0  ) :
                if ( px == ix and py == iy ) :
                    self.clearall()
    #
    def drawsnake ( self , newImg ) : # shows the snake on the screen
        #to draw the snake
        for i,node in enumerate(self.nodes):
            if i  :      #  atleast two nodes are required to draw a snake , i = 0 is first node index
                # cv2.line(newImg , self.nodes[i-1], self.nodes[i], (0,10 , 255)  , 9 ) #node can be used instead of self.nodes[i]
                cv2.line(newImg , self.nodes[i-1], self.nodes[i], (40,255 , 90)  , 12 ) #node can be used instead of self.nodes[i]

        if self.nodes:  # there should be atleast one node ( that node is head )
            cv2.circle(newImg, self.nodes[-1], 20 , (100, 100, 20), cv2.FILLED) # -1 as index means refers to the last element

        return newImg


    #
    def can_eat(self , fruit_location):
        px , py = self.prevhead
        fx , fy = fruit_location

        dist = math.hypot(px-fx , py - fy )

        if ( dist < 40 ) :
            self.snakeExp += 1
            self.levelLen = 150 + int ( math.sqrt (self.snakeExp) ) *30

            return True

        else :

            return False


    #
    def clearall ( self ) :
        self.nodes.clear()
        self.segLen.clear()
        self.snakeExp = 0
        self.levelLen = 150
        self.prevhead = 0 , 0
        self.snakeLen = 0


saanp = snakeclass()
apple = fruitclass("donut.png")
count = 0
samples = 0
while True:
    suc, img = camer.read()
    img = cv2.flip(img,1 )
    imgg = img
    hands, _ = detector.findHands(img , flipType= 0 )


    if ( hands ) :
        if ( hands[0]["type"] == "Right")  :
            imppointlist = hands[0]['lmList']   # land mark list
            indexpointer = imppointlist[8][0:2] # 2 is exclusive , x , y , z ; z not needed
            saanp.refresh( indexpointer )
            count = 0
        else :
            count += 1
            if count > 40 :
                saanp.clearall()
                count = 0


        # eat


    apple.has_been_eaten (  saanp.can_eat ( apple.location )  )

    imgg = saanp.drawsnake(imgg)  # draw the snake on the image where hand is detected
    imgg = apple.drawfood (imgg)  # draw food on the image on which snake is already drawn
    cv2.imshow("thatis" , imgg )
    # samples += 1
    # print( samples )

    cv2.waitKey(1)
