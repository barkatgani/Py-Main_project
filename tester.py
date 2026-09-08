import speech_recognition as sr
import webbrowser
import pyttsx3
import music
import requests

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

newsapi= "0f3ff6edfe264e208d06306ea6b9aa18"
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

        r = requests.get( "https://newsapi.org/v2/top-headlines?country=us&apiKey=0f3ff6edfe264e208d06306ea6b9aa18" )


        data = r.json()

        if data["status"] == "ok":
           titles = [article["title"] for article in data["articles"][:5]]

           speak("\nLatest News:")
        for i, title in enumerate(titles, 1):
             speak(f"{i}. {title}")
    #else:
        #let openai to decide what to do 
        

if __name__ == "__main__":
    speak("initializing jarvis....")
    #listen for wake word jarvis
    #obtain audio from the microphone
    while True:
        recognizer = sr.Recognizer()
        print("recognizing...")

        try:
          with sr.Microphone() as source:
              print("Listening for wake word...")
              audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
              command = recognizer.recognize_google(audio)
          if command.lower() == "jarvis":
              speak("Yes, how can I assist you?")
            
              #listen commands after wake word
              with sr.Microphone() as source:
                  print("jarvis is active ...")
                  audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                  command = recognizer.recognize_google(audio)
                  processcommand(command)

        except Exception as e:
            print("Error:", format(e))