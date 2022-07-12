from json.tool import main
import uuid as uuid_library
import hmac
import json
import hashlib
from datetime import datetime
import requests
import six.moves.urllib as urllib
import json
from difflib import SequenceMatcher
import chparse
from dotenv import load_dotenv
load_dotenv()

def get_lyrics(id,auth):
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

    return json.loads(response.content)


auth = login(os.getenv("instagram_auth_token"))

lyrics = get_lyrics('321060052413953', auth)

# print(lyrics)

spotify_auth = get_token_spotify(os.getenv("cookie_spotify"))
# print(spotify_auth["accessToken"])

spotify_lyrics = get_lyrics_spotify('4Oun2ylbjFKMPTiaSbbCih',spotify_auth["accessToken"])
# print(spotify_lyrics["lyrics"]['lines'][0]['words'])

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

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

# print(json.dumps(lyrics, separators=(',', ':')))

def secondsToPosition(seconds, chart):
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

with open('notes.chart', "r+") as chartfile:
    chart = chparse.load(chartfile)
    for key in lyrics["lyrics"]["phrases"]:
        phrase = key['phrase'].replace('"', "''").replace('-', "=")
        chart.events.add(chparse.note.Event(int(secondsToPosition(key['start_time_in_ms'] / 1000, chart)), "phrase_end"))
        chart.events.add(chparse.note.Event(int(secondsToPosition(key['start_time_in_ms'] / 1000, chart)), "phrase_start"))
        if "word_offsets" in key:
            for offsets in key["word_offsets"]:
                chart.events.add(chparse.note.Event(int(secondsToPosition((key['start_time_in_ms'] + offsets["end_offset_ms"]) / 1000, chart)), "lyric " + phrase[offsets['start_index']:offsets['end_index']]))
            # chart.events.add(chparse.note.Event(int(secondsToPosition(key['end_time_in_ms'] / 1000, chart)), "phrase_end"))
    print(chart.events) 
    chartfile.seek(0)
    chart.dump(chartfile)
    chartfile.truncate()
