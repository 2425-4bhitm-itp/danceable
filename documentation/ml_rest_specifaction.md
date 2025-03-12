# ML expected REST routes


### 

Request:
```
POST http://ml:5001/spectrograms

{
    "snippetLocation": "xyz.wav"
    "tags":
        [
            "chacha",
            "rumba"
        ]
}
```

Response:
```
{
    "spectrogramLocation": "spectrogram-locationl.png"
}
```