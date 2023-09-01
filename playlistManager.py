from ast import literal_eval
import os
import copy
import random
import aniso8601

def get_data(f, config = False):    
    nb_playlists = int(f.read().count("_name"))
    f.seek(0)#allows to read the file again, and dat is nice :)
    if config:
        f.readline()
        f.readline()
    rawData = f.readlines()
    myData = []
    additional_steps = 0
    for i in range(nb_playlists):
        playlist_name = rawData[0+additional_steps][8:].strip()
        playlist_count = int(rawData[1+additional_steps][8:].strip())
        playlist_id = rawData[2+additional_steps][5:].strip()
        playlist_musics = []
        for j in range(playlist_count):
            playlist_musics.append(literal_eval(rawData[4+j+additional_steps].strip()))
        myData.append(
            {
                "_name" : playlist_name,
                "count" : playlist_count,
                "id" : playlist_id,
                "musics" : playlist_musics
            }
        )
        additional_steps += playlist_count+6#six comes from spaces in file and id, count, etc that you need to skip
    return myData

def choose_playlist(theData, worked_on_which_playlists):
    print(f'You have {str(len(theData))}  playlists on your account:')
    for i in range(len(theData)):
        print(f'({str(i+1)}): {theData[i]["_name"]}')
    print("(999): Multiplaylists")
    answer = input("Which playlist do you want to manage? (type in number of playlist)\n")
    try:
        answer = int(answer)
    except:
        raise ValueError("An integer was expected")
    if answer == 999:
        print("You have decided to work on multiple playlists.")
        return None
    if answer==1:
        print("You have decided to work on the first playlist.")
    elif answer ==2:
        print("You have decided to work on the second playlist.")
    elif answer == 3:
        print("You have decided to work on the third playlist.")
    elif answer>3:
        print(f"You have decided to work on the {answer}th playlist.")
    possible_answers = [i+1 for i in range(len(theData))]
    if not answer in possible_answers:
        raise ValueError("The number typed in isn't valid.")
    worked_on_which_playlists[answer-1] = True
    return theData[answer-1]

def sort_artists_then_musics_alphabetically(music_list, reverse=False):
    return sorted(music_list,key=lambda item:(item[1].lower(),item[2].lower()),reverse=reverse)

def sort_artists_alphabetically(music_list, reverse = False):
    return sorted(music_list, key=lambda item:item[1].lower(), reverse=reverse)

def sort_all_musics_alphabetically(music_list, reverse = False):
    return sorted(music_list, key= lambda item:item[2].lower(),reverse=reverse)

def sort_musics_of_artists_alphabetically(music_list, reverse = False):
    new_list_order = [None for i in range(len(music_list))]
    list_artists = list_all_artists(music_list)
    for artist in list_artists:
        #query all the positions (numbers) for the given artist (indexes of their musics in the playlist)
        positions = []
        for count, music in enumerate(music_list):
            if music[1]==artist:
                positions.append(count)
        new_positions = copy.deepcopy(positions)
        new_positions.sort(key=lambda item:music_list[item][2].lower(),reverse=reverse)
        for i in range(len(positions)):
            new_list_order[positions[i]] = new_positions[i]
    sorted_music_list = []
    for element in new_list_order:
        sorted_music_list.append(music_list[element])
    return sorted_music_list

def beautiful_write(theData, file):
    for dictionary in theData:
        for key in dictionary:
            if type(dictionary[key])==list:                
                file.write(f"{key} :")
                file.write("\n")
                for line in dictionary[key]:
                    file.write(str(line))
                    file.write("\n")
            else:
                file.write(f"{key} : {dictionary[key]}")
                file.write("\n")    
        file.write("\n\n")

