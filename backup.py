import os
import argparse
import datetime
import json
import requests
import app_constants as APP_CONSTANTS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

parser = argparse.ArgumentParser(
    description='Backup Slack channel, conversation, Users, and direct messages.')

parser.add_argument('-t', '--token', dest='token',required=True,
                    help='Slack api Access token')

parser.add_argument('-od', '--outDir', dest='outDir',required=False,default='./output',
                    help='Output directory to store JSON backup files.')

args = parser.parse_args()

token = args.token
auth_headers = {'Authorization': 'Bearer ' + token}
outDir = args.outDir

client = WebClient(token=token)

def getOutputPath(relativePath):
    return outDir+relativePath


def parseTemplatedFileName(template, *args):
    return template.format(*args)


def readPostManCollectionJson():
    with open('slack-postman.json') as file:
        jsonObj = json.load(file)
        return jsonObj


def readRequestJsonFile():
    with open('requests.json') as file:
        jsonObj = json.load(file)
        return jsonObj

def makedirPath(outputPath):
    dirPath = os.path.dirname(outputPath)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

def writeJSONFile(jsonObj, filePath):
    outputPath = getOutputPath(filePath)
    makedirPath(outputPath)
    with open(outputPath, 'w+') as file:
        json.dump(jsonObj, file, indent=True)

def getUsers():
    response = client.users_list()
    return response['members']

def lookupUser(users, userID):
    for u in users:
        if u['id'] == userID:
            return u

def getChannels():
    response = client.conversations_list(types='public_channel,private_channel')
    return response['channels']

def getGroups():
    response = client.conversations_list(types='mpim')
    return response['channels']

def getOneToOneConversations():
    response = client.conversations_list(types='im')
    return response['channels']

def getConversationHistory(channelId):
    params = { 'channel': channelId, 'count': 1000}
    msgs = []
    while True:
        response = client.conversations_history(**params)
        msgs.extend(response['messages'])
        if not response['has_more']:
            break

        params['latest'] = msgs[-1]['ts']

    for m in msgs:
        if not ('reply_count' in m and m['reply_count'] > 0):
            continue

        m['replies'] = []
        params = { 'channel': channelId, 'ts': m['ts'] }
        while True:
            response = client.conversations_replies(**params)
            if not response['ok']:
                break

            m['replies'].extend(response['messages'])

            if not response['has_more']:
                break
            params['cursor'] = response['response_metadata']['next_cursor']

    return msgs

def getFileList():
    params = { 'count': 100, 'show_files_hidden_by_limit': True, 'page': 1}
    files = []
    while True:
        response = client.files_list(**params)
        if not response['ok']:
            break

        files.extend(response['files'])

        if response['paging']['pages'] <= params['page']:
            break
        params['page'] += 1

    return files

