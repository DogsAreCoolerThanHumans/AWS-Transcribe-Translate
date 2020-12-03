import json
import boto3
import re
import codecs
import time
import math
from audioUtils import *


def newPhrase():
	return { 'start_time': '', 'end_time': '', 'words' : [] }


# Format and return a string that contains the converted number of seconds into SRT format
def getTimeCode(seconds):
    (frac, whole) = math.modf(seconds)
    frac = frac * 1000
    return str('%s,%03d' % (time.strftime('%H:%M:%S',time.gmtime(whole)), frac))


def writeTranscriptToSRT( transcript, sourceLangCode, targetLangCode, srtFileName, region):
	# Write the SRT file for the original language
	print( "==> Creating SRT from transcript")
	phrases = getPhrasesFromTranscript( transcript )
	outputFile = codecs.open(srtFileName,"w+", "utf-8")
	for index, phrase in enumerate(phrases):
		translation = translatePhrase(phrase,sourceLangCode, targetLangCode, region)
		translatedPhrase = newPhrase()
		translatedPhrase['start_time'] = phrase['start_time']
		translatedPhrase['end_time'] = phrase['end_time'] 
		translatedPhrase['words'] = translation
		writePhraseToSRT( translatedPhrase, outputFile, index+1 )
	outputFile.close()

def writePhraseToSRT(phrase, outputFile, index):
	# determine how many words are in the phrase
	length = len(phrase["words"])
	
	# write out the phrase number
	outputFile.write( str(index) + "\n" )
	
	# write out the start and end time
	outputFile.write( phrase["start_time"] + " --> " + phrase["end_time"] + "\n" )
	out = phrase["words"]

	# write out the srt file
	outputFile.write(out + "\n\n" )
	

def translatePhrase(phrase, sourceLangCode, targetLangCode, region):
	#set up the Amazon Translate client
	translate = boto3.client(service_name='translate')
	words = phrase["words"]
	text = ""
	for word in words:
		text = text + " " + word

	translation = translate.translate_text(Text=text,SourceLanguageCode=sourceLangCode, TargetLanguageCode=targetLangCode)
	translatedText = translation["TranslatedText"]
	print (translatedText)
	return translatedText
	
def writeTranslationToSRT( transcript, sourceLangCode, targetLangCode, srtFileName, region ):
	# First get the translation
	print( "\n\n==> Translating from " + sourceLangCode + " to " + targetLangCode )
	translation = translateTranscript( transcript, sourceLangCode, targetLangCode, region )
		
	# Now create phrases from the translation
	textToTranslate = str(translation["TranslatedText"])
	phrases = getPhrasesFromTranslation( textToTranslate, targetLangCode )
	writeSRT( phrases, srtFileName )

def getPhrasesFromTranslation( translation, targetLangCode ):
	# Now create phrases from the translation
	words = translation.split()
	
	#set up some variables for the first pass
	phrase =  newPhrase()
	phrases = []
	nPhrase = True
	x = 0
	c = 0
	seconds = 0

	print("==> Creating phrases from translation...")

	for word in words:

		# if it is a new phrase, then get the start_time of the first item
		if nPhrase == True:
			phrase["start_time"] = getTimeCode( seconds )
			nPhrase = False
			c += 1
				
		# Append the word to the phrase...
		phrase["words"].append(word)
		x += 1
		
		
		if x == 10:
		
			# For Translations, we now need to calculate the end time for the phrase
			psecs = getSecondsFromTranslation( getPhraseText( phrase), targetLangCode, "phraseAudio" + str(c) + ".mp3" ) 
			seconds += psecs
			phrase["end_time"] = getTimeCode( seconds )
		
			#print c, phrase
			phrases.append(phrase)
			phrase = newPhrase()
			nPhrase = True
			#seconds += .001
			x = 0
			
		if c == 30:
			break
			
	return phrases
	

def getPhrasesFromTranscript( transcript ):
	ts = json.loads( transcript )
	items = ts['results']['items']
	phrase =  newPhrase()
	phrases = []
	nPhrase = True
	x = 0
	c = 0
	lastEndTime = ""

	print("==> Creating phrases from transcript...")

	for item in items:
		# if it is a new phrase, then get the start_time of the first item
		if nPhrase == True:
			if item["type"] == "pronunciation":
				phrase["start_time"] = getTimeCode( float(item["start_time"]) )
				nPhrase = False
				lastEndTime =  getTimeCode( float(item["end_time"]) )
			c+= 1
		else:	
			if item["type"] == "pronunciation":
				phrase["end_time"] = getTimeCode( float(item["end_time"]) )
				
		# in either case, append the word to the phrase...
		phrase["words"].append(item['alternatives'][0]["content"])
		x += 1
		
		# now add the phrase to the phrases, generate a new phrase, etc.
		if x == 10:
			#print c, phrase
			phrases.append(phrase)
			phrase = newPhrase()
			nPhrase = True
			x = 0
	
	# if there are any words in the final phrase add to phrases  
	if(len(phrase["words"]) > 0):
		if phrase['end_time'] == '':
            		phrase['end_time'] = lastEndTime
		phrases.append(phrase)	
				
	return phrases
	

def translateTranscript( transcript, sourceLangCode, targetLangCode, region ):
	ts = json.loads( transcript )
	txt = ts["results"]["transcripts"][0]["transcript"]
	translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)
	translation = translate.translate_text(Text=txt,SourceLanguageCode=sourceLangCode, TargetLanguageCode=targetLangCode)
	
	return translation
	

def writeSRT( phrases, filename ):
	print ("==> Writing phrases to disk...")

	# open the files
	e = codecs.open(filename,"w+", "utf-8")
	x = 1
	
	for phrase in phrases:
		length = len(phrase["words"])
		e.write( str(x) + "\n" )
		x += 1
		e.write( phrase["start_time"] + " --> " + phrase["end_time"] + "\n" )
		out = getPhraseText( phrase )
		e.write(out + "\n\n" )
		
	e.close()
	

def getPhraseText( phrase ):
	length = len(phrase["words"])
		
	out = ""
	for i in range( 0, length ):
		if re.match( '[a-zA-Z0-9]', phrase["words"][i]):
			if i > 0:
				out += " " + phrase["words"][i]
			else:
				out += phrase["words"][i]
		else:
			out += phrase["words"][i]
			
	return out
	