# audio_conversion
This Python script automates audio file conversion within a directory (where this file is located) using FFmpeg. It iterates through specified audio files and converts them to a new format.

By default, the original files are deleted after conversion.  
If you want to keep the originals, use the `-k` flag when running the script.

## Example usage
The first argument specifies the source extension, while the second specifies the desired extension. No dot is needed in the extension names.
```shell
convert.py webm mp3    # converts all .webm files to .mp3.

convert.py avi mp4     # converts all .avi files to .mp4.

convert.py -k mp3 webm # convert all mp3 files to webm, keeping the original files.
```

## Dependencies
- Python 3.7 and above
- [FFmpeg](https://ffmpeg.org/download.html)
- [Rich](https://github.com/willmcgugan/rich)

## Contribution
I'm using this for my personal use, so do whatever you want with it.
If you have any suggestions or improvements or found a bug, feel free to open an issue or a pull request.
