# -*- encoding: UTF-8 -*-
# pip install --upgrade google-api-python-client
import os
import httplib2
from pprint import pprint
from oauth2client.file import Storage
from apiclient.discovery import build
from apiclient import errors
from apiclient import http as api_http
from oauth2client.client import OAuth2WebServerFlow
import ast
import collections

# make OUT_PATH where we will save the dataset
OUT_PATH = ''
if not os.path.exists(OUT_PATH):
    os.makedirs(OUT_PATH)

# Copy your credentials from the console
# https://console.developers.google.com
CLIENT_ID = '1031915833238-qelsipmsj1besb2cfbpukcvmepa9i0l5.apps.googleusercontent.com'
CLIENT_SECRET = 'ELWoWLoKn5wdhHIdoRVL79hK'

OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CREDS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
storage = Storage(CREDS_FILE)
credentials = storage.get()

if credentials is None:
    # Run through the OAuth flow and retrieve credentials
    flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    code = input('Enter verification code: ').strip()
    # print(code)
    # code = ast.literal_eval(code)
    # code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)

# Create an httplib2.Http object and authorize it with our credentials
http = httplib2.Http()
http = credentials.authorize(http)
drive_service = build('drive', 'v2', http=http)


def list_files(service):
    page_token = None
    while True:
        param = {}
        if page_token:
            param['pageToken'] = page_token
        files = service.files().list(**param).execute()
        for item in files['items']:
            yield item
        page_token = files.get('nextPageToken')
        if not page_token:
            break


DATA = {'train_split.6.tar.gz': 'train',
        'train_split.10.tar.gz': 'val',
        'train_split.12.tar.gz': 'test'}

for item in list_files(drive_service):
    print(item.get('title'))
    if item.get('title') in list(DATA.keys()):
        title = item['title']
        outfile = os.path.join(OUT_PATH, DATA[title], title)
        download_url = item['downloadUrl']
        print(download_url)
        print(outfile)
        if download_url:
            resp, content = drive_service._http.request(download_url)
            print("downloading %s" % item.get('title'))
            if resp.status == 200:
                if os.path.isfile(outfile):
                    print("ERROR, %s already exist" % outfile)
                else:
                    with open(outfile, 'wb') as f:
                        f.write(content)
                    print("OK")
            else:
                print('ERROR downloading %s' % item.get('title'))