def sort_grouping(music_list):
    list_artists = list_all_artists(music_list)
    for artist in list_artists:
        print(f"Working on {artist}")
        #query all the positions (numbers) for the given artist (indexes of their musics in the playlist)
        positions = []
        for count, music in enumerate(music_list):
            if music[1]==artist:
                positions.append(count)
        #search for groups of musics from the same artist
        groups = []
        if len(positions)>1:
            first_music_of_the_group = ''
            count = 1
            for position in positions:
                if first_music_of_the_group=='':
                    first_music_of_the_group = position
                    previous_position = position
                    continue
                if position == previous_position+1:
                    count+=1
                else:
                    groups.append((count, first_music_of_the_group))
                    count=1
                    first_music_of_the_group = position
                previous_position = position
                if position == positions[-1]:#last number, there is no number repeating itself, each number can be in the list only once
                    groups.append((count, first_music_of_the_group))
        else:
            continue
        #if only one group, all musics of the given artist are following each others in the playlist
        if len(groups) == 1:
            continue
        #if multiple groups, for each group that is not the biggest group, take the musics and move them to the biggest group
        else:
            groups.sort(reverse=True,key=lambda item:(item[0],-item[1]))#sort by count in descending order and if same count by position in the playlist in ascending order
            main_group = groups[0]#biggest group
            groups.sort(reverse=False,key=lambda item:item[1])
            #first, groups after the biggest group, from first to last, remove the first music of the group, then second, etc each time adding it at the end of the biggest group
            #second, groups before the biggest group,from last to first, remove last music to first of each group, each time adding it to the biggest group
            #in this second phase, each time a music is removed, the biggest group moves one place up, need to keep track of this movement to move the musics to the right place
            main_group_index = groups.index(main_group)
            if main_group_index >0:
                groups_before = True
            else: 
                groups_before = False
            if main_group_index+1==len(groups):
                groups_after = False
            else:
                groups_after = True

            #FIRST
            if groups_after:
                for i in range(main_group_index+1,len(groups),1):
                    working_on_group = groups[i]
                    #through all the musics of each group
                    for j in range(working_on_group[0]):
                        working_on_music = music_list[working_on_group[1]+j]
                        music_list.remove(working_on_music)
                        music_list.insert(main_group[1]+main_group[0],working_on_music)
                        main_group = (main_group[0]+1, main_group[1])

            #SECOND
            if groups_before:
                nb_musics_removed = 0
                #through all the groups before biggest group
                for i in range(main_group_index-1,-1,-1):
                    working_on_group = groups[i]
                    #through all the musics of each group
                    for j in range(working_on_group[0]):
                        working_on_music = music_list[working_on_group[1]+working_on_group[0]-1-j]
                        music_list.remove(working_on_music)
                        nb_musics_removed +=1
                        music_list.insert(main_group[1]-nb_musics_removed,working_on_music)
    return music_list

def define_exceptions(artist_name,artist_new_name):
    if os.path.exists("data_and_stuff/exceptions.txt"):
        first_opening = False
    else:
        first_opening = True
    with open("data_and_stuff/exceptions.txt", encoding='utf-8',mode="a") as f:
        if not first_opening:
            f.write('\n')
        f.write(f"{artist_name}|{artist_new_name}")

def load_exceptions(theData):
    if not os.path.exists("data_and_stuff/exceptions.txt"):
        return
    with open("data_and_stuff/exceptions.txt", encoding='utf-8', mode='r') as f:
        exceptions_raw = f.readlines()
        exceptions = {}
        for line in exceptions_raw:
            this_exception = line.strip().split("|")
            exceptions[this_exception[0]] = this_exception[1]
    for playlist in theData:
        for i in range(len(playlist["musics"])):
            music = playlist["musics"][i]
            if music[1] in exceptions :
                playlist["musics"][i] = tuple([music[i] if i!=1 else exceptions[music[1]] for i in range(len(music))])

def uniformisation(theData):
    load_exceptions(theData=theData)
    uniformisation_param = ["VEVO"," - Topic"]
    uniformised =[]
    for playlist in theData:
        for i in range(len(playlist["musics"])):
            music = playlist["musics"][i]
            if music[1] in uniformised:
                continue
            new_artist_name = ""
            no_change_made = True
            for parameter in uniformisation_param:
                search_result = music[1].find(parameter)
                if search_result != -1:
                    if no_change_made:
                        new_artist_name = copy.deepcopy(music[1])
                        no_change_made = False
                    new_artist_name = "".join([new_artist_name[0:search_result],new_artist_name[search_result+len(parameter):len(new_artist_name)]])
            if not no_change_made:
                uniformised.append(music[1])
                define_exceptions(music[1],new_artist_name)
    load_exceptions(theData=theData)
    print("Uniformised the playlist.")
            
def write_actions(list_actions):
    #Keep count of the actions made in order to update the real playlist        
    if os.path.exists("data_and_stuff/listActions.txt"):
        os.remove("data_and_stuff/listActions.txt")
    with open("data_and_stuff/listActions.txt",mode="a") as f:
        for action in list_actions:
            for element in action:
                if element == action[0]:
                    f.write(element)
                else:
                    f.write(f'|{element}')
            f.write("\n")

def ceiling_in_ascending_sorted_sublist_(v,li,t):
    def helper(l,r):
        if li[t[l]]>=v:
            return l
        elif li[t[r]]<v:
            return r+1
        elif l>=r-1:
            return r
        else:
            m=(l+r)//2
            if li[t[m]]<=v:
                return helper(m,r)
            else:
                return helper(l,m)

    if not li:
        print('empty')
        return
    else:
        return helper(0,len(t)-1)
    
def longest_inc_subseq_nlogn(li):
    if not li:
        print('empty')
        return
    n=len(li)
    t=[0]
    b=[-1]*n
    for i in range(1,n):
        v=li[i]
        j=ceiling_in_ascending_sorted_sublist_(v,li,t)
        if j<len(t):
            t[j]=i
            if j>0:
                b[i]=t[j-1]
        else:
            if t:
                b[i]=t[-1]
            t.append(i)

    print('the longest increasing subsequence has {} elements'.format(len(t)))
    j=t[-1]
    indices=[]
    result=[]
    indices.append(j)
    result.append(li[j])
    while b[j]>-1:
        j=b[j]
        indices.insert(0,j)
        result.insert(0,li[j])

    return indices,result

