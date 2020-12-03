import argparse
from transcribeUtils import *
from srtUtils import *
import time
import uuid
from videoUtils import *
from audioUtils import *

# Get the command line arguments and parse them
parser = argparse.ArgumentParser( prog='translatevideo.py', description='Process a video found in the input file, process it, and write tit out to the output file')
parser.add_argument('-region', required=True, help="The AWS region containing the S3 buckets" )
parser.add_argument('-inbucket', required=True, help='The S3 bucket containing the input file')
parser.add_argument('-infile', required=True, help='The input file to process')
parser.add_argument('-outbucket', required=True, help='The S3 bucket containing the input file')
parser.add_argument('-outfilename', required=True, help='The file name without the extension')
parser.add_argument('-outfiletype', required=True, help='The output file type.  E.g. mp4, mov')
parser.add_argument('-outlang', required=True, nargs='+', help='The language codes for the desired output.  E.g. en = English, de = German')		
args = parser.parse_args()

# print out parameters and key header information for the user
print( "==> translatevideo.py:\n")
print( "==> Parameters: ")
print("\tInput bucket/object: " + args.inbucket + args.infile )
print( "\tOutput bucket/object: " + args.outbucket + args.outfilename + "." + args.outfiletype )

print( "\n==> Target Language Translation Output: " )

for lang in args.outlang:
	print( "\t" + args.outbucket + args.outfilename + "-" + lang + "." + args.outfiletype)
	
	
client = boto3.client('s3')
transcribe = boto3.client('transcribe')
bucket = 'awscloudproject2020'

def transcribeVideo(inputVideo):
	job_name="transcribe_" + uuid.uuid4().hex + '_' + args.infile + ".mp4"
	#mediaUri = "https://s3-us-east-1.amazonaws.com/awscloudproject2020/AlphabetAerobics.mp4" 
	mediaUri = "https://" + "s3-us-east-1.amazonaws.com/" + bucket + "/" + args.infile
	#s3://awscloudproject2020/AlphabetAerobics.mp4
	response = transcribe.start_transcription_job(
	 	TranscriptionJobName= job_name,
	    Media={'MediaFileUri': mediaUri},
	    MediaFormat='mp4',
	    LanguageCode= "en-US"
	)
	return response

download_path = 'AlphabetAerobics.mp4'
outputname = 'sub-' + args.infile


response = transcribeVideo('AlphabetAerobics.mp4')
while( response["TranscriptionJob"]["TranscriptionJobStatus"] == "IN_PROGRESS"):
	print( "."),
	time.sleep( 30 )
	response = getTranscriptionJobStatus( response["TranscriptionJob"]["TranscriptionJobName"] )
response = getTranscriptionJobStatus( response["TranscriptionJob"]["TranscriptionJobName"] )
transcript = getTranscript( str(response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]) )
#writeTranscriptToSRT( transcript, single_audio_lang, subtitle_lang, "subtitles.srt",'us-east-1'  )
writeTranscriptToSRT( transcript, 'en', 'es', "subtitles-es.srt",'us-east-1'  )
createVideo(download_path, 'subtitles-es.srt', outputname)
print('outputname:')
print(outputname)
client.upload_file(outputname, bucket, outputname)

#createVideo( args.infile, "subtitles-en.srt", args.outfilename + "-en." + args.outfiletype, "audio-en.mp3", True)