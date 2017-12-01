import argparse
import imutils
import cv2
import sys
import numpy as np
from FindMagnets import CompareImg

class HandleImage:

	@staticmethod
	def PrepareSourceImage(img):
		#Resize
		resized = imutils.resize(img, width=1024)
		ratio = img.shape[0] / float(resized.shape[0])
		#Grey and Blur
		gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
		blurred = cv2.GaussianBlur(gray, (5, 5), 0)
		#Thresh
		thresh = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
		#cv2.imshow("PrepareSourceImage", thresh)
		return thresh


	@staticmethod
	def GetMagnets(img, crop):
		compareImg = CompareImg()
		magnets = compareImg.findAllMagnets(img, crop)
		return magnets


	@staticmethod
	def GetMostSmallerAndMostBiggerDots(magnets):
		return [min(magnets), max(magnets)]

	@staticmethod
	def CutTheBoard(img, magnets):
		board_w = magnets[1][0] - magnets[0][0]
		board_h = magnets[1][1] - magnets[0][1]
		board_x = magnets[0][0]
		board_y = magnets[0][1]
		crop_img = img[board_y:(board_y + board_h), board_x:(board_x + board_w)] 
		# Crop from x, y, w, h -> 100, 200, 300, 400
		# NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
		#cv2.imshow("cropped", crop_img)
		#cv2.waitKey(0)

		return crop_img

	"""
	Parms:
		magGrpA = the saved set of magnets
		magGrpB = the new set of magnets
		th = the allowed treshold. This is the x,y position of the magnet + the amount of pixels outside of this position

	Compares two sets of x,y coordinates (one from a saved image and the other from a current image) representing the location of the magnets on the board.
	If any of the x,y coordinates lie outside the given treshold, then the change is significant enough to return true (i.e change is detected) 
	If no change detected return False
	"""
	@staticmethod
	def hasAnyMagnetLocationChanged(magGrpA, magGrpB, th):  
		#If array are not equal i nlength, something has been added or removed from the board
		if not len(magGrpA) == len(magGrpB):
			return True
		
		#Loop through arrays, compare each X and Y coordinate of the input array. Check if they are within the defined
		#threshold (th). If they are nothing has changed. If any is not, return True to signify something has changed
		for i in range (0, len(magGrpA)-1):
			for j in range (0, 1):
				
				if not magGrpB[i][j] <= magGrpA[i][j] + th or not magGrpB[i][j] >= magGrpA[i][j] - th:
					return True
		
		#Return false if no changes detected
		return False