def find_actions_configs(theData, theOldData):
    list_actions = []
    common_ids = []
    to_delete_ids = []
    to_add_ids = []
    theData_ids = [item['id'] for item in theData]
    theOldData_ids = [item['id'] for item in theOldData]
    delete_temp = []#just to make it work, cannot delete item of list while looping through it, otherwise won't work
    for id in theData_ids:
        if id in theOldData_ids:
            common_ids.append(id)
            delete_temp.append(id)
        else:
            to_add_ids.append(id)
    for element in delete_temp:
            theOldData_ids.pop(theOldData_ids.index(element))
    delete_temp = []        
    to_delete_ids = theOldData_ids
    
    for id in common_ids:
        music_delete = []
        music_add = []
        theOldData_specific = []
        theData_specific = []
        the_new_data = []
        for playlist in theOldData:
            if id == playlist["id"]:
                theOldData_specific = [[music[i]for i in range(len(music)-1)]for music in playlist["musics"]]
        for playlist in theData:
            if id == playlist["id"]:
                index = theData.index(playlist)
                theData_specific = [[music[i]for i in range(len(music)-1)]for music in playlist["musics"]]
        for music in theData_specific:
            if music not in theOldData_specific:
                music_add.append(music)
                delete_temp.append(music)
        for element in delete_temp:
            theData_specific.pop(theData_specific.index(element))
        delete_temp = []
        for music in theOldData_specific:
            if music not in theData_specific:
                music_delete.append(music)
                delete_temp.append(music)
        for element in delete_temp:
            theOldData_specific.pop(theOldData_specific.index(element))
        delete_temp = []
        for music in music_delete:
            this_action = ["dm",music[6]]
            list_actions.append(this_action)
        for music in theData_specific:
            oldIndex = theOldData_specific.index(music)
            the_new_data.append((oldIndex,music[1],music[2],music[3],music[4],music[5],music[6]))
        list_actions = find_actions(the_new_data=the_new_data,playlist_id=id,list_actions=list_actions)
        for music in music_add:
            inserting_at_position = theData[index]["musics"].index(music)
            this_action = ["im",music[6],music[5],inserting_at_position,id]
            list_actions.append(this_action)

    for id in to_delete_ids:
        this_action = ["dp",id]
        list_actions.append(this_action)

    for id in to_add_ids:
        for playlist in theData:
            if playlist["id"] == id:
                playlist_to_add = playlist
                break
        this_action = ["ap", playlist_to_add["_name"],id]
        list_actions.append(this_action)
        for music in playlist_to_add["musics"]:
            this_action = ["am", music[6], music[5],id]
            list_actions.append(this_action)
    
    return list_actions

def find_actions(the_new_data, playlist_id, list_actions = []):
    #adding numbers to have for each music old position (music[0]) and new position (music[-1])
    the_new_data_nb = []
    for i in range(len(the_new_data)):
        element = [the_new_data[i][j] for j in range(len(the_new_data[0]))]
        element.append(int(i))
        the_new_data_nb.append(element)
    
    #sorting the data to make it look like the original data, except we have in position -1 the final position in playlist of each music
    the_new_data_nb.sort(key=lambda item:item[0])

    #binary search LIS in the_new_data_nb,
    unsorted_list = [copy.deepcopy(music[-1]) for music in the_new_data_nb]
    indices, LIS = longest_inc_subseq_nlogn(unsorted_list)

    #find necessary actions to sort the unsorted_list
    # ------------------------------------------
    list_actions = list_actions
    #negative_LIS = final numbers that are out of place and that we therefore should move
    negative_LIS = []
    for i in range(len(the_new_data_nb)):
        if i not in LIS:
            negative_LIS.append(i)
    #for each of these numbers
    for nb in negative_LIS:
        #find where it is in the list
        for i in range(len(the_new_data_nb)):
            if the_new_data_nb[i][-1] == nb:
                index = i
                break
        #at which position in the list we're moving it to
        if nb > LIS[-1]:
            moving_to_end = True
            moving_to = len(the_new_data_nb) #end of list
            yt_moving_to = moving_to-1
        else:
            moving_to_end = False
            moving_to = indices[nb]
            if moving_to > index:
                yt_moving_to = moving_to-1
            else:
                yt_moving_to = moving_to
        #define action
        this_action = ["mm",the_new_data_nb[index][6],the_new_data_nb[index][5],yt_moving_to,playlist_id]
        list_actions.append(this_action)
        #update LIS:
        if moving_to_end:
            LIS.append(nb)
        else:
            LIS.insert(nb,nb)
        #update the_new_data_nb
        the_new_data_nb.insert(moving_to,the_new_data_nb[index])
        if moving_to > index:
            the_new_data_nb.pop(index)
        else:
            the_new_data_nb.pop(index+1)
        #udpate indices
        for i in range(len(indices)):
            if indices[i]>index:
                indices[i]-=1
        for i in range(nb,len(indices),1):
            indices[i] +=1
        if moving_to_end:
            indices.append(nb)
        else:
            indices.insert(nb,indices[nb]-1)
    return list_actions
    # ------------------------------------------

