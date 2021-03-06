# Lee-Way Wang
# 11 August 2020
# This file contains all of the functions needed to run the virtual assistant
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

import cv2
import os
import time
import speech_recognition as sr
import subprocess
import random

from datetime import datetime
from gtts import gTTS
from playsound import playsound


def imshow_fullscreen(window_name, image):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, image)


# Function shows a random image
def show_random_image():
    base_directory = os.path.dirname(os.path.abspath(__file__))  # Directory that this file is located in
    image_dictionary = {}  # Dictionary that holds a number and its corresponding image
    counter = 0
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith("png") or file.endswith("jpg") or file.endswith("JPG") or file.endswith("jpeg"):
                path_to_file = os.path.join(root, file)  # the path of the file
                image_dictionary[counter] = path_to_file
                counter += 1

    random_number = random.randint(0, counter-1)
    image = image_dictionary[random_number]
    image = cv2.imread(image)

    imshow_fullscreen("Image", image)
    cv2.waitKey(0)  # Closes the window once the user presses a key
    cv2.destroyAllWindows()

# Function returns the current time inside a string
def get_clock_time():
    current_time = datetime.now()
    if current_time.hour == 0:
        clock_time = "The time is " + str(12) + " " + str(current_time.minute) + " a.m."
    elif current_time.hour == 12:
        clock_time = "The time is " + str(12) + " " + str(current_time.minute) + " p.m."
    elif current_time.hour < 12:
        clock_time = "The time is " + str(current_time.hour) + " " + str(current_time.minute) + " a.m."
    else:
        clock_time = "The time is " + str(current_time.hour - 12) + " " + str(current_time.minute) + " p.m."
    return clock_time


# Function returns the current date inside a string
def get_calendar_date():

    month_conversions = {1: "January",
                         2: "February",
                         3: "March",
                         4: "April",
                         5: "May",
                         6: "June",
                         7: "July",
                         8: "August",
                         9: "September",
                         10: "October",
                         11: "November",
                         12: "December"
                         }
    current_time = datetime.now()

    calendar_date = "The date is " + str(current_time.day) + " " + month_conversions[
                current_time.month] + " " + str(current_time.year)
    return calendar_date


# Function counts down the number of seconds, based on minutes and seconds
# Returns a string signalling that the program has counted down to 0
def countdown(minute, sec):
    total_time = (60 * minute) + sec
    while total_time > 0:
        total_time -= 1
        time.sleep(1)
    return "Your timer is done. Your timer is done. Your timer is done."


# Creates a timer based on the converted speech. Returns the countdown function.
# Once the countdown function is done counting down, then it will return the the phrase: "Your timer is done..."
def set_timer(converted_speech, enable_text_input):
    try:
        min_and_sec = [int(i) for i in converted_speech.split() if i.isdigit()]
        spoken_phrase = "OK, setting timer for " + str(min_and_sec[0]) + " minutes and " + str(min_and_sec[1]) + " seconds"
        if enable_text_input:
            print(spoken_phrase)
        else:
            speak(spoken_phrase)
    except IndexError:
        spoken_phrase = "Unknown minutes or seconds. Please try again"
        return spoken_phrase

    # Returns a phrase, once the timer has counted down, signalling that the timer has counted down to 0
    return countdown(min_and_sec[0], min_and_sec[1])


# Creates a txt file based on a text input. txt file is named after the time at which it was created.
def create_note(text):
    date = datetime.now()

    # Name the txt file after the time of its creation
    file_name = str(date).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(text)

    subprocess.Popen(["notepad.exe", file_name])


# This function recognizes speech from a microphone. Converts the speech into text, and then returns that text
# If the speech was unrecognizable (perhaps there was too much ambient background noise), then the converted speech
# automatically becomes "Speech was unrecognizable. Please say again"
def convert_speech_to_text():
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)
    try:
        converted_speech = r.recognize_google(audio)
    except sr.UnknownValueError:
        converted_speech = "Speech was unrecognizable. Please say again"
    return converted_speech


