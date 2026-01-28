So this project is going to be a collection of scripts. The ultimate goal of the project is to use YT-DLP and FFmpeg to download videos from YouTube. I just need the audio files, not the entire video. That will be the task of YT-DLP, and FFmpeg will take on the task of cutting snippets of the audio files and creating copies

I'm going to roughly describe the features of the project.

I would like the script that handles downloading YouTube audio with YT-DLP to have the capability to ingest multiple URLs at once and process them all in a list. For each item in the list, if there is a failure to download, I would like YT-DLP to retry as many times as you feel makes sense.

I believe a CSV file makes sense for this. The CSV file should just have two columns:
1. First, the URL of the video to be downloaded
2. Third, the desired audio format of the file

When the yt-dlp command is run, everything else should just be the default flags. For example, the CSV file should not need to specify the title of the downloaded file, because the title should just be whatever title it extracts from the YouTube URL. 

So then that script will store all of the successfully downloaded audio files in a folder within this project.

Then I will also need a script that uses FFmpeg that takes in an audio file, and a CSV file (different than the previous CSV file). Each line inside of this CSV file will have two time-stamps: one indicating the beginning of the song and one indicating the end of the song, and also a title for the extracted song. They are essentially time-stamps. Here are the pairs, each represents a song that the user is trying to extract from the audio file. for additional context. The other part of this project is that I would like to extract songs from DJ mixes and such.

Finally, I just need you to make a script that uses FFMPEG to combine all audio files in a folder into a single file. I also need to be able to pass it the title of the new file. It should delete the originals in the source folder. 

By the way, I have already installed YT-DLP and FFmpeg on this computer. They are installed globally, so you should not have any trouble using them. The scripts should be able to just use them as if they were using them on the command line. 