import speech_recognition as sr
import webbrowser
import pyttsx3
import music
import requests
import pandas as pd
import os
from dotenv import load_dotenv

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

    load_dotenv()

    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
def processcommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://www.google.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://www.youtube.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://www.facebook.com")
    elif "open twitter" in c.lower():
        webbrowser.open("https://www.twitter.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://www.linkedin.com")
    elif c.lower().startswith("play"):
        video = c.lower().split(" ")[1]
        link = music.music[video]
        webbrowser.open(link)
    elif "news" in c.lower():

        r = requests.get("https://newsapi.org/v2/top-headlines",
           params={
             "country": "in",
             "apiKey": NEWS_API_KEY} )
        
        data = r.json()

        if data["status"] == "ok":
           titles = [article["title"] for article in data["articles"][:5]]

           speak("\nLatest News:")
        for i, title in enumerate(titles, 1):
             speak(f"{i}. {title}")
    #else:
        #let openai to decide what to do 
    else:
        import pandas as pd

        df = pd.read_csv("dataset_tk..2.csv")

        state = c.lower().replace("power demand", "").replace("in", "").strip()

    # Match state column
        state_col = next((col for col in df.columns if col.lower() == state),
          None)

        if state_col:
            demand = df[state_col].dropna().iloc[-1]
            speak(f"Power demand in {state_col} is {demand:.2f} kilowatts.")
        else:
            speak(f"I could not find power demand data for {state}.")

if __name__ == "__main__":
    speak("jarvis is ready.")
    #listen for wake word jarvis
    #obtain audio from the microphone
    while True:
        recognizer = sr.Recognizer()
        print("Listening for wake word....")

        try:
          with sr.Microphone() as source:
              print("Listening for wake word...")
              audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
              command = recognizer.recognize_google(audio)
          if "jarvis" in command.lower() or "soli" in command.lower():
              speak("Yes, how can I assist you?")
            
            
              #listen commands after wake word
              with sr.Microphone() as source:
                  print("jarvis is active ...")
                  audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                  command = recognizer.recognize_google(audio)
                  processcommand(command)

        except Exception as e:
            print("Error:", format(e))