# This function speaks out loud a certain input phrase
def speak(phrase):
    language = 'en'
    my_obj = gTTS(text=phrase, lang=language, slow=False)
    my_obj.save("output.mp3")  # Save the sound file of the speech
    playsound('output.mp3')  # Play the sound file
    os.remove("output.mp3")  # Remove the sound file. This is necessary, because otherwise an error is thrown

# Global variables. They need to be global because the chatbot must be trained before the program starts, for the
# user's convenience. These variables could be inside the talk_to_chatbot function, but that would cause a pause
# right in the middle of the user's interaction with the virtual assistant. It would be more user-friendly to load
# everything up front.
chatbot = ChatBot('Assistant')

# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot based on the english corpus
trainer.train("chatterbot.corpus.english")

# This function allows the user to talk to a chatbot using either their voice or through text input.
# The chatbot will use either text-to-speech or text to respond back to the user.
# As long as the input phrase does not contain any of the stop conversation keywords, then the chatbot conversation
# will keep going.
def talk_to_chatbot(enable_text_input):
    stop_conversation_keywords = ["farewell", "exit", "stop", "goodbye", "quit"]

    if enable_text_input:
        print("What would you like to talk about?")
    else:
        speak("What would you like to talk about?")

    while True:
        if enable_text_input:
            input_phrase = input("Type your response: ")
        else:
            input_phrase = convert_speech_to_text()
            print(input_phrase)

        if input_phrase != "Speech was unrecognizable. Please say again":
            # Need to explicitly turn the response into a string. Otherwise, an attribute error will be thrown
            if any(word in input_phrase for word in stop_conversation_keywords):
                break
            else:
                response = chatbot.get_response(input_phrase)
                if enable_text_input:
                    print("Chatbot: ", response)
                else:
                    speak(str(response))


def take_selfie():
    faceCascade = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_alt2.xml')
    eye_cascade = cv2.CascadeClassifier('cascades/data/haarcascade_eye.xml')

    video_capture = cv2.VideoCapture(0)  # Set video source to default webcam

    while True:

        # Capture frame-by-frame
        # Return code tells us if we've run out of frames, but this won't happen because we're using a webcam
        # Only applicable if using a video as the source
        ret, frame = video_capture.read()  # Read one frame of the webcam's video, store it as 2d list/array

        # Do everything I did before in the above code, except with 1 frame from the webcam
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert 1 frame from the webcam video into grayscale image

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5
        )

        eye_count = 0
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            ending_x_coordinate = x + w
            ending_y_coordinate = y + h
            roi_gray = gray[y:y + h, x:x + w]  # region of interest
            roi_color = frame[y:y + h, x:x + w]

            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, eh, ew) in eyes:

                if (ex + ew) < w and (ey + eh) < (h / 2):
                    eye_count += 1
                    cv2.rectangle(frame, (x, y), (ending_x_coordinate, ending_y_coordinate), (255, 0, 0), 2)

                    # if eye_count == 2:
                    #     date = datetime.now()
                    #     # Name the selfie image file after the time of its creation
                    #     img_file_name = str(date).replace(":", "-") + "-selfie.png"
                    #     # img_file_name = "selfie_image.png"
                    #     cv2.imwrite(img_file_name, roi_color)

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if (cv2.waitKey(1) & 0xFF == ord('q')) and eye_count == 2:  # Close the window once the user presses 'q'
            date = datetime.now()
            # Name the selfie image file after the time of its creation
            img_file_name = str(date).replace(":", "-") + "-selfie.png"
            # img_file_name = "selfie_image.png"
            cv2.imwrite(img_file_name, roi_color)
            break

    # When everything is done, release the capture
    video_capture.release()

    cv2.destroyAllWindows()
    root = r"C:\Users\leewa\PycharmProjects\Virtual_Assistant_Test_3"
    selfie_image = cv2.imread(os.path.join(root, img_file_name))
    cv2.imshow("Selfie image", selfie_image)
    cv2.waitKey(0)  # Closes the window once the user presses a key
    cv2.destroyAllWindows()


