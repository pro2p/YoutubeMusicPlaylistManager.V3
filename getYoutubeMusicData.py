from googleapiclient.discovery import build
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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

#test for third request, list all musics in a playlist
def fetch_musics(playlist_id, music_count, playlist_name):
    print(f"Fetching musics from playlist : {playlist_name}")
    musics=[]
    iteration=0
    while len(musics)< music_count:#count
        iteration+=1
        print(f"Iteration n°{iteration}")
        if len(musics)==0:
            request = youtubeService.playlistItems().list(
                part=["snippet","id"],
                playlistId= playlist_id,
                maxResults= 50
            )        
        else:
            request = youtubeService.playlistItems().list(
                part=["snippet","id"],
                playlistId=playlist_id,
                maxResults=50,
                pageToken = nextPageToken
            )
        response = request.execute()
        try:
            nextPageToken = response["nextPageToken"]
        except:
            print("Run through all the musics")
        #time request
        times = {}
        id_list = [music["snippet"]["resourceId"]["videoId"] for music in response["items"]]
        request2 = youtubeService.videos().list(part = ["contentDetails","id"],id = id_list) 
        response2 = request2.execute()
        for item in response2["items"]:
            times[item["id"]]=item["contentDetails"]["duration"]
        #other caracteristics already in base response
        for music in response["items"]:
            music_name = music["snippet"]["title"].strip(" \n")
            music_artist = music["snippet"]["videoOwnerChannelTitle"].strip(" \n")
            music_number = music["snippet"]["position"]
            music_id = music["snippet"]["resourceId"]["videoId"]
            music_id_long = music["id"]
            music_date_added_to_playlist = music["snippet"]["publishedAt"]
            music_time = times[music_id]
            music_date =''
            musics.append((music_number,music_artist,music_name,music_time,music_date, music_id,music_id_long, music_date_added_to_playlist))
    return musics
        

#list playlist name, music count and all musics part of that playlist (name, artist, date)
#first, fetch my playlists, their data and more importantly their id
#then for each id, search for all the musics and add them to the list of musics in the dictionary
def list_playlistMusics():
    request = youtubeService.playlists().list(
        part=["contentDetails","snippet"],
        mine = True,
        maxResults = 50
    )
    response = request.execute()

    list_playlistMusics = []
    for playlist in response["items"]:
        playlist_name = playlist["snippet"]["localized"]["title"]
        playlist_count = playlist["contentDetails"]["itemCount"]
        playlist_id = playlist["id"]
        list_playlistMusics.append({
            '_name':playlist_name,
            'count':playlist_count,
            'id': playlist_id,
            'musics':fetch_musics(playlist_id,playlist_count,playlist_name)
        })
    return list_playlistMusics

myData = list_playlistMusics()
youtubeService.close()

#print the data in a great way in the console
def beautiful_print(list_of_playlist_musics):
    for dictionary in list_of_playlist_musics:
        for key in dictionary:
            if type(dictionary[key])==list:
                print(f"{key} :")
                for line in dictionary[key]:
                    print(line)
            else:
                print(f"{key} : {dictionary[key]}")    
        print("\n\n")    
    print("Fetched all musics from playlists.")


#same as beautiful_print but for writing the data into a file
def beautiful_write(list_of_playlist_musics, file, numbers_for_musics=False):
    for dictionary in list_of_playlist_musics:
        for key in dictionary:
            if type(dictionary[key])==list:                
                file.write(f"{key} :")
                file.write("\n")
                for i in range(len(dictionary[key])):
                    if numbers_for_musics:
                        file.write(f'{i}: ')
                    file.write(str(dictionary[key][i]))
                    file.write("\n")
            else:
                file.write(f"{key} : {dictionary[key]}")
                file.write("\n")    
        file.write("\n\n")    
    file.write("Fetched all musics from playlists.")

#writes all the data into a file
with open("data_and_stuff/myData.txt","w",encoding='utf-8') as f:
    beautiful_write(myData, f)
#also writes the data into myDataUpdated.txt file so that is the only file the user needs to see
with open("data_and_stuff/myDataUpdated.txt","w",encoding='utf-8') as f:
    beautiful_write(myData,f, numbers_for_musics=True)