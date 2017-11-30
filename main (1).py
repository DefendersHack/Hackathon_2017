#!/usr/bin/python

"""Google Drive Quickstart in Python.

This script uploads and shares a single file to Google Drive.

https://github.com/googledrive/python-quickstart
"""
import time,datetime

import pprint

import httplib2
import apiclient.discovery
import apiclient.http
import oauth2client.client

import subprocess,os,requests

# OAuth 2.0 scope that will be authorized.
# Check https://developers.google.com/drive/scopes for all available scopes.
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Location of the client secrets.
CLIENT_SECRETS = 'client_secrets.json'

# Path to the file to upload.
FILENAME = 'whiteboard.jpg'

# Metadata about the file.
MIMETYPE = 'image/jpg'
TITLE = 'Workday Logo'
DESCRIPTION = 'Workday Logo'

# Perform OAuth2.0 authorization flow.
flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
authorize_url = flow.step1_get_authorize_url()
print 'Go to the following link in your browser: ' + authorize_url
code = raw_input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)

# Create an authorized Drive API client.
http = httplib2.Http()
credentials.authorize(http)
drive_service = apiclient.discovery.build('drive', 'v2', http=http)

while True:
	# print subprocess.check_output(['raspistill','-o','whiteboard.jpg']) 
	FILENAME='whiteboard_'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')+'.jpg'
	os.system('raspistill -o '+FILENAME)

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
	new_file = drive_service.files().insert(body=body, media_body=media_body).execute()


	# The body contains new permission for the file
	new_permission = {
	      'value': 'default',
	      'type': 'anyone',
	      'role': 'reader'
	  }

	drive_service.permissions().insert(
	        fileId=new_file.get('id'), body=new_permission).execute()
	# pprint.pprint(new_file)

	print "Shared link is: ", new_file.get('webContentLink')

	json = "{'text': 'The White Board was updated!','attachments': [{'title': 'Defenders of the Earth White Board','author_name': 'Defenders of the Earth','image_url':'"+ new_file.get('webContentLink')+"'},{'color': '#0000FF','attachment_type': 'default'}]}"


	r = requests.post('https://hooks.slack.com/services/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', json)

	time.sleep(60)
