'''
Created on May 20, 2018

@author: hlv_trinh
'''



from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.http import MediaFileUpload
import resource

ROOT_BACKUP_FOLDER = "server-backup"
MAX_RETRY = 10
CHUNK_SIZE = 5 * 1024 * 1024 #5MB

MAX_MEMORY = 256 * 1024 * 1024

soft, hard = resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS, (MAX_MEMORY, hard))
print("Current limit: %s, %s | New: %s" %(soft, hard, MAX_MEMORY))

def FindAndCreateIfNotExist(service, parentFolderId, folderName):
    if parentFolderId == None:
        query = ("name='%s'" % folderName)
    else:
        query = ("name='%s' and '%s' in parents" % (folderName, parentFolderId))
    
    response = service.files().list(
        q=query, 
        spaces='drive', 
        fields='nextPageToken, files(id, name)', 
        pageToken=None).execute()
    backupDir = response.get('files', [])
    if len(backupDir) > 0:
        backupFile = backupDir[0]
    else:
        print ("Not found root folder, trying to create: %s" % folderName)
        if parentFolderId == None:
            body = {'name':folderName, 
                    'mimeType':'application/vnd.google-apps.folder'}
        else:
            body = {'name':folderName, 
                    'mimeType':'application/vnd.google-apps.folder',
                    'parents': [parentFolderId]}
        backupFile = service.files().create(
            body=body, 
            fields='id, name').execute()
    if (backupFile.get('id') != ''):
        print ('Backup Root Folder: %s (%s)' % (backupFile.get('name'), backupFile.get('id')))
    
    return backupFile

def uploadBackupFile(service, parentFolderId, filePath):
    print(filePath)
    import os.path
    fileSize = os.path.getsize(filePath)
    if fileSize <= CHUNK_SIZE:
        media_body = MediaFileUpload(filePath, mimetype='application/octet-stream', resumable=True)
    else:
        media_body = MediaFileUpload(filePath, mimetype='application/octet-stream', chunksize=CHUNK_SIZE, resumable=True)
    fileName = os.path.basename(filePath)
    body = {
        'name': fileName,
        'description': fileName,
        'mimeType': 'application/octet-stream',
        'parents': [parentFolderId]
    }
    
    retries = 0
    request = service.files().create(body=body, media_body=media_body)
    response = None
    from apiclient import errors
    success = True
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                print ("Uploaded %.2f%%" % (status.progress() * 100))
                retries = 0
        except errors.HttpError, e:
                if e.resp.status == 404:
                    print("Error 404! Aborting.")
                    success = False
                    break
                else:   
                    if retries > MAX_RETRY:
                        print ("Retries limit exceeded! Aborting.")
                        success = False
                        break
                    else:   
                        retries += 1
                        import time
                        time.sleep(2**retries)
                        print ("Error (%d)... retrying." % e.resp.status)
                        continue
    if success:
        print ("Upload Complete!")
        os.remove(filePath)

def main():
    """
    Shows basic usage of the Drive v3 API.
    
    Creates a Drive v3 API service and prints the names and ids of the last 10 files
    the user has access to.
    """
    
    import sys
    if len(sys.argv) < 1:
        print('Invalid input folder')
        exit(1)
    
    # Setup the Drive v3 API
    SCOPES = 'https://www.googleapis.com/auth/drive.file'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    
    # Find the backup root folder or else, create it
    backupFile = FindAndCreateIfNotExist(service, None, ROOT_BACKUP_FOLDER)
    
    import socket
    hostname = socket.gethostname()
    if hostname.strip() == "":
        hostname = "Unknown"
        
    backupFile = FindAndCreateIfNotExist(service, backupFile.get('id'), hostname)
    
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")
    backupFile = FindAndCreateIfNotExist(service, backupFile.get('id'), timestr)
    
    parentFolderId = backupFile.get('id')
    filePath = sys.argv[1]
    
    import os
    if os.path.isfile(filePath):
        uploadBackupFile(service, parentFolderId, filePath)
    else:
        for f in os.listdir(filePath):
            uploadBackupFile(service, parentFolderId, os.path.join(filePath,f))
    
    service.close()
    
if __name__ == '__main__':
    main()
