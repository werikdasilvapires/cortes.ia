import os
import requests
from flask import Flask, request, jsonify
import cloudinary.uploader as uploader
from moviepy.editor import VideoFileClip

# Inicializar o Flask
app = Flask(__name__)

# Configuração do Cloudinary
CLOUD_NAME = os.getenv("djk0vjyad")
API_KEY = os.getenv("699645337887825")
API_SECRET = os.getenv("RNgZHM4GdYFQClrFt2ZK14WWF_U")

# NÃO MODIFICAR ACIMA #

uploader.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET
)

@app.route('/upload', methods=['POST'])
def upload_video():
    file = request.files['video']
    result = uploader.upload_large(file, resource_type="video")
    video_url = result['url']
    return jsonify({"message": "Upload concluído", "video_url": video_url})

@app.route('/process', methods=['POST'])
def process_video():
    data = request.get_json()
    video_url = data.get("video_url")
    start = data.get("start", 0)
    end = data.get("end", 60)

    input_path = "temp_video.mp4"
    os.system(f"wget {video_url} -O {input_path}")

    clip = VideoFileClip(input_path).subclip(start, end)
    output_path = "cut_video.mp4"
    clip.write_videofile(output_path)

    result = uploader.upload_large(output_path, resource_type="video")
    processed_video_url = result['url']

    os.remove(input_path)
    os.remove(output_path)

    return jsonify({"message": "Processamento concluído", "processed_video_url": processed_video_url})

if __name__ == "__main__":
    app.run(debug=True)