def list_artists_stat(music_list, only_purpose = True):
    list_artists_stat = {}
    for music in music_list:
        try:
            list_artists_stat[f"{music[1]}"] +=1
        except:
            list_artists_stat[f"{music[1]}"] = 1
    if only_purpose:        
        for key, value in list_artists_stat.items():
                print(f"{key} :\n{value} music{'s'[:value^1]}")
    return list_artists_stat#which is a dict btw

def list_all_artists(music_list):    
    #query all artists in the playlist
    list_artists = []
    for music in music_list:
        if not music[1] in list_artists:
            list_artists.append(music[1])
    return list_artists

def list_artists_stat_all_playlists(theData, ascending = False, reverse = False):
    list_artists_stat_all_playlists = {}
    for playlist in theData:
        this_list_artists_stat = list_artists_stat(playlist["musics"],only_purpose=False)
        for key, value in this_list_artists_stat.items():
            try:
                list_artists_stat_all_playlists[key][theData.index(playlist)] = value
            except:
                list_artists_stat_all_playlists[key] = [0 for i in range(len(theData))]
                list_artists_stat_all_playlists[key][theData.index(playlist)] = value
    
    if ascending:
        if not reverse:
            list_artists_stat_all_playlists = dict(sorted(list_artists_stat_all_playlists.items(), key=lambda item:sum(item[1])))
        else:
            list_artists_stat_all_playlists = dict(sorted(list_artists_stat_all_playlists.items(), key=lambda item:sum(item[1]), reverse= True))

    for key, value in list_artists_stat_all_playlists.items():
        print(f"{key} :")
        for i in range(len(theData)):
            if value[i] != 0:
                print(f"{value[i]} music{'s'[:value[i]^1]} in {theData[i]['_name']}")
        print("")
    return list_artists_stat_all_playlists

def search_artist(theData, artist_name):
    potential_artists = {}
    for playlist in theData:
        for musics in playlist["musics"]:
            if (artist_name.lower() in musics[1].lower()) | (musics[1].lower() in artist_name.lower()):
                try:
                    potential_artists[musics[1]][theData.index(playlist)] +=1
                except:
                    potential_artists[musics[1]] = [0 for i in range(len(theData))]
                    potential_artists[musics[1]][theData.index(playlist)] +=1    
    if len(potential_artists) == 0:
        print(f"'{artist_name}' was not found in your playlists.")
    elif len(potential_artists) == 1:
        if potential_artists.get(artist_name) != None:
            print(f"Found Artist '{artist_name}':")
            for i in range(len(theData)):
                if potential_artists[artist_name][i] !=0:
                    print(f"{potential_artists[artist_name][i]} music{'s'[:potential_artists[artist_name][i]^1]} in playlist '{theData[i]['_name']}'")
        else:
            print("Best finding:")
            print(f"Artist '{list(potential_artists.keys())[0]}':")
            key = list(potential_artists.keys())[0]
            for i in range(len(theData)):
                if potential_artists[key][i] !=0:
                    print(f"{potential_artists[key][i]} music{'s'[:potential_artists[key][i]^1]} in playlist '{theData[i]['_name']}'")
    else:
        if potential_artists.get(artist_name) != None:
            print(f"Found Artist '{artist_name}':")
            for i in range(len(theData)):
                if potential_artists[artist_name][i] !=0:
                    print(f"{potential_artists[artist_name][i]} music{'s'[:potential_artists[artist_name][i]^1]} in playlist '{theData[i]['_name']}'")
            print("")
            print("Also found:")
            for key, value in potential_artists.items():
                if key != artist_name:
                    print(f"Artist '{key}':")
                    for i in range(len(theData)):
                        if value[i] != 0:
                            print(f"{value[i]} music{'s'[:value[i]^1]} in playlist '{theData[i]['_name']}'")
                    print("")
        else:
            print("Best findings:")
            for key, value in potential_artists.items():
                if key != artist_name:
                    print(f"Artist '{key}':")
                    for i in range(len(theData)):
                        if value[i] != 0:
                            print(f"{value[i]} music{'s'[:value[i]^1]} in playlist '{theData[i]['_name']}'")
                    print("")
    return potential_artists

def original_order(music_list, reverse = False):
    return sorted(music_list, key = lambda item:(item[7][0:4],item[7][5:7],item[7][8:10],item[7][11:13],item[7][14:16],item[7][17:19]), reverse=reverse)

