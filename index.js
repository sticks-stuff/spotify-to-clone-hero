var unirest = require('unirest')
var SpotifyWebApi = require('spotify-web-api-node')
var lineReader = require('line-reader')
var fs = require('fs')
var ChartIO = require('herochartio').ChartIO
require("dotenv").config();

lyrics = [];
unirest.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")
	.headers({'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'spotify lyrics to clone hero', 'Cookie': `sp_dc=${process.env.sp_dc};`})
	.send()
	.end(response=> {
		var json = response.body
		var spotifyApi = new SpotifyWebApi();
		spotifyApi.setAccessToken(json.accessToken)
		spotifyApi.searchTracks('Simon Viklund - I Will Give You My All')
		.then(function(data) {
			unirest.get(`https://spclient.wg.spotify.com/color-lyrics/v2/track/${data.body.tracks.items[0].id}`)
				.headers({'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': `Bearer ${json.accessToken}`, 'app-platform': 'WebPlayer', 'User-Agent': 'spotify lyrics to clone hero'})
				.send()
				.end(lyric_response=> {
					ChartIO.load("Simon Viklund - I Will Give You My All/notes.chart").then(chart => {
						lyric_response.body.lyrics.lines.forEach(element => {
							chart.Events[parseInt(chart.secondsToPosition(element.startTimeMs / 1000))] = [
								{ type: 'E', name: 'phrase_end' },
								{ type: 'E', name: 'phrase_start' },
								{ type: 'E', name: `lyric ${element.words}` }
							]
						});
						ChartIO.save(chart, "Simon Viklund - I Will Give You My All/notes.chart");
					})
				})
		}, function(err) {
			console.log('Something went wrong!', err);
		});
	})