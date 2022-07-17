import base64
import io
import sys
from flask import Flask, make_response, request, send_file, after_this_request, jsonify, redirect, flash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_cors import CORS
import json
import instagram_clonhur
import chparse
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])

spotify_auth = instagram_clonhur.get_token_spotify(os.getenv("cookie_spotify"))

@app.route('/search', methods=['POST'])
def generate():
	if request.method == 'POST':
		data = request.get_json()
		return jsonify(instagram_clonhur.double_search(data['query'], os.getenv("instagram_auth_token"), spotify_auth))

ALLOWED_EXTENSIONS = ["mid", "chart"]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
		
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	# if request.method == 'POST':
	data = request.form
	print('Data Received: "{data}"'.format(data=data))
	spotify_id = request.form['song-ids'].split('\\', 2)[0]
	instagram_id = request.form['song-ids'].split('\\', 2)[1]
	print(spotify_id)
	print(instagram_id)
	instagram_lyrics = instagram_clonhur.get_lyrics_instagram(instagram_id, os.getenv("instagram_auth_token"))
	spotify_lyrics = instagram_clonhur.get_lyrics_spotify(spotify_id, spotify_auth)
	lyrics = instagram_clonhur.uncensor_lyrics(instagram_lyrics, spotify_lyrics)
	# print(lyrics)
	file = request.files["file"]
	if file:
		# print(file)
		# file_string = base64.b64encode(file.read())
		# file_string2 = base64.b64decode(file_string)
		# print(file.read().decode('utf-8'))
		buf = io.StringIO(file.read().decode('utf-8'))
		chart = chparse.load(buf)
		chart_lyrics = instagram_clonhur.lyricsToChart(chart, lyrics)
		fileobj = io.StringIO()
		fileobj.seek(0)
		fileobj.truncate()
		chart_lyrics.dump(fileobj=fileobj)
		fileobj.seek(0)
		response = make_response(fileobj.read())
		response.headers.set('Content-Type', 'text/plain')
		response.headers.set('Content-Disposition', 'attachment', filename='%s' % file.filename)
		return response
  
if __name__ == "__main__":
    app.secret_key = 'super secret key'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
