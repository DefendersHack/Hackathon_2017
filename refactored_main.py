#!/usr/bin/python

"""Google Drive Quickstart in Python.
This script uploads and shares a single file to Google Drive.
https://github.com/googledrive/python-quickstart
"""
import time,datetime
import argparse
import imutils
import cv2
import numpy as np
from HandleImage import HandleImage
import httplib2
import apiclient.http
import oauth2client.client
import scipy
from scipy.misc.pilutil import imread
from scipy.linalg import norm
from scipy import sum, average

import os, requests

# OAuth 2.0 scope that will be authorized.
# Check https://developers.google.com/drive/scopes for all available scopes.
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Location of the client secrets.
CLIENT_SECRETS = 'client_secrets.json'

# Metadata about the file.
MIMETYPE = 'image/jpg'
TITLE = 'Workday Logo'
DESCRIPTION = 'Workday Logo'

# The body contains new permission for the file
FILE_PERMISSIONS = {'value': 'default', 'type': 'anyone', 'role': 'reader'}

def oAuth():
    # Perform OAuth2.0 authorization flow.
    flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
    flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
    authorize_url = flow.step1_get_authorize_url()
    print 'Go to the following link in your browser: ' + authorize_url
    code = raw_input('Enter verification code: ').strip()
    return flow.step2_exchange(code)

def triggerCamera():
    FILENAME = 'whiteboard_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'

    os.system('raspistill -o ' + FILENAME)

    return FILENAME

def uploadPicture(FILENAME, drive_service):


    # Insert a file. Files are comprised of contents and metadata.
    # MediaFileUpload abstracts uploading file contents from a file on disk.
    media_body = apiclient.http.MediaFileUpload(
        FILENAME,
        mimetype=MIMETYPE,
        resumable=True
    )
    # The body contains the metadata for the file.
    body = {
        'title': TITLE,
        'description': DESCRIPTION,
        'shared': True
    }

    # Perform the request and print the result.
    temp_file = drive_service.files().insert(body=body, media_body=media_body).execute()

    drive_service.permissions().insert(fileId=temp_file.get('id'), body=FILE_PERMISSIONS).execute()

    print "Shared link is: ", temp_file.get('webContentLink')

    return temp_file

def postPicture(picture):
    json = "{'text': 'The White Board was updated!','attachments': [{'title': 'Defenders of the Earth White Board','author_name': 'Defenders of the Earth','image_url':'" + picture.get('webContentLink') + "'},{'color': '#0000FF','attachment_type': 'default'}]}"

    requests.post('https://hooks.slack.com/services/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', json)

def isChanged2(oldImg, newImg):
    hi = HandleImage()
    oldImgMagnets = find2(oldImg, hi)
    newImgMagnets = find2(newImg, hi)
    return hi.hasAnyMagnetLocationChanged(oldImgMagnets, newImgMagnets, 50)


def find2(_img, hi):
    img = hi.PrepareSourceImage(_img)
    return hi.GetMagnets(img, False)


def isChanged(file1, file2):
    hi = HandleImage()
    # read images as 2D arrays (convert to grayscale for simplicity)
    img1 = hi.PrepareSourceImage(file1)
    img1a = to_grayscale(img1.astype(float))

    img2 = hi.PrepareSourceImage(file2)
    img2a = to_grayscale(img2.astype(float))
    # compare
    n_m, n_0 = compare_images(img1a, img2a)
    print "Manhattan norm:", n_m, "/ per pixel:", n_m/img1.size
    print "Zero norm:", n_0, "/ per pixel:", n_0*1.0/img1.size
    return int(n_m/img1.size) > 40

def compare_images(img1, img2):
    # normalize to compensate for exposure difference, this may be unnecessary
    # consider disabling it
    img1 = normalize(img1)
    img2 = normalize(img2)
    # calculate the difference and its norms
    diff = img1 - img2  # elementwise for scipy arrays
    print diff
    m_norm = sum(abs(diff))  # Manhattan norm
    z_norm = norm(diff.ravel(), 0)  # Zero norm
    return (m_norm, z_norm)

def to_grayscale(arr):
    "If arr is a color image (3D array), convert it to grayscale (2D array)."
    if len(arr.shape) == 3:
        return average(arr, -1)  # average over the last axis (color channels)
    else:
        return arr

def normalize(arr):
    rng = arr.max()-arr.min()
    amin = arr.min()
    return (arr-amin)*255/rng

def main():
    credentials = oAuth()

    # Create an authorized Drive API client.
    http = httplib2.Http()
    credentials.authorize(http)
    drive_service = apiclient.discovery.build('drive', 'v2', http=http)
    last_uploaded_file = ''
    while True:

        new_file = triggerCamera()
        image_file = cv2.imread(new_file)
        if last_uploaded_file == '' or isChanged(last_uploaded_file, new_file):
            new_file = uploadPicture(new_file, drive_service)
            last_uploaded_file = image_file
            postPicture(new_file)

    
        time.sleep(60)
        
if __name__ == '__main__':
    main()