def downloadFiles(users):
    files = getFileList()
    writeJSONFile(files, APP_CONSTANTS.FILE_LIST_FILE)

    skipped_files=0
    for file in files:
        print(file)
        if file['mode'] == 'hidden_by_limit':
            skipped_files+=1
            continue
        """"
        {'id': 'F05RECURUUW', 'created': 1694209073, 'timestamp': 1694209073, 'name': 'Authenticated PIR works and directions', 'title': 'Authenticated PIR what exists', 'mimetype': 'application/vnd.google-apps.spreadsheet', 'filetype': 'gsheet', 'pretty_type': 'G Suite Spreadsheet', 'user': 'U0572307DJ4', 'user_team': 'TKC0KS3T9', 'editable': False, 'size': 18377, 'mode': 'external', 'is_external': True, 'external_type': 'gdrive', 'is_public': False, 'public_url_shared': False, 'display_as_bot': False, 'username': '', 'url_private': 'https://docs.google.com/spreadsheets/d/1xoVginoTrbkZluIdLkf0-Vkvo-3KIwqvdj6RhYUn9uU/edit?usp=sharing', 'media_display_type': 'unknown', 'thumb_64': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_64.png', 'thumb_80': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_80.png', 'thumb_360': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_360.png', 'thumb_360_w': 254, 'thumb_360_h': 360, 'thumb_480': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_480.png', 'thumb_480_w': 339, 'thumb_480_h': 480, 'thumb_160': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_160.png', 'thumb_720': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_720.png', 'thumb_720_w': 509, 'thumb_720_h': 720, 'thumb_800': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_800.png', 'thumb_800_w': 800, 'thumb_800_h': 1132, 'thumb_960': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_960.png', 'thumb_960_w': 678, 'thumb_960_h': 960, 'thumb_1024': 'https://files.slack.com/files-tmb/TKC0KS3T9-F05RECURUUW-9109fed65c/authenticated_pir_works_and_directions_1024.png', 'thumb_1024_w': 724, 'thumb_1024_h': 1024, 'original_w': 1024, 'original_h': 1449, 'thumb_tiny': 'AwAwACHTo5oooAOaKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD//2Q==', 'permalink': 'https://penndsl.slack.com/files/U0572307DJ4/F05RECURUUW/authenticated_pir_works_and_directions', 'channels': ['C0565PAMDN2'], 'groups': [], 'ims': [], 'comments_count': 0}

        fails to work for google sheets -- just want to retrieve URL instead
        """

        file['date'] = datetime.datetime.fromtimestamp(file['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        file['author'] = lookupUser(users, file['user'])['name']

        if file['filetype'] == 'gsheet': # we can't download the file in this case, just save URL to text file
            filename = APP_CONSTANTS.FILES_FILENAME.format(**file) + '.txt' #add .txt because it doesn't seem gfiles have the extension in the field 'name'
            outputPath = getOutputPath(filename)
            makedirPath(outputPath)
            with open(outputPath, 'wb') as f:
                f.write(str.encode(file['url_private']))

        else:
            filename = APP_CONSTANTS.FILES_FILENAME.format(**file)
            url = file['url_private_download']
            r = requests.get(url, headers={'Authorization': 'Bearer ' + token}, stream=True)
            r.raise_for_status()

            print('Downloading to ' + filename)

            outputPath = getOutputPath(filename)
            makedirPath(outputPath)
            with open(outputPath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=32*1024):
                    f.write(chunk)


    print(f"{skipped_files} files hidden by limit")

def run():
    channels = getChannels()
    writeJSONFile(channels, APP_CONSTANTS.CHANNEL_LIST_FILE)

    for channel in channels:
        print(channel)
        channelId = channel['id']
        channelName = channel['name']
        if channel['is_member']:  # added this if to avoid "not_in_channel" errors
            channelHistory = getConversationHistory(channelId)
            if channel['is_private']:
                template = APP_CONSTANTS.PRIVATE_CHANNEL_HISTORY_FILE
            else:
                template = APP_CONSTANTS.CHANNEL_HISTORY_FILE
            channelHistoryFilename = parseTemplatedFileName(template, channelName)
            writeJSONFile(channelHistory, channelHistoryFilename)
      
            groups = getGroups()
            writeJSONFile(groups, APP_CONSTANTS.GROUP_LIST_FILE)
        else: 
            print(f"skipping channel {channel['name']} -- not a member.")
    
    
    for group in groups:
        groupId = group['id']
        groupName = group['name']

        groupHistory = getConversationHistory(groupId)

        groupHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.GROUP_HISTORY_FILE, groupName)
        writeJSONFile(groupHistory, groupHistoryFilename)

    users = getUsers()
    writeJSONFile(users, APP_CONSTANTS.USER_LIST_FILE)

    userIdToNameDict = {user['id']: user['name'] for user in users}

    # Get one to one conversation list
    oneToOneConversations = getOneToOneConversations()
    writeJSONFile(oneToOneConversations,
                  APP_CONSTANTS.ONE_TO_ONE_CONVERSATION_LIST_FILE)

    for conversation in oneToOneConversations:
        conversationId = conversation['id']
        userId = conversation['user']
        userName = userIdToNameDict[userId]

        conversationHistory = getConversationHistory(conversationId)
        conversationHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.ONE_TO_ONE_CONVERSATION_HISTORY_FILE, userName, userId)
        writeJSONFile(conversationHistory, conversationHistoryFilename)

    downloadFiles(users)

if __name__ == '__main__':
    run()
