
// Import dependencies
const fs = require("fs")
const express = require("express")
const multer = require("multer")
var unirest = require('unirest')
var SpotifyWebApi = require('spotify-web-api-node')
var ChartIO = require('herochartio').ChartIO
require("dotenv").config()

// Setup express
const app = express()
const port = 3000

// Setup Storage
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        // Set the destination where the files should be stored on disk
        cb(null, "uploads")
    },
    filename: function (req, file, cb) {
        // Set the file name on the file in the uploads folder
        cb(null, file.fieldname + "-" + Date.now() + '.' + file.originalname.split('.')[1])
    },
    fileFilter: function (req, file, cb) {
        if (file.mimetype !== "text/plain" || file.mimetype !== "audio/midi") {
            // To reject a file pass `false` or pass an error
            cb(new Error(`Forbidden file type`))
        } else {
            // To accept the file pass `true`
            cb(null, true)
        }
    }
})

// Setup multer
const upload = multer({ storage: storage }) // { destination: "uploads/"}
// Setup the upload route
app.post("/upload", upload.single("data"), (req, res) => {
	console.log(req.body)
    if (req.file) {
        try {
			// const raw = fs.readFileSync(`uploads/${req.file.filename}`)
			// console.log(raw.toString())
			unirest.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")
				.headers({'Accept': 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'spotify lyrics to clone hero', 'Cookie': `sp_dc=${process.env.sp_dc}`})
				.send()
				.end(response=> {
					var json = response.body
                    var songid = req.body.song.split("https://open.spotify.com/track/")[1]
                    songid = songid.split('?')[0]
					unirest.get(`https://spclient.wg.spotify.com/color-lyrics/v2/track/${songid}`)
						.headers({'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': `Bearer ${json.accessToken}`, 'app-platform': 'WebPlayer', 'User-Agent': 'spotify lyrics to clone hero'})
						.send()
						.end(lyric_response=> {
							ChartIO.load(`uploads/${req.file.filename}`).then(chart => {
								lyric_response.body.lyrics.lines.forEach(element => {
									chart.Events[parseInt(chart.secondsToPosition(element.startTimeMs / 1000))] = [
										{ type: 'E', name: 'phrase_end' },
										{ type: 'E', name: 'phrase_start' },
										{ type: 'E', name: `lyric ${element.words}` }
									]
								})
								ChartIO.save(chart, `uploads/${req.file.filename}`)
								let rs = fs.createReadStream(`uploads/${req.file.filename}`)
								res.attachment(req.file.originalname)
								rs.pipe(res)
							})
						})
				})
        } catch (ex) {
            // Show error
            console.log(ex)
            // Send response
            res.status(500).send({
                ok: false,
                error: "Something went wrong on the server"
            })
        }
    } else {
        res.status(400).send({ ok: false,
            error: "Please upload a file"
        })
    }
})

// Start the server
app.listen(port, () => console.log(`file uploader listening at http://localhost:${port}`))