import runpy

answer = input("Get data?[y/n]\n")
if answer == "y":
    runpy.run_path(path_name='getYoutubeMusicData.py')
answer = input("Manage Playlists?[y/n]\n")
if answer == "y":
    runpy.run_path(path_name='playlistManager.py')
answer = input("Update Data?[y/n]\n")
if answer == "y":
    runpy.run_path(path_name='updateYoutubeMusicData.py')
