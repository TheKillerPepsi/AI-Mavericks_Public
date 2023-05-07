import os
import azure.cognitiveservices.speech as speechsdk
import json
import json
import string
import openai
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import tkinter
#--------------OPENAI CONFIG--------------------
openai.api_type = "azure"
openai.api_base = "https://gpt-playground-us.openai.azure.com/"
openai.api_version = "2023-03-15-preview"
openai.api_key = "XXXXXXXX"
#--------------AZURE VOICE REC CONFIG-------------------------
speech_key = "XXXXXX"
speech_region = "eastus"
#--------------------NEEDED GLOBAL VARIABLES------------------------
global speechdata 
speechdata = "speech_recognition_output.json" #cleaned data from voice input
masterjson = "conversation.json" #master json
answ_chatgpt=""
assessment = "assessment.json" #needed for the data visualisation

def recognize_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
    speech_config.speech_recognition_language="en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(speech_recognition_result.text))
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and region values?")
    print(type(speech_recognition_result.text))
    with open('speech_recognition_output.json', 'w') as file:
        json.dump(speech_recognition_result.text, file)

def pre_processing():
# Load the JSON file
    with open('speech_recognition_output.json') as file:
        data = json.load(file)

# Tokenize the text
    tokens = nltk.word_tokenize(data)

# Remove stop words and punctuation, and turn all letters to lowercase
    stop_words = set(stopwords.words('english'))
    punctuations = set(string.punctuation)
    filtered_tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token not in punctuations]

# Join the tokens to form the cleaned text
    cleaned_text = ' '.join(filtered_tokens)

    with open('cleaned_text.json', 'w') as file:
        json.dump(cleaned_text, file)

def talk_to_chatgpt(masterjson):
    with open(masterjson) as json_file:
        data = json.load(json_file)

    response = openai.ChatCompletion.create(
        engine="chatgpt", # engine = "deployment_name".
     messages=data
    )
    global answ_chatgpt
    answ_chatgpt = (response['choices'][0]['message']['content'])
    print(answ_chatgpt)

    #add assessment file for visualization
    f = open(assessment, "w")
    f.write(answ_chatgpt)
    f.close()

def add_speech_to_json (speechdata, masterjson):
    with open(speechdata) as json_file:
        data = json.load(json_file)
    new_data = {"role": "user", "content": data}

    def write_json(new_data, masterjson):
        with open(masterjson,'r+') as file:
          # First we load existing data into a dict.
            file_data = json.load(file)
        # Join new_data with file_data inside emp_details
            file_data.append(new_data)
        # Sets file's current position at offset.
            file.seek(0)
        # convert back to json.
            json.dump(file_data, file, indent = 4)
     
    write_json(new_data, masterjson)

def add_answ_chatgpt_masterjson(answ_chatgpt):
    new_data = {"role": "assistant", "content": answ_chatgpt}
    with open(masterjson,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data.append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

def doing_some_math():

    #Parse the data BUT without the cleaning!
    with open('assessment.json') as user_file:
        data = user_file.read()
    
    parsed_data = json.loads(data)
    
# Extract the scalar values and store them in a dictionary
    scalar_data = {}
    for key in parsed_data:
        print(key)
        if key != "Tips":
            scalar_data[key] = int(parsed_data[key])

# Create a bar chart for the scalar values
    fig, ax = plt.subplots()
    ax.bar(scalar_data.keys(), scalar_data.values())
    ax.set_ylim(0, 10)
    ax.set_ylabel('Score')
    ax.set_title('Performance Ratings')
    plt.show()

# Print the list of tips
    print("Tips:")
    for tip in parsed_data["Tips"]:
        print("- " + tip)


#------------LETS START WITH THE ACTUAL WORK! :)-------------------
recognize_from_microphone()
print("Lets start with the Pre-Processing!")
pre_processing()
add_speech_to_json(speechdata, masterjson)
print("Unserinput added to masterjson")
talk_to_chatgpt(masterjson)
add_answ_chatgpt_masterjson(answ_chatgpt)
print("CGPTinput added to masterjson")
tkinter.messagebox.askquestion(title=None, message=answ_chatgpt)
#doing_some_math()