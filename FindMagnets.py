# import the necessary packages
import imutils
import numpy as np
import cv2
import sys

class CompareImg:
		
	@staticmethod
	def findAllMagnets(img, crop):
		#cv2.imshow("findMagnets", img)

		img_height, img_width = img.shape[:2]
	
		lst = []
	
		#cropped board width
		board_w = 1100.0
		
		#cropped board height
		board_h = 810.0
		
		#first cell width
		first_cell_width = 232.0
		first_cell_width_ratio = first_cell_width / board_w
		first_cell_width_calculated = img_width * first_cell_width_ratio
		
		#first cell height
		first_cell_height = 95.0
		first_cell_height_ratio = first_cell_height / board_h
		first_cell_height_calculated = img_height * first_cell_height_ratio
		
		#magnet width
		magnet_w = 30.0
		
		#magnet to board width ratio 
		magnet_2_board_w_ratio = magnet_w / board_w
		magnet_2_board_h_ratio = magnet_w / board_h
		
		#calculated magnet dimensions
		magnet_w_calculated = img_width * magnet_2_board_w_ratio
		magnet_h_calculated = img_height * magnet_2_board_h_ratio
		
		#threshold
		threshold = 0.5
		
		#min calculated magnet width
		magnet_w_calculated_min = magnet_w_calculated - magnet_w_calculated * threshold
		
		#max calculated magnet width
		magnet_w_calculated_max = magnet_w_calculated + magnet_w_calculated * threshold
		
		#min calculated magnet height
		magnet_h_calculated_min = magnet_h_calculated - magnet_h_calculated * threshold
		
		#max calculated magnet height
		magnet_h_calculated_max = magnet_h_calculated + magnet_h_calculated * threshold
		crop_img = img
		if crop:
			crop_img = img[int(first_cell_height_calculated):img_height, int(first_cell_width_calculated):img_width]
		# find contours in the thresholded image and initialize the
		# shape detector
		#cnts = cv2.findContours(crop_img.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
		#cnts = cnts[0] if imutils.is_cv2() else cnts[1]
		#sd = ShapeDetector()
		#gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		
		#output = crop_img.copy()
		circles = cv2.HoughCircles(crop_img,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=0,maxRadius=0)
		#circles = cv2.HoughCircles(crop_img,cv2.HOUGH_GRADIENT,1.2, 100)
		#circles = cv2.HoughCircles(crop_img,cv2.HOUGH_GRADIENT, 1, 20, 10, 40, 5, 10)

		circles = np.uint16(np.around(circles))
		for i in circles[0,:]:
			if int(i[2]) >= int(magnet_w_calculated_min / 2.0) and int(i[2]) <= int(magnet_w_calculated_max / 3.0):
				# draw the outer circle
				cv2.circle(crop_img,(i[0],i[1]),i[2],(0,255,0),2)
				# draw the center of the circle
				#cv2.circle(crop_img,(i[0],i[1]),2,(0,0,255),3)
				lst.append( [i[0],i[1]] )
		
		#cv2.imwrite("circles.jpg",crop_img)
		
		# show the output image
		#cv2.imshow("Image with circles", crop_img)
		#cv2.waitKey(0)
		
		
		return lst
