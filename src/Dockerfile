FROM python
RUN apt-get update
RUN pip install boto3
RUN pip install moviepy
RUN pip install requests
RUN pip install resources
RUN pip install imageio-ffmpeg
RUN apt-get -y install ffmpeg imagemagick
RUN cat /etc/ImageMagick-6/policy.xml
WORKDIR /app
COPY translatevideo.py, audioUtils.py, concatenateVideos.py, srt.py, srtUtils.py, transcribeUtils.py, videoUtils.py /app/
CMD [python translatevideo.py -region us-east-1 -inbucket awscloudproject2020/ 
-infile AlphabetAerobics.mp4 -outbucket awscloudproject2020/ -outfilename subtitledVideo -outfiletype mp4 -outlang es]