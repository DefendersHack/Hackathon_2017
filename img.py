import argparse
import imutils
import cv2
import numpy as np
from HandleImage import HandleImage


def isChanged(oldImg, newImg):
	hi = HandleImage()
	oldImgMagnets = find2(oldImg, hi)
	newImgMagnets = find2(newImg, hi)
	return hi.hasAnyMagnetLocationChanged(oldImgMagnets, newImgMagnets, 50)


def findMagnets(_img, hi):
	img = hi.PrepareSourceImage(_img)
	magnetsAll = hi.GetMagnets(img, False)
	magnetsBorder = hi.GetMostSmallerAndMostBiggerDots(magnetsAll)
	whiteBoard = hi.CutTheBoard(img, magnetsBorder)
	return hi.GetMagnets(whiteBoard, True)

def find2(_img, hi):
    img = hi.PrepareSourceImage(_img)
    return hi.GetMagnets(img, False)








