import json
import requests
import json
from difflib import SequenceMatcher
import chparse
import os
from dotenv import load_dotenv
load_dotenv()

def get_lyrics_instagram(id,auth):
    url = "https://i.instagram.com/api/v1/music/track/{}/lyrics/?audio_asset_id=1&audio_cluster_id=1".format(id)
    
    headers = {
        'User-Agent': 'Instagram 212.0.0.38.119 Android (31/12; 450dpi; 1080x2327; samsung; SM-G985F; y2s; exynos990; en_GB; 329675731)',
        'authorization': auth    
    }

    response = requests.request("GET", url, headers=headers)
    print(response.content)
    assert response.status_code == 200

    return json.loads(response.content)

def get_lyrics_spotify(id,auth):
    url = "https://spclient.wg.spotify.com/color-lyrics/v2/track/{}".format(id)
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'spotify lyrics to clone hero',
        'Authorization': 'Bearer {}'.format(auth),
        'app-platform': 'WebPlayer'
    }

    response = requests.request("GET", url, headers=headers)
    # print(response)
    assert response.status_code == 200

    return json.loads(response.content)


def get_token_spotify(auth):
    url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player".format(id)
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'app-platform': 'WebPlayer',
        'User-Agent': 'spotify lyrics to clone hero', 
        'Cookie': 'sp_dc={}'.format(auth)
    }

    response = requests.request("GET", url, headers=headers)
    # print(response.content)
    assert response.status_code == 200

    return json.loads(response.content)["accessToken"]

# lyrics = get_lyrics('321060052413953', os.getenv("instagram_auth_token"))

# print(lyrics)

# spotify_auth = get_token_spotify(os.getenv("cookie_spotify"))
# print(spotify_auth["accessToken"])

# spotify_lyrics = get_lyrics_spotify('4Oun2ylbjFKMPTiaSbbCih',spotify_auth["accessToken"])
# print(spotify_lyrics["lyrics"]['lines'][0]['words'])

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def uncensor_lyrics(lyrics, spotify_lyrics): 
    for key in lyrics["lyrics"]["phrases"]:
        value = key['phrase']
        if '*' in value:
            found = 0
            for line in spotify_lyrics["lyrics"]['lines']:
                words = line['words']
                # print(words)
                if similar(value, words) > 0.5 and len(value) == len(words):
                    # print("NEW " + words)
                    key['phrase'] = words
                    found = 1
                    break
            if(found == 0): 
                print("OLD " + value)
                firstPos = value.find('*') 
                secondPos = value.rfind('*')
                print("WEE WOO")
                for line in spotify_lyrics["lyrics"]['lines']:
                    words = line['words']
                    # print(words)
                    if similar(value, words) > 0.5:
                        value_list = value.split()
                        words_list = words.split()
                        for i in range(len(value_list)):
                            if('*' in value_list[i]):
                                value_list[i] = words_list[i]
                        potential = " ".join(value_list)
                        print("NEW " + potential)
                        key['phrase'] = potential
                        found = 1
                        break
    return lyrics

# print(json.dumps(lyrics, separators=(',', ':')))

def seconds_to_position(seconds, chart): #adapted from herochartio
	bps = 120000
	lastBpsChange = 0
	elapsed = 0
	lastts = 0
	resolution = 192

	for i in chart.sync_track:
		ts = i.time
		lastBpsChange = elapsed
		elapsed += (ts - lastts) * 60000 / bps / resolution
		if elapsed > seconds:
			return lastts + (elapsed - lastBpsChange) / (60000 / bps / resolution)
		if i.kind == chparse.NoteTypes.BPM:
			bps = i.value
		lastts = ts;

	return lastts + (seconds - lastBpsChange) / (60000 / bps / resolution)

def lyricsToChart(chart, lyrics): 
    for key in lyrics["lyrics"]["phrases"]:
        phrase = key['phrase'].replace('"', "''").replace('-', "=")
        chart.events.add(chparse.note.Event(int(seconds_to_position(key['start_time_in_ms'] / 1000, chart)), "phrase_end"))
        chart.events.add(chparse.note.Event(int(seconds_to_position(key['start_time_in_ms'] / 1000, chart)), "phrase_start"))
        if "word_offsets" in key:
            for offsets in key["word_offsets"]:
                chart.events.add(chparse.note.Event(int(seconds_to_position((key['start_time_in_ms'] + offsets["end_offset_ms"]) / 1000, chart)), "lyric " + phrase[offsets['start_index']:offsets['end_index']]))
            # chart.events.add(chparse.note.Event(int(seconds_to_position(key['end_time_in_ms'] / 1000, chart)), "phrase_end"))
    return chart

def search_instagram_songs(query, auth):
    url = "https://i.instagram.com/api/v1/music/search/"
    
    data = {
        "from_typeahead":"false",
        "product":"story_camera_music_overlay_post_capture",
        "q":query
    }


    headers = {
        'User-Agent': 'Instagram 212.0.0.38.119 Android (31/12; 450dpi; 1080x2327; samsung; SM-G985F; y2s; exynos990; en_GB; 329675731)',
        'authorization': auth
    }

    response = requests.request("POST", url, headers=headers, data=data)
    # print(response.content)
    assert response.status_code == 200

    return json.loads(response.content)

def search_spotify_songs(query ,auth):
    url = "https://api.spotify.com/v1/search?q={}&type=track&limit=30".format(query)
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'spotify lyrics to clone hero',
        'Authorization': 'Bearer {}'.format(auth)
    }

    response = requests.request("GET", url, headers=headers)
    # print(response.content)
    assert response.status_code == 200

    return json.loads(response.content)

# print(search_result["items"].items())
# print(search_result["items"][0]["track"]["id"])
# print(search_result["items"][0]["track"]["title"])
# print(search_result["items"][0]["track"]["display_artist"])
# print(search_result["items"][0]["track"]["has_lyrics"])

# print(search_result["tracks"]["items"][0]["id"])
# print(search_result["tracks"]["items"][0]["name"])
# print(search_result["tracks"]["items"][0]["artists"][0]["name"])

def double_search(query, instagram_auth, spotify_auth):
    instagram_search_result = search_instagram_songs(query, instagram_auth)
    spotify_search_result = search_spotify_songs(query, spotify_auth)
    matched = 0
    double_search_result = []
    for result in instagram_search_result["items"]:
        track = result["track"]
        if track["has_lyrics"] == "False": break
        print("CHECKING " + track["title"])
        for spotify_track in spotify_search_result["tracks"]["items"]:
            if similar(track["title"], spotify_track["name"]) > 0.9 and similar(track["display_artist"], spotify_track["artists"][0]["name"]) > 0.5:
                matched += 1
                info = {}
                info["title"] = track["title"]
                info["artist"] = track["display_artist"]
                info["cover_art"] = spotify_track["album"]["images"][0]["url"]
                info["spotify_id"] = spotify_track["id"]
                info["instagram_id"] = track["id"]
                double_search_result.append(info)
                print("MATCHED " + track["title"] + " WITH " + spotify_track["name"])
                break
    print("matched " + str(matched) + " out of 30")
    return double_search_result

spotify_auth = get_token_spotify(os.getenv("cookie_spotify"))
double_search_result = double_search('stupid for you', os.getenv("instagram_auth_token"), spotify_auth)
print(json.dumps(double_search_result))