# This function executes the different voice commands that the user might give the virtual assistant.
# If the trigger phrase is in the converted speech, then the virtual assistant will activate
# Returns the virtual assistant's response
def execute_commands(converted_speech, enable_text_input):

    trigger_phrase = "assistant"

    # spoken_phrase = "Trigger phrase was not heard"
    spoken_phrase = "trigger phrase was not detected"

    if trigger_phrase in converted_speech:

        # Conditions for creating a note. If the program hears these words, then it will create a note
        create_note_phrases = ["note", "reminder", "write this down", "remember"]
        create_note_condition = any(word in converted_speech for word in create_note_phrases)

        # Conditions for opening Chrome. If the program hears these words, then it will create a note
        open_browser_phrases = ["chrome", "browser", "web"]
        open_browser_condition = any(word in converted_speech for word in open_browser_phrases)

        # Conditions for activating the chatbot. If the program hears these words, then it will create a note
        start_chat_bot_phrases = ["talk", "conversation", "chat", "discuss", "discussion"]
        start_chat_bot_condition = any(word in converted_speech for word in start_chat_bot_phrases)

        show_image_phrases = ["picture", "image", "photo"]
        show_image_condition = any(word in converted_speech for word in show_image_phrases)

        take_selfie_phrases = ["selfie"]
        take_selfie_condition = any(word in converted_speech for word in take_selfie_phrases)

        if "hello" in converted_speech:
            spoken_phrase = "Hello to you too"
        elif "your name" in converted_speech:
            spoken_phrase = "My name is Assistant, pleased to meet you."
        elif "joke" in converted_speech:
            spoken_phrase = "How do billboards talk? Sign language"
        elif "date" in converted_speech:
            spoken_phrase = get_calendar_date()
        elif "the time" in converted_speech:
            spoken_phrase = get_clock_time()
        elif "timer for" in converted_speech:
            spoken_phrase = set_timer(converted_speech, enable_text_input)
        elif start_chat_bot_condition:
            talk_to_chatbot(enable_text_input)
            spoken_phrase = "It was great talking to you"
        elif open_browser_condition:
            spoken_phrase = "Opening the Chrome web browser"
            # Open Google Chrome
            subprocess.call([r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'])
        elif show_image_condition:
            spoken_phrase = "Showing a random image"
            show_random_image()
        elif take_selfie_condition:
            spoken_phrase = "Opening camera. Press q to take a selfie."
            if enable_text_input:
                print(spoken_phrase)
            else:
                speak(spoken_phrase)
            spoken_phrase = "Selfie taken"
            take_selfie()
        elif create_note_condition:
            # Create a txt reminder in notepad
            if not enable_text_input:
                speak("what would you like me to write down?")
                note_text = convert_speech_to_text()
            else:
                print("what would you like me to write down?")
                note_text = input("Enter a note: ")

            create_note(note_text)
            spoken_phrase = "I've made a note of that"
        else:
            spoken_phrase = "I don't understand that command. Please say again."
    elif converted_speech == "speech was unrecognizable. please say again":
        spoken_phrase = converted_speech

    return spoken_phrase


def activate_virtual_assistant(enable_text_input):
    print("Start")

    # User can specify whether or not they want to use text input to control the virtual assistant
    # If converted_speech = "text input", then the user can input text. Otherwise, the user uses their voice to control
    # the program
    converted_speech = ""

    if enable_text_input:
        while "quit" not in converted_speech:
            print("Ready for a command")
            converted_speech = input("Enter a command: ")
            if "quit" not in converted_speech:
                print(execute_commands(converted_speech.lower(), True))

        print("Thank you for using this virtual assistant")

    else:
        while "quit" not in converted_speech:
            speak("Ready for a command")
            converted_speech = convert_speech_to_text()
            print(converted_speech)
            if "quit" not in converted_speech:
                speak(execute_commands(converted_speech.lower(), False))
        speak("Thank you for using this virtual assistant")