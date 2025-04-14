# IDEA

I want to make a tool to transcribe and visualize the rhythm of the opening bars of a lot of different recordings of opus 127. 


## Transcription:

I'd like to make a python script which runs a loop which does:
1. Accept a quartet name
2. Accept a spotify url/uri
3. Allow timestamp input (spacebar presses, followed by 'x', see below)
4. produce an output: times.json, which will be a list of dictionaries (see below).

Each time the spacebar is tapped, a timestamp is recorded.
When x is pressed, the sequence of timestamps is stored, all relative to the first tap, which will be recorded as time 0.
the time at which x was pressed will not be recorded.

After x is pressed, times.json will be updated with the latest data (to ensure no data loss if / when the program is terminated).
Alternatively, could hardcode to accept only 12 spacebar presses.

For example the data file might look like:

times.json
----
[
    {
        "artist": "Cleveland Quartet",
        "spotify": "https://open.spotify.com/track/3Ngfw9Yd07LiLT8HJ76MZo?si=2661a3c36d5c4de1", 
        "timestamps": [0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11],
    },
    // ...
]

I expect to record 12 timestamps for each recording (going to ignore the v1 filligree at first). 

Please write this script in clean, elegant python3 code.

## Reading timestamps from the score:
each eight note counts as 1. 
```
0, 4, 1, 2, 1, 4, 1, 2, 1, 3, 1, 4
t = [0, 4, 1, 2, 1, 4, 1, 2, 1, 3, 1, 4]
s = []
n = 0
for i in t:
    n += i
    s.append(n)
print(s)
> [0, 4, 5, 7, 8, 12, 13, 15, 16, 19, 20, 24]
# need to apply bpm to turn relative relationships into absolute ones.
# assume 30 bpm (kinda slow, but easy math), can just divide everything by 2.

s = [i / 2.0 for i in s]
print(json.dumps({'name':'tempo@30bpm', 'spotify':'','timestamps':s}, indent=4))
{
    "name": "tempo@30bpm",
    "spotify": "",
    "timestamps": [
        0.0,
        2.0,
        2.5,
        3.5,
        4.0,
        6.0,
        6.5,
        7.5,
        8.0,
        9.5,
        10.0,
        12.0
    ]
}
```

## Visualization: 
Please build a simple and elegant data visualization as a static web page that has the following files: 
1. index.html
2. viz.js
3. viz.css
4. score.png
5. times.json -- a list of dictionaries such as:
```
[
    {
        "artist": "Cleveland Quartet",
        "spotify": "https://open.spotify.com/track/3Ngfw9Yd07LiLT8HJ76MZo?si=2661a3c36d5c4de1", 
        "timestamps": [0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11],
    },
    {
        "artist": "Default",
        "spotify": "", 
        "timestamps": [0, 4, 5, 7, 8, 12, 13, 15, 16, 19, 20, 24],
    },
]
```
where t1 through t11 are float timestamps.

The static page will will reference times.json and visualize the data within using the latest version of d3.js.
If a build step is needed, it will use esbuild and provide a `build.sh` script.


the background color for the entire page will be configured with css.
The page will have the following elements, described below
1. Title: a large title element
2. Image: the image 'score.png' displayed at full width
3. Option: an option radio button (scaled | unscaled)
4. Rows: a series of rows, one for each dictionary in times.json, which is the meat of the visualization.
5. Footnote: a footnote linking to the github repository.

### Rows:
Each row will visualize one dictionary from times.json as follows:

* The row will have a title, which is the artist name, and it will be a clickable link that refers to the "spotify" url.
* The row will visualize the timestamps as a series of semicircles. 
* The semi circles will alternate between facing up and down. Each semi circle will use 2 timestamps, i.e. from the list
`[t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11]`, semicircle 1 uses t0 and t1, semicircle 2 uses t1 and t2, etc.
* For each semicircle, the first coordinate will be it's x position. The second coordinate will be its diameter.
* Each semicircle will be filled, and the fill color will be configured via css.
* Because the maximum semicircle size will likely differ between rows, we will determine the max row height (highest downward facing semi circle + lowest upward facing semicircle) and set the height of each row to that value.
* The visualization portion of each row will start at the same x-coordinate on the page, so that all of the visualizations are right-aligned with each other. This means that the title field of each row will be left-aligned but have a fixed length (wide enough to acccomodate the longest title).
* The link color for the title field will be configured in css.

### Option
* There will be an on option controlled by a radio button: "scaled" or "unscaled". It will default to "scaled".
* When the `scaled` option is selected, the x-positions specified by the timestamps will be scaled to the range [0, max_row_length].
* When the `unscaled` option is selected, the x-positions specified by the timestamps will be scaled so that the largest timestamp is max_row_length.
* `max_row_length` will be a variable in the code, and will be initially set to 1000 pixels.