def original_order_artist(music_list, reverse = False):
    music_list2 = original_order(music_list, reverse=reverse)
    music_list = []
    while len(music_list2)!=0:
        first = copy.deepcopy(music_list2[0])
        print(f'First = {first}')
        to_delete = []
        for element in music_list2:
            if element[1] == first[1]:
                    print(f"Adding element : {element}")
                    music_list.append(element)
                    to_delete.append(element)
        for element in to_delete:
            music_list2.pop(music_list2.index(element))
    return music_list

def wish_list_write():
    want_to_write = True
    while want_to_write:
        answer2 =input(f"Write :\n")
        if os.path.exists("data_and_stuff/wishList.txt"):
            first_opening = False
        else:
            first_opening = True
        with open("data_and_stuff/wishList.txt", encoding='utf-8',mode="a") as f:
            if not first_opening:
                f.write('\n')
            f.write(f"{answer2}")
        answer2 = input(f"Do you still want to write in your wish list ?[y/n]\n")
        if answer2 == 'n':
            want_to_write = False
        elif answer2 == 'y':
            continue
        else:
            raise ValueError("Expected one of the following answers : y,n")

def wish_list_get(first = True):
    if os.path.exists("data_and_stuff/wishList.txt"):
        with open("data_and_stuff/wishList.txt",encoding='utf-8', mode="r") as f:
            wish_list = [line.strip() for line in f.readlines()]
            want_to_get = True 
            if len(wish_list)==0:
                print("Cannot read, Wish List is empty.")
                return
            if first:
                on_position = 0
                print(f"Element 0 (first element):\n{wish_list[0]}\n")
            else:
                on_position = len(wish_list)-1
                print(f"Element {len(wish_list)-1} (last element):\n{wish_list[-1]}\n")
            while want_to_get:
                p = True if on_position!=0 else False
                n = True if on_position!=(len(wish_list)-1) else False
                d = True if len(wish_list)!=0 else False
                answer2 = input(f"Following action? {'PREVIOUS[p] | ' if p else ''}{'NEXT[n] | 'if n else ''}STOP[s]{' | DELETE[d]' if d else ''}\n")
                print("")
                if (answer2 == 's'):
                    with open("data_and_stuff/wishList.txt",encoding='utf-8', mode="w") as f:
                        for line in wish_list:
                            if wish_list.index(line) == 0:
                                f.write(line)
                            else:
                                f.write('\n'+line)
                    break
                elif (answer2 == 'p') & p:
                    on_position -=1
                elif (answer2 == 'n') & n:
                    on_position+=1
                elif (answer2 == 'd') & d:
                    wish_list.pop(on_position)
                    if len(wish_list) == 0:
                        print("Wish list is empty.")
                        os.remove("data_and_stuff/wishList.txt")
                        break
                    elif on_position == len(wish_list):
                        on_position -=1
                else:
                    raise ValueError(f"Expected one of the following letters: {'p,'if p else ''}{'n,'if n else ''}s{',d' if d else ''}")
                print(f"Element {on_position}{' (first element)' if (on_position==0)&(len(wish_list)!=1) else ''}{' (last element)' if (on_position==(len(wish_list)-1))&(len(wish_list)!=1) else ''}{' (only element)' if len(wish_list)==1 else ''}:\n{wish_list[on_position]}")
    else:
        print("Cannot read, Wish List is empty.")

def sorting_an_area1(data):
    answer = input("Do you want to sort your entire playlist that way or only a specific part?\nAnswers:\nentire playlist -> [e]\nspecific area -> [s]\n")
    if answer == "e":
        return data, 'all'
    elif answer == "s":
        answer = input(f"Give a specific area. (playlist begins at position 0)\nLast position in playlist: {len(data)-1}\nFormat answers:\nfrom position [x] included to position [y] included -> [x]-[y]\none number [z] -> [z]\nfrom position [x] included to end -> [x]-\nfrom start to position [y] included -> -[y]\nseparate multiple inputs with commas\n!no spaces!\n")
        for character in answer:
            if character not in ["0","1","2","3","4","5","6","7","8","9","-",","]:
                raise ValueError("Wrong Input.")
        for i in range(1,len(answer)):
            if answer[i-1]=="," and answer[i]==",":
                raise ValueError("Wrong Input.")
        numbers = []
        for param in answer.split(","):
            if "-" in param:
                if param.count("-") >1:
                    raise ValueError("Wrong Input.")
                if len(param) == 1:
                    return data, 'all'
                elif param[-1] == "-":
                    start_bound = int(param[:len(param)-1])
                    end_bound = len(data)
                elif param[0] == "-":
                    start_bound = 0
                    end_bound = int(param[1:])+1
                else:
                    start_bound = int(param.split("-")[0])
                    end_bound = int(param.split("-")[1])+1
                if (start_bound>=len(data))|(end_bound>=len(data))|(start_bound+1>end_bound):
                    raise ValueError("Wrong Input.")
                for i in range(start_bound,end_bound,1):
                    numbers.append(i)
            else:
                number = int(param)
                if number >= len(data):
                    raise ValueError("Wrong Input.")
                numbers.append(number)
        numbers = list(dict.fromkeys(numbers))
        numbers.sort()
        very_specific_data = [data[number] for number in numbers]
        return very_specific_data, numbers

