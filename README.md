# audio_conversion
This Python script automates audio file conversion within a directory (specifically where this script is located) using FFmpeg. It iterates through specified audio files and converts them to a new format.

By default the script will keep the original files.
You will need to explicitly specify the `-d` flag to delete the original files.

## Example usage
The first argument specifies the source extension, while the second specifies the desired extension. No dot is needed in the extension names.
```shell
convert.py webm mp3 # converts all .webm files to .mp3. .webm files will be kept.

convert.py avi mp4 # converts all .avi files to .mp4.

convert.py -d mp3 webm # convert all mp3 files to webm, deleting the original files.
```

## Dependencies
- Python 3.7 and above
- [FFmpeg](https://ffmpeg.org/download.html)
- [Rich](https://github.com/willmcgugan/rich)

## Contribution
I'm using this for my personal use, so do whatever you want with it.
If you have any suggestions or improvements or found a bug, let me know.
