# audio_conversion
This is a Python script that converts audio files in a directory via FFmpeg.

By default, it deletes the original files after conversion.
Use the `-k` flag to keep the original files.

## Example usage
The first argument specifies the source extension, while the second specifies the desired extension.
```shell
convert.py webm mp3    # converts all .webm files to .mp3.

convert.py avi mp4     # converts all .avi files to .mp4.

convert.py -k mp3 webm # convert all mp3 files to webm while keeping the original files.
```

## Contribution
You can help me fix any bugs. I'd be glad.
