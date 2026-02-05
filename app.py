import os, subprocess
from datetime import timedelta
from pytubefix import YouTube
from pytubefix.cli import on_progress
from flask import Flask, render_template, request, send_from_directory, send_file


static_folder = "static/"
app = Flask(__name__, template_folder="templates/", static_folder=None)

videos_output_folder = "downloads/videos/"
audios_output_folder = "downloads/audios/"
final_files_output_folder = "downloads/final_files/"
download_folders = [
    videos_output_folder,
    audios_output_folder,
    final_files_output_folder
]

for folder in download_folders:
    os.makedirs(folder, exist_ok=True)


@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")


@app.route("/video", methods=['GET', 'POST'])
def show_video():
    video_url = request.form['input_url']
    video_info = {"Url": video_url}

    try:
        yt_video = YouTube(video_url, on_progress_callback=on_progress)
    except:
        return "Internal Server Error!!", 500 
    
    video_info["Título"] = yt_video.title
    video_info["Autor"] = yt_video.author
    video_info["Duración"] = str(timedelta(seconds=yt_video.length)) # Convert seconds to hours, minutes and seconds format
    video_info["Fecha de publicación"] = yt_video.publish_date

    resolution_list =[]
    for stream in yt_video.streams.filter(adaptive=True, only_video=True, video_codec="vp9"):
        resolution_list.append(stream.resolution)

    return render_template("video_preview.html", video_info=video_info, thumbnail_url=yt_video.thumbnail_url, resolution_list=resolution_list)

@app.route("/download", methods=['GET'])
def download_video():
    resolution = request.args.get("resolution")
    yt_video = YouTube(request.args.get("video_url"), on_progress_callback=on_progress)

    video_stream = (
        yt_video.streams
        .filter(
            adaptive=True,
            only_video=True,
            video_codec="vp9",
            res=resolution
        ).first()
    )

    audio_stream = (
        yt_video.streams
        .filter(
            adaptive=True,
            only_audio=True
        ).first()
    )

    if video_stream and audio_stream:
        filename = yt_video.title + "_" + resolution
        
        video_path = videos_output_folder + filename + ".webm"
        if not os.path.isfile(video_path):
            video_stream.download(
                output_path=videos_output_folder, 
                filename=filename + ".webm"
            )
        audio_path = audios_output_folder + filename + ".m4a"
        if not os.path.isfile(audio_path):
            audio_stream.download(
                output_path=audios_output_folder,
                filename=filename + ".m4a"
            )

        final_path = final_files_output_folder + filename + ".mp4"
        if not os.path.isfile(final_path):
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", os.path.abspath(video_path),
                "-i", os.path.abspath(audio_path),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-filter:a", "loudnorm",
                "-strict", "experimental",
                "-threads", "6", # (CPU threads / 2) --> 50% CPU usage
                os.path.abspath(final_path)
            ]

            subprocess.run(ffmpeg_cmd, check=True)

        try:
            os.remove(video_path)
        except OSError:
            pass

        try:
            os.remove(audio_path)
        except OSError:
            pass

        return send_file(final_path, as_attachment=True)
    else:
        print("Video couldnt be downloaded!!")
        return "Internal Server Error!!", 500


@app.route('/static/<path:filename>', methods=['GET'])
def custom_static(filename):
    full_path = os.path.join(static_folder, filename)
    if os.path.isfile(full_path):
        return send_from_directory(static_folder, filename)
    
    return "Internal Server Error!!", 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