def sorting_an_area2(data,sorted_very_specific_data,numbers):
    if numbers == "all":
        return sorted_very_specific_data
    else:
        for i in range(len(numbers)):
            data[numbers[i]] = sorted_very_specific_data[i]
        return data

def save_config(data,name_of_config, playlist_number = None):
    found_somewhere_to_save = False
    i=1
    while not found_somewhere_to_save:
        if not os.path.exists("".join(['configs/',str(i),str(i),str(i),'.txt'])):
            found_somewhere_to_save = True
        else:
            i+=1
            if i>15:
                print("You already have 15 configs. Delete one of them before trying to save another config.")
                return
    with open(''.join(['configs/',str(i),str(i),str(i),'.txt']), encoding='utf-8', mode="w") as f:
        if playlist_number == None:
            f.write(f"{name_of_config}\n")
            f.write('all\n')
            beautiful_write(data,f)
        else:
            f.write(f'{name_of_config}\n')
            f.write(f'{data[int(playlist_number)-1]["id"]}\n')
            beautiful_write([data[int(playlist_number)-1]],f)
    print("Config saved.")

def load_config(data,nb):
    with open(f"configs/{nb}{nb}{nb}.txt", encoding='utf-8', mode ='r') as f:
        print(f"Loading config '{f.readline().strip()}'")
        id = f.readline().strip()
        if id == 'all':
            return get_data(f, config=True)
        else:
            for i in range(len(data)):
                if data[i]["id"] == id:
                    data[i] = get_data(f, config=True)[0]
                    return data             

def delete_config(nb):
    os.remove(f"configs/{nb}{nb}{nb}.txt")
    for i in range(int(nb)+1,16):
        if os.path.exists(f"configs/{str(i)}{str(i)}{str(i)}.txt"):
            os.rename(f"configs/{str(i)}{str(i)}{str(i)}.txt",f"configs/{str(i-1)}{str(i-1)}{str(i-1)}.txt")

def shuffle_playlist(music_list):
    return random.sample(music_list,len(music_list))