### Footnote
At the bottom of the page there will be a footnote referencing a github repository which will be configured in code, which will be the repository the code for this page lives in once it is complete.

## Resources:
https://www.rolf-musicblog.net/beethoven-string-quartet-op-127/


## Recordings:
Danish String Quartet: https://open.spotify.com/track/5UctLUMiMHqiXcNJ2P0SOz
Cleveland Quartet: https://open.spotify.com/track/3Ngfw9Yd07LiLT8HJ76MZo
Emerson String Quartet: https://open.spotify.com/track/2xDfdf75sdw3ravq3yHn5C
Quatour Mosaiques: https://open.spotify.com/track/0XLgzad9V95vt8xv4K9Bz4
Juilliard (1974): https://open.spotify.com/track/4id5sxDHfx2wfGMRB9rA0u 
Quatour Ebene: https://open.spotify.com/track/7dVaZGTvb07w4yDceKpU7L
Hagen Quartett: https://open.spotify.com/track/4id5sxDHfx2wfGMRB9rA0u
Busch: https://open.spotify.com/track/5iIIN3NjehQxe8tJJFdXrC
Takacs: https://open.spotify.com/track/413wTWB1iJhR981zP5Nj6j
Budapest: https://open.spotify.com/track/5l77JNEPlr0N6eggLhNTUF
Amadeus: https://open.spotify.com/track/3q9yYFqOr1lkfaGols1iDX
Guarneri: https://open.spotify.com/track/3BeHnvAOSctQaZjsg0Z7Vw
Italiano: https://open.spotify.com/track/67zrce391SaV9oiHlJHRrL
Endellion: https://open.spotify.com/track/6tJh37hakDTxhpAz6l78m6
LaSalle: https://open.spotify.com/track/6Q8v1qifgM8zIyBbie5MM4
Alban Berg: https://open.spotify.com/track/569PdPNQV5TfNFiJr26bcP
Leipziger: https://open.spotify.com/track/1Y5f531xEDf9Vw7qrTmBJp
Melos: https://open.spotify.com/track/2BT8QSnuJRg83b2k6YcikV
Artemis: https://open.spotify.com/track/0FOw1egXXVLkiaAyeSDLqp
Dover: https://open.spotify.com/track/75LfJDmws8DDRdN4Qyaa2i



rolf lists: 
- [] Amadeus Quartet (1963)
- [] Guarneri String Quartet (1969)
- [] Quartetto Italiano (1968)
- [x] Emerson String Quartet (1997)
- [] Endellion String Quartet (2008)
- [x] Busch Quartett (1936)
- [] LaSalle Quartet (1976)
- [] Alban Berg Quartett (1982)
- [] Leipziger Streichquartett (2001)
- [] Melos Quartett Stuttgart (1984)
- [x] Takács Quartet (2004)
- [] Artemis Quartet (2010)
- [x] Hagen Quartett (2004)

---
replace online fonts with offline

<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">



## Prompt 2 for visualization:
I've asked you to build a simple and elegant data visualization as a static web page that has the following files: 
1. index.html
4. score.png
5. times.json -- a list of dictionaries such as:
```
[
    {
        "artist": "Cleveland Quartet",
        "spotify": "https://open.spotify.com/track/3Ngfw9Yd07LiLT8HJ76MZo?si=2661a3c36d5c4de1", 
        "timestamps": [0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11],
        "track_length": "6:44",
    },
    {
        "artist": "Default",
        "spotify": "", 
        "timestamps": [0, 4, 5, 7, 8, 12, 13, 15, 16, 19, 20, 24],
        "track_length": "7:44",
    },
]
```
where t1 through t11 are float timestamps.

The static page will will reference times.json and visualize the data within using the latest version of d3.js.


the background color for the entire page will be configured with css.
The page will have the following elements, described below
1. Title: a large title element
2. Image: the image 'score.png' displayed at full width
3. Option: an option radio button (scaled | unscaled)
4. Rows: a series of rows, one for each dictionary in times.json, which is the meat of the visualization.
5. Footnote: a footnote linking to the github repository.

After some back and forth, you generated the attached index.html file. I'd like to make the following changes: 

0. I'd like to add sort options next to the "scaled | unscaled" radio button as a drop-down. The sort options should be: 
    * snippet length (value of last timestamp, t11), 
    * movement length (value of track_length), 
    * ensemble name (value of "artist") 
    * longest m6 (value of t11 - t10)
The default sort option should be ensemble name. When the drop-down is changed, the rows of the visualization will re-sort.
1. For each semicircle, I'd like to add a tooltip showing its duration in seconds.
2. I'd like to change the colors of the red semicircles according to their duration (longest is darkest, shortest is lightest)

Please make the changes as surgically as possible while maintaining elegant, idiomatic, readable code.
