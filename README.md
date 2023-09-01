# YoutubeMusicPlaylistManager.V3

I created this project because of the disappointment I felt when realising that there was no way to easily sort my music playlists on youtube.
I was pretty surprised because Youtube is a big company, and that kind of service and functionalities are so basic that it is weird that they were not implemented.
I therefore decided to create this service myself, at first for my own use, then I decided to publish it here on Github as I'm pretty sure that I'm not the only who felt those needs.

I think my project works fine and hope it will also for you. However I cannot affirm that it is bug-free or issue-free, nor that is is optimised. Therefore, if any bug arises, please tell me in the comments section. However, as I am just entering a preparatory class this september, I do not think that I will be able to make any major changes to this project during the two following years. But I can still tweak some code if necessary in order to solve bugs, if they are thoroughly described in the comments section and that I can solve them rapidly. If you have some improvement ideas or some fancy features that you wish me to add, do tell me in the commments section as well.
________________________________________________________________________________________________________________________________________________________________________________________________________

The code allows you to:

-sort a playlist alphabetically

-sort a playlist by date added

-sort a playlist by music duration

-shuffle a playlist randomly

-determine your playlists' total duration

-list the artists in your playlists, counting the number of songs you have saved for each of them

-search an artist, in order to know wether you have any of this artist's songs in your playlists

-create, read and modify a wishlist

-save configs of your playlists, that you can load later on

-sort only specific parts of your playlist

and more...
(there are various ways to sort alphabetically, etc... For more info, read the documentation below)

________________________________________________________________________________________________________________________________________________________________________________________________________
How the project globally works:

-the main.py file uses the runpy module to run the three other files, getYoutubeMusicData.py, playlistManager.py and updateYoutubeMusicData.py. Before running any of these files and the code inside of them, you will be asked wether you wish to run them or not. Between each of these files, which are executed successively, the necessary data to run the following file is stored inside text files inside the "data_and_stuff" folder.

-the getYoutubeMusicData.py file fetches all your playlists' data. To do this, Oauth2 credentials are required. To get your own key and credentials, read the "How to use the project" section. Fetching your data can be a bit long depending on the number of playlists and the number of musics inside of them. You can accelerate this process by going into the code and removing the requests for the musics' duration if you wish not to use the related functionalities (twice faster);

-the getYoutubeMusicData.py file then stores your data into two text files, MyData.txt and MyDataUpdated.txt. Therefore, when the code stops running, your data is still stored somewhere and you can access it the next time you run the code, avoiding therefore to fetch all your data again (if it has not been modified). The MyData.txt file allows you to see your playlists as they are, without any change made. The MyDataUpdated.txt file is where your updated data is stored. Each time you sort your data or modify it, the file will be updated with your changes, allowing you to see what your final playlists will look like once you're done managing playlists;

-the playlistManager.py file is the main file of the project. It loads the data stored into the myData.txt file and then will offer you different actions that can be made on your data until your done. Those actions are described in details in the documentation below. Once you're done, it defines the necessary actions to make your old data become as in the myDataUpdated.txt file and stores them in the listActions.txt file in the "data_and_stuff" folder;

-the updateYoutubeMusicData.py file loads the data stored into the listActions.txt file and executes each action, making API requests to the youtube servers and effectively updating your playlists on youtube. To do this, Oauth2 credentials are also required. To get your own key and credentials, read the "How to use the project" section.
________________________________________________________________________________________________________________________________________________________________________________________________________
How to use the project -- in 10 very simple steps for noobs (like me)(setup time: at the most 10min):

1. Download the project and open it in your IDE.
2. Create a project on the google developer console https://console.cloud.google.com/
3. Add the "YouTube Data API v3" to your project
4.Go to "APIs and Services" menu, then "Credentials" submenu and click on "create credentials", then "OAuth Client ID".
5. Select "Web Application", name it how you like, click on "add URI" under "Authorised redirect URIs" and paste "http://localhost:8080/" (I used port 8080 following a tutorial, using another port will require modifying a tiny bit of code in the getYoutubeMusicData.py and updateYoutubeMusicData.py files), click on "create", your OAuth Client ID is created!
6. Click on the "download json" button to download your OAuth Client ID as a json file
7. Rename the file "client_secrets" and move it inside the "data_and_stuff" folder in the project
8. Install the required packages that I wrote in the requirements.txt file using pip or elseway if they are not already installed ("pip install google-api-python-client","pip install google_auth_oauthlib","pip install aniso8601" in the terminal)
9. Launch the project by running the main.py file ("python main.py" command in the terminal)
10. When asked to select a google account, select your account (with your playlists), click on "advanced",then "Go to [the_name_you_gave_to_the_project]", and finally "Continue".
You can then come back to your IDE and the project's running.

Note: Youtube API limits requests with quotas, 10 000/day. I optimised the requests to their maximum (at least I think so) but it might happen that you run out of quotas. The program will throw an error in the console, you just have to wait the next day (which, I admit, is a bit annoying).
________________________________________________________________________________________________________________________________________________________________________________________________________
Documentation:
The documentation will reproduce the text-based menu and explain briefly each command.

///|\\\

"Get Data[y/n]"

y -> runs getYoutubeMusicData.py file

n -> asks if you want to run the playlistManager.py file

one iteration = 50 musics fetched

basic request does not return music duration, that's why it is necessary to make a second request (doubling the total number of requests)

///|\\\

"Manage Playlists[y/n]"

y -> runs playlistManager.py file

n -> asks if you want to run the updateYoutubeMusicData.py file

	
	"You have [x] playlists on you account:
	 (1): First playlist
	 (2): Second playlist
	 ...
	 (x): x th playlist
	 (999): multiplaylist
	 Which playlist do you want to manage? (type in number of playlist)"
	number -> manage the [number]th playlist
		
		"(1)Sort alphabetically
 		 (2)Sort by artist by grouping (biggest group)
  		 (3)List Artists
		 (4)Sort by original order (creation of playlist order)
		 (5)Random shuffle
		 (6)Playlist duration
		 (7)Sort by duration"
		1 -> sort alphabetically

			"What do you want to sort alphabetically?
			 (1)All musics
			 (2)Artists
			 (3)Musics of artists
			 (4)Artists, then musics of artists
			 (5)[Reverse]All musics
			 (6)[Reverse]Artists
			 (7)[Reverse]Musics of artists
			 (8)[Reverse]Artists, then musics of artists"
			1 -> sorts all musics of the chosen playlist alphabetically, from A to Z
			2 -> sorts all artists of the chosen playlist alphabetically, from A to Z, groups all musics of the same artist together and sorts those groups alphabetically based on the   
                             artist's name 
			3 -> for each artist, sorts the artist's songs alphabetically, from A to Z, without moving the positions of the artist's songs in the playlist
			     for example, if you put all the songs sung by Rihanna at the top of your playlist and just next all the songs of Elvis Presley, The songs of Rihanna will be sorted
                             alphabetically, and those of the king Elvis Presley as well, but all the Rihanna songs will stay at the top, and Elvis' songs underneath. Your musics do not have to be
                             already grouped by artist, works with any playlist configuration
			4 -> same as if you used (2) and then (3)
			[Reverse] -> from Z to A instead of A to Z
		
		2 -> groups all musics of the same artists together, all the musics basically stick themselves to the biggest group of musics following themselves sung by the same artist
		
		3 -> list artists inside this particular playlist, counting the number of musics you have added to your playlist for each artist

		4 -> sort musics based on their date added to the playlist
		
			"How do you want your playlist back?
			 (1)Ascending Order (most recently added musics at the bottom of the playlist)
			 (2)Descending Order (most recently added musics at the top of the playlist)
			 (3)Artist order ascending (first artist added to playlist at the top)
			 (4)Artist order descending (first artist added to playlist at the bottom)"
			1 -> places the musics you have most recently added to your playlist at the bottom and the oldest ones at the top (default YoutubeMusic and Youtube behaviour)
			2 -> same as (1) but the other way around
			3 -> sorts the artists in your playlist based on the oldest date added of their musics. Example : if you first added a music of Rihanne to your playlist, then a few musics of
                             Elvis Presley, and then some other musics sung by Rihanna, all Rihanna's musics will be at the top, because the first music of Rihanna added to your playlist was added
                             before any music of Elvis Presley
			4 -> same as (3) but the other way around

		5 -> sorts your playlist randomly (pretty useful because the "random play" offered by Youtube is not very random...(especially with huge playlists) However, using this still uses a
                     bunch of quotas, do not use it every time you want to hear music following a "shuffle play" logic

		6 -> determines the total duration of your playlist, summing all the durations of the musics inside the playlist

		7 -> sorts the musics by playlist duration (did not code as much options as for the alphabetic sort, as it might never be used!, or used only for curiosity matters)

			"How do you want your playlist sorted?
			 (1)Ascending (shortest musics at the start)
			 (2)Descending (Longest musics at the start)"
			1 -> seems pretty clear to me
			2 -> same (writing this documentation is really long, I'm starting to get bored)

	999 -> functionalities that apply to multiple playlists, or no playlist in particular

		"You have decided to work on multiple playlists.
		 What do you want to do with multiple playlists?
		 (1)Define exceptions
		 (2)List artists
		 (3)Search Artist
		 (4)Wish List
		 (5)Configs of playlists"
		1 -> some artists have different channels and it occurs pretty often that an artist has a channel named [artist_name] and another one named [artist_name]VEVO. This is solved by an
                     uniformisation made at the beginning of the execution of the playlistManager.py file as it arises often. However, some exceptions might escape this uniformisation process, you
                     can in this case define manually the exception, that will be stored in a text file. 
		     Other use: if you wish to sort several artists under the same label, you can define an exception so that these artists' names become the label.
		     Example: I defined an exception to change the artist name "Valerie Broussard" to "League of Legends" for the music "Awaken" in order to group together all the musics based on the
                     videogame League of Legends
		     You can define exceptions manually in the exceptions.txt file in the "data_and_stuff" folder, using the correct syntax
			
			"Type in artist name you want to modify and new artist name in the following way:
			 actual_artist_name|new_artist_name"
			->just do as I wrote ;)
   
		2 -> lists all the artists in your playlists with the corresponding number of songs for each playlist
			
			"How do you want to list artists?
			 (1) default order (in order of playlist)
			 (2) ascending order (from artist with the fewest songs to artist with the most songs)
			 (3) descending order (from artists with the most songs to artist with the fewest songs)"
			1 -> lists the artists in the order in which they are placed in you playlists (runs through playlist (1) and if encounters a new artist, searches for all his songs, then
                             continue and runs through all the playlists to make sure no artist is forgotten)
			2 -> prints first the artists with the fewest songs saved across your playlists down to those with the most songs. As the artists printed first will appear at the top of your
                             console, you will have to scroll a lot to find them, therefore if you really want to know which artist has the most songs across your playlists, it is of better use to
                             chose the option (2) rather than the option (3)
			3 -> same as (2) but the other way around

		3 -> searches for an artist across your playlist and returns the best possible results, followed by the number of musics of these artists/results inside each of your playlist
		     note: checks for exact same name lowercase, but also for names containing the one you typed and names contained inside the one you type
		     example: searched "SCH" in my playlists (very nice artist btw), found 'SCH' but also 'Robin Schulz' because 'sch' is in 'schulz'...

			"Which artist do you want to search?"
			-> type in the name of the artist
		
		4 -> allows you to write into a wish list (the names of the songs you want to add to your playlists or artists you want to listen to, etc...), read it and delete lines

			"What do you want to do with your wish list?
			 (1)Add element
			 (2)Get first element (added first)
			 (3)Get last element (added last)"
			1 -> writes a line at the end of you wish list, then asks you if you want to write another line or stop
			2 -> gets first line of the wish list, can then read the next line, delete the line, or stop modifying the wish list
			3 -> gets last line of the wish list, can the read the previous line, delete the line, or stop modifying the wish list

		5 -> allows you to save, load or delete configs. I set arbitrarily a limit of 15 playlists. It can be changed but a lot of tiny details in the code might need to be changed as well.
                     You can name your configs using alphanumeric characters. The configs are saved in the "configs" folder. A config is basically a copy of the myDataUpdated.txt file or a part of
                     this file, depending wether you want to save a config for all your playlists or just a config of one playlist. Loading a config may lead to musics being deleted, others being
                     added, playlists being deleted and playlists being added.

			"You have 0 saved configs.
			 Managing configs of playlists:
			 (1)Save config
			 (2)Load config
			 (3)Delete config"
			-> these text menu options and the following ones are pretty clear, you should understand
        ________________________________________________________________________________________________________________________________________________________________________________________________
        Each time you select an option to sort a playlist, the following output will be printed in the console:

	        "Do you want to sort your entire playlist that way or only a specific part?
	         Answers:
	         entire playlist -> [e]
	         specific area -> [s]"

        Most of the times, you will just type in the answer 'e', but in some cases you might want to select a specific area. For example, you might want to sort alphabetically only the 20 first
        musics of you playlist or the musics from position 34 to position 75 (these positions are written down next to the songs in the myDataUpdated.txt file),etc...
        if you type in "s", the following will be printed:

	        "Give a specific area. (playlist begins at position 0)
	         Last position in playlist: 58
	         Format answers:
	         from position [x] included to position [y] included -> [x]-[y]
	         one number [z] -> [z]
	         from position [x] included to end -> [x]-
	         from start to position [y] included -> -[y]
	         separate multiple inputs with commas
	         !no spaces!"

        which is basically instructions to select the area. Works the same as when you need to select an area of a document that you want to print (in real life ;) ) instead of the whole document. I
        coded this system from scratch, might not always work, especially if your goal is to break the code! There might have been a library or package now that I'm thinking about it, would have
        saved me some efforts...

///|\\\

"Update Data?[y/n]"

y -> updates your playlists on your google account so that they look exactly like in the myDataUpdated.txt file

n -> stops the program

ps: length of the longest increasing subsequence is equal to the total number of actions (if you don't mess things up with configs), just a matter of optimisation.
________________________________________________________________________________________________________________________________________________________________________________________________________
THE END:

really hope it helps, a nice comment is always welcome in the comments section if this project has been useful to you, it did take me dozens of hours :D