def playlist_duration(music_list):
    sum_seconds = 0
    for music in  music_list:
        timeDeltaObject = aniso8601.parse_duration(music[3])
        sum_seconds += timeDeltaObject.total_seconds()
    hours = int(sum_seconds//3600)
    minutes = int((sum_seconds%3600)//60)
    seconds = int((sum_seconds%3600)%60)
    print(f"Your playlist duration is:\n{hours} hour{'s' if hours>1 else ''}, {minutes} minute{'s' if minutes>1 else ''} and {seconds} second{'s' if seconds >1 else ''}.")

def return_total_seconds(music):
    timeDeltaObject = aniso8601.parse_duration(music[3])
    return timeDeltaObject.total_seconds()

def sort_by_duration(music_list, reverse = False):
    return sorted(music_list, key=return_total_seconds,reverse=reverse)

def playlist_manager():
    #get the data, initialize (load exceptions...)
    theData = ''
    with open("data_and_stuff/myData.txt",encoding='utf-8',mode="r") as f:
        theData = get_data(f=f)
    still_managing_playlists = True
    uniformisation(theData=theData)    
    list_actions = []
    worked_on_wich_playlists = [False for i in range(len(theData))]
    theOldData = copy.deepcopy(theData)
        
    #playlist management
    while still_managing_playlists:
        updating_data = True
        loading_configs = False
        #ask for which playlist to manage
        specific_data = choose_playlist(theData, worked_on_wich_playlists)
        if specific_data == None:
            answer = input(f"What do you want to do with multiple playlists?\n(1)Define exceptions\n(2)List artists\n(3)Search Artist\n(4)Wish List\n(5)Configs of playlists\n")
            try:
                answer = int(answer)
            except:
                raise ValueError("An integer was expected")
            if answer == 1:
                actual_name, new_name = input(f"Type in artist name you want to modify and new artist name in the following way:\nactual_artist_name|new_artist_name\n").split("|")
                define_exceptions(actual_name,new_name)
                theData = load_exceptions(theData=theData)
            elif answer == 2:
                updating_data = False
                answer = input("How do you want to list artists?\n(1) default order (in order of playlist)\n(2) ascending order (from artist with the fewest songs to artist with the most songs)\n(3) descending order (from artists with the most songs to artist with the fewest songs)\n")
                try:
                    answer = int(answer)
                except:
                    raise ValueError("An integer was expected")
                if answer == 1:
                    print("Listing all artists in all of your playlists...")
                    list_artists_stat_all_playlists(theData=theData)
                    print("Listed all artists in all of your playlists.")
                elif answer == 2:
                    print("Listing all artists in all of your playlists in ascending order...")
                    list_artists_stat_all_playlists(theData=theData, ascending=True)
                    print("Listed all artists in all of your playlists in ascending order.")
                elif answer == 3:
                    print("Listing all artists in all of your playlists in descending order...")
                    list_artists_stat_all_playlists(theData=theData, ascending=True,reverse=True)
                    print("Listed all artists in all of your playlists in descending order.")
                else:
                    raise ValueError("The number typed in isn't valid.")
            elif answer == 3:
                updating_data = False
                answer = input(f"Which artist do you want to search?\n")
                print(f"Searching Artist '{answer}'...")
                search_artist(theData=theData,artist_name=answer)
            elif answer == 4:
                updating_data = False
                answer = input(f"What do you want to do with your wish list?\n(1)Add element\n(2)Get first element (added first)\n(3)Get last element (added last)\n")
                try:
                    answer = int(answer)
                except:
                    raise ValueError("An integer was expected")
                if answer == 1:
                    wish_list_write()
                elif answer == 2:
                    wish_list_get()
                elif answer == 3:
                    wish_list_get(first=False)
                else:
                    raise ValueError("The number typed in isn't valid.")
            elif answer == 5:
                name_of_configs = []
                for i in range(15):
                    if os.path.exists(f"configs/{i}{i}{i}.txt"):
                        with open(f"configs/{i}{i}{i}.txt",encoding='utf-8', mode='r')as f:
                            name_of_configs.append(f.readline().strip())
                print(f"You have {len(name_of_configs)} saved configs{':' if len(name_of_configs)>0 else '.'}")
                for i in range(len(name_of_configs)):
                    print(f"({str(i+1)}): {name_of_configs[i]}")
                answer = input("Managing configs of playlists:\n(1)Save config\n(2)Load config\n(3)Delete config\n")
                try:
                    answer = int(answer)
                except:
                    raise ValueError("An integer was expected")
                if answer == 1:
                    updating_data = False
                    answer = input(f"Save the whole data or only one playlist's data?\n(a) all data\n([number]) one playlist's data, number being it's number\n")
                    answer2 = input("Name your config (use only alphanumeric characters):\n")
                    if not answer2.isalnum():
                        raise ValueError("Name of playlist is not alphanumeric. Use only alphanumeric characters (A-Z,a-z,0-9).")
                    if answer == 'a':
                        save_config(theData,answer2)
                    elif int(answer)-1 in [i for i in range(len(theData))]:
                        save_config(theData,answer2,int(answer))
                    else:
                        raise ValueError("Unexpected answer.Expected [a] or [number] with number one of your playlists' number.")
                elif answer == 2:
                    loading_configs = True
                    answer = input("Type in the number of the config that you want to load:\n")
                    try:
                        answer = int(answer)
                    except:
                        raise ValueError("An integer was expected.")
                    if os.path.exists(f"configs/{int(answer)}{int(answer)}{int(answer)}.txt"):
                        theData = load_config(theData,answer)
                    else:
                        raise ValueError("Wrong config number.")
                elif answer == 3:
                    updating_data = False
                    answer = input("Type in the number of the config that you want to delete:\n")
                    try:
                        answer = int(answer)
                    except:
                        raise ValueError("An integer was expected.")
                    if os.path.exists(f"configs/{int(answer)}{int(answer)}{int(answer)}.txt"):
                        delete_config(answer)
                    else:
                        raise ValueError("Wrong config number.")
                else:
                    raise ValueError("The number typed in isn't valid.")
            else:
                raise ValueError("The number typed in isn't valid.")
        else:
            answer = input(f"What do you want to do with the playlist \'{specific_data['_name']}\' ?\n(1)Sort alphabetically\n(2)Sort by artist by grouping (biggest group)\n(3)List Artists\n(4)Sort by original order (creation of playlist order)\n(5)Random shuffle\n(6)Playlist duration\n(7)Sort by duration\n")
            try:
                answer = int(answer)
            except:
                raise ValueError("An integer was expected")
            if answer == 1:
                answer = input(f"What do you want to sort alphabetically?\n(1)All musics\n(2)Artists\n(3)Musics of artists\n(4)Artists, then musics of artists\n(5)[Reverse]All musics\n(6)[Reverse]Artists\n(7)[Reverse]Musics of artists\n(8)[Reverse]Artists, then musics of artists\n")
                try:
                    answer = int(answer)
                except:
                    raise ValueError("An integer was expected")
                if answer == 1:
                    print("Sorting all musics alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_all_musics_alphabetically(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("Sorted all musics alphabetically.")
                elif answer == 2:
                    print("Sorting artists alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_artists_alphabetically(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("Sorted artists alphabetically.")
                elif answer == 3:
                    print("Sorting musics of artists alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_musics_of_artists_alphabetically(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("Sorted musics of artists alphabetically.")
                elif answer == 4:
                    print("Sorting artists alphabetically, then musics of artists alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_artists_then_musics_alphabetically(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("Sorted artists alphabetically, then musics of artists alphabetically.")
                elif answer == 5:
                    print("[Reverse]Sorting all musics alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_all_musics_alphabetically(music_list=very_specific_data, reverse= True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("[Reverse]Sorted all musics alphabetically.")
                elif answer == 6:
                    print("[Reverse]Sorting artists alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_artists_alphabetically(music_list=very_specific_data,reverse= True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("[Reverse]Sorted artists alphabetically.")
                elif answer == 7:
                    print("[Reverse]Sorting musics of artists alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_musics_of_artists_alphabetically(music_list=very_specific_data,reverse=True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("[Reverse]Sorted musics of artists alphabetically.")
                elif answer == 8:
                    print("[Reverse]Sorting artists alphabetically, then musics of artists alphabetically...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_artists_then_musics_alphabetically(music_list=very_specific_data, reverse=True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("[Reverse]Sorted artists alphabetically, then musics of artists alphabetically.")
                else:
                    raise ValueError("The number typed in isn't valid")
            elif answer == 2:
                print("Sorting the playlist by grouping the musics by artist name (biggest group)...")
                very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                sorted_very_specific_data = sort_grouping(music_list=very_specific_data)
                sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                print(f"The {'playlist' if area =='all' else 'area'} is sorted by grouping the musics by artist name (biggest group).")
            elif answer == 3:
                updating_data = False
                print("Listing all artists in the playlist '"+specific_data["_name"]+"'...")
                list_artists_stat(specific_data["musics"])
                print("Listed all artists in the playlist '"+specific_data["_name"]+"'.")
            elif answer == 4:
                answer = input(f"How do you want your playlist back?\n(1)Ascending Order (most recently added musics at the bottom of the playlist)\n(2)Descending Order (most recently added musics at the top of the playlist)\n(3)Artist order ascending (first artist added to playlist at the top)\n(4)Artist order descending (first artist added to playlist at the bottom)\n")
                try:
                    answer = int(answer)
                except:
                    raise ValueError("An integer was expected")
                if answer == 1:
                    print("Getting your playlist back to its original order (Ascending)...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = original_order(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("Got your playlist back to its original order (Ascending).")                    
                elif answer == 2:
                    print("Getting your playlist back to its original order (Descending)...")
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = original_order(music_list=very_specific_data, reverse=True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                    print("Got your playlist back to its original order (Descending).")
                elif answer == 3:
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = original_order_artist(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                elif answer == 4:
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = original_order_artist(music_list=very_specific_data, reverse=True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                else:
                    raise ValueError("The number typed in isn't valid.")
            elif answer == 5:                
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = shuffle_playlist(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
            elif answer == 6:
                updating_data = False
                playlist_duration(music_list=specific_data["musics"])
            elif answer == 7:
                answer = input(f"How do you want your playlist sorted?\n(1)Ascending (shortest musics at the start)\n(2)Descending (Longest musics at the start)\n")
                try:
                    answer = int(answer)
                except:
                    raise ValueError("An integer was expected")
                if answer == 1:
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_by_duration(music_list=very_specific_data)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                elif answer == 2:
                    very_specific_data,area = sorting_an_area1(data=specific_data["musics"])
                    sorted_very_specific_data = sort_by_duration(music_list=very_specific_data, reverse = True)
                    sorted_music_list = sorting_an_area2(data=specific_data["musics"],sorted_very_specific_data=sorted_very_specific_data,numbers=area)
                else:
                    raise ValueError("The number typed in isn't valid.")
            else:
                raise ValueError("The number typed in isn't valid.")
        #writes all the data into a file (updated data)
        if updating_data:
            if specific_data !=None:
                index = theData.index(specific_data)
                theData[index]["musics"] = sorted_music_list
            with open("data_and_stuff/myDataUpdated.txt","w",encoding='utf-8') as f:
                beautiful_write(theData, f) 
            print("Updated the data into myDataUpdated.txt file.")
        #continue managing or not?
        answer = input("Do you wish to continue managing your playlists?[y/n]\n")
        if answer == 'y':
            continue
        elif answer == 'n': 
            print("Finished managing playlists.")
            still_managing_playlists = False
        else:
            raise ValueError("Expected the following type of answer: 'y' or 'n'")
        #find actions made over all the data
        if not loading_configs:
            for i in range(len(worked_on_wich_playlists)):
                if worked_on_wich_playlists[i]:
                    this_list_actions = find_actions(theData[i]["musics"],theData[i]["id"])
                    list_actions += this_list_actions
        else:
            list_actions = find_actions_configs(theData=theData,theOldData=theOldData)
        #write those actions into text file
        write_actions(list_actions=list_actions)
                
playlist_manager()