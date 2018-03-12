import requests
import argparse
import os

#This method will grab the result or indicate if the result is still in process
#when using the -f argument.  The operation that is passed as the argument to
#this method is provided by the tName.txt file that is generated when
#submitting a transcription request
#This method produces two files, one with transcription and one with word times
#in the same directory as this application.
def fetch(operation):
    transcriptionResponse = requests.get("https://speech.googleapis.com/v1/operations/" + operation + "?key=AIzaSyBh3tZXSWXq6l2W_yg4eWEn0fW8P_mIaC8")
    
    stringToFile = ""
    try:
        for transcript in transcriptionResponse.json()["response"]["results"]:
            stringToFile += transcript["alternatives"][0]["transcript"] + "."
            
        
        file = open(operation + "_transcript.txt", 'w')
        file.write(stringToFile)
        file.close()
        
        stringToFile = ""
        
        for result in transcriptionResponse.json()["response"]["results"]:
            for words in result["alternatives"][0]["words"]:
                stringToFile += "Start_Time," + words["startTime"] + ',End_Time,' + words["endTime"] + ",Word," + words["word"] + "\n"
                
        file = open(operation + "_wordTimes.csv", 'w')
        file.write(stringToFile)
        file.close()
        #This will get the transcription.  Not the name of the operation
        if open(operation + "_transcript.txt", 'r'):
            print("Looks like everything went well.  Check the directory of this application for " 
                  + operation +"_transcript.txt  and " + operation + "._wordTimes.csv")
        else:
            print("Something went wrong.  The transcript file couldn't be opened.  Either it doesn't exist"
                  + " or it is something else.")
    except:
        print("The request must still be processing.  The details are below. \n\n")
        print(transcriptionResponse.text)

#This method submits the transcription request when using the -t argument.
#The api_key is supplied by the Speech.key file, the URI is supplied
#by the -t argument and the URI must come from the Google Cloud Storage and 
#the file must be a WAV file.
#The timing is enabled by default but can be set to False using "-gt False"
# appended to the -t command.
def transcribe(uri, api_key, getTimes = True):
    
    #The sample hertz can only be obtained from the metadata via the URI if
    # the link is set to public in the Bucket in the google cloud console.
    jsonConfig = {
                  "config": {
                      "encoding": "LINEAR16",
                      #"sampleRateHertz": 16000,
                      "languageCode": "en-US",
                      "enableWordTimeOffsets": getTimes
                  },
                  "audio": {
                      "uri": uri
                  }
            }

    r = requests.post("https://speech.googleapis.com/v1/speech:longrunningrecognize?key=" + api_key, json=jsonConfig)
    
    if os.path.isfile("tName.txt"):
        with open("tName.txt", 'w') as file:
            file.write(r.json()["name"])
            file.close()
    else:
        file = open("tName.txt", 'w')
        file.write(r.json()["name"])
        file.close()
            
    print(r.json()["name"])
    
if os.path.isfile("speech.key"):
    print("Speech Key found")
    file = open("speech.key", 'r')
    speechKey = file.read()
    file.close()
else:
    print("A speech enabled API key is required to transcribe speech.")
   
########### Argument Parser without using the Sys Args for cleaner parsing ######    
parser = argparse.ArgumentParser(description="Transcribes files using Google's Speech API.")

parser.add_argument("-sk", "--speech_key", help="This is the API key needed for Speech")
parser.add_argument("-t", "--transcribe", help="Give a URI to transcribe")
parser.add_argument("-gt", "--get_times", type=bool, help="Give a URI to transcribe")
parser.add_argument("-f", "--fetch", help= "This will grab the operations that are have been in process", action="store_true")
args = parser.parse_args()
    
if args.speech_key:
    file = open("speech.key", 'w')
    file.write(args.speech_key)
    file.close()
    print("Key saved.")
    
if args.transcribe:
    if args.get_times is None:
        transcribe(args.transcribe, speechKey)
    else:
        transcribe(args.transcribe, speechKey, args.get_times)
        
if args.fetch:
    if os.path.isfile("tName.txt"):
        file = open("tName.txt", 'r')
        operation = file.read()
        file.close()
        fetch(operation)
        
    else:
        print("There are no operations available")
        
########### Argument Parser without using the Sys Args for cleaner parsing ######  
    






