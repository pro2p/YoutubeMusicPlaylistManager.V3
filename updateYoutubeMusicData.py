from googleapiclient.discovery import build
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time

credentials = None

#get oauth credentials
if os.path.exists("data_and_stuff/token.pickle"):
    print("Loading Credentials From File...")
    with open("data_and_stuff/token.pickle", "rb") as token:
        credentials = pickle.load(token)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print("Refreshing Access Token...")
        credentials.refresh(Request())
    else:
        print("Fetching New Tokens...")
        flow = InstalledAppFlow.from_client_secrets_file('data_and_stuff/client_secrets.json',scopes = ["https://www.googleapis.com/auth/youtube"])
        flow.run_local_server(port=8080, prompt="consent", authorization_prompt_message="")
        credentials = flow.credentials

        with open("data_and_stuff/token.pickle","wb") as f:
            print("Saving Credentials for Future Use...")
            pickle.dump(credentials, f)

#create service
youtubeService = build('youtube','v3',credentials=credentials)


def get_actions():
    with open("data_and_stuff/listActions.txt", mode='r') as f:
        actions = []
        for line in f.readlines():
            this_action = line.strip().split("|")
            actions.append(this_action)
    return actions

def update_playlists():
    actions = get_actions()
    i = 0
    if actions != []:    
        adding_playlists={}#Not always necessary
        for action in actions:
            added_playlists = False
            i+=1
            print(f'Executing Action n°{i}')
            if action[0] == "dm":
                request = youtubeService.playlistItems().delete(
                    id = action[1]
                )
            elif action[0] == "mm":
                request = youtubeService.playlistItems().update(
                    part=["snippet","id"],
                    body = {
                        "id": action[1],
                        "snippet":{
                            "playlistId": action[4],
                            "resourceId":{
                                "playlistId":action[4],
                                "kind": "youtube#video",
                                "videoId": action[2]
                            },
                            "position":action[3]
                        }
                    }
                )
            elif action[0] == "im":
                request = youtubeService.playlistItems().insert(
                    part=["snippet","id"],
                    body = {
                        "id": action[1],
                        "snippet":{
                            "playlistId": action[4],
                            "resourceId":{
                                "playlistId":action[4],
                                "kind": "youtube#video",
                                "videoId": action[2]
                            },
                            "position":action[3]
                        }
                    }
                )
            elif action[0] == "dp":
                request = youtubeService.playlists().delete(
                    id = action[1]
                )
            elif action[0] == "ap":
                added_playlists = True
                request = youtubeService.playlists().insert(
                    part = ["snippet"],
                    body = {
                        "snippet":{
                            "title":action[1]
                        }
                    }
                )
            elif action[0] == "am":
                request = youtubeService.playlistItems().insert(
                    part=["snippet","id"],
                    body = {
                        "id": action[1],
                        "snippet":{
                            "playlistId": adding_playlists[action[3]],
                            "resourceId":{
                                "playlistId":adding_playlists[action[3]],
                                "kind": "youtube#video",
                                "videoId": action[2]
                            }
                        }
                    }
                )
            request.execute()
            if added_playlists:
                print("Waiting for creation of playlist on the servers")
                time.sleep(3)
                request = youtubeService.playlists().list(part=["snippet","id"],mine = True,maxResults = 50)
                response = request.execute()
                for playlist in response["items"]:
                    if playlist["snippet"]["title"] == action[1]:
                        adding_playlists[action[2]]=playlist["id"]
                        print("Updating ids in configs...")
                        for j in range(1,16):
                            #ctrl+c ctrl+v  ;)
                            if os.path.exists(f"configs/{str(j)*3}.txt"):
                                with open(f"configs/{str(j)*3}.txt",mode="r",encoding='utf-8') as f, open(f"configs/{str(j)*3}.txt.tmp", mode="w",encoding='utf-8') as g:
                                    for line in f:
                                        for key in adding_playlists:
                                            line = line.replace(key,adding_playlists[key])
                                        g.write(line)
                                os.remove(f"configs/{str(j)*3}.txt")
                                os.rename(f"configs/{str(j)*3}.txt.tmp",f"configs/{str(j)*3}.txt")
                        break


update_playlists()
youtubeService.close()
