import datetime
import os
import urllib.parse
import webbrowser

import pandas as pd
import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

ASSISTANT_NAME = "Solai"
WAKE_WORDS = ["solai"]
ENERGY_DATA_PATH = os.getenv("ENERGY_DATA_PATH", "dataset_tk.csv")
POWER_COLUMN = os.getenv("POWER_COLUMN", "Punjab")
SOLAR_COLUMN = os.getenv("SOLAR_COLUMN", "solar_generation")


# --------------------------------------------------
# Initialize speech tools
# --------------------------------------------------

recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)


# --------------------------------------------------
# Text-to-speech
# --------------------------------------------------

def speak(text):
    """Print and speak a response locally using pyttsx3."""
    print(f"{ASSISTANT_NAME}: {text}")

    try:
        engine.say(str(text))
        engine.runAndWait()
    except Exception as error:
        print(f"Speech error: {error}")


# --------------------------------------------------
# Energy-data functions
# --------------------------------------------------

def load_energy_data():
    """Load the energy CSV and return a DataFrame."""
    try:
        if not os.path.exists(ENERGY_DATA_PATH):
            print(f"Data file not found: {ENERGY_DATA_PATH}")
            return None

        data = pd.read_csv(ENERGY_DATA_PATH)

        if data.empty:
            print("The energy CSV is empty.")
            return None

        return data

    except Exception as error:
        print(f"Could not load energy data: {error}")
        return None


def get_latest_row():
    """Return the last row from the energy dataset."""
    data = load_energy_data()

    if data is None:
        return None

    return data.iloc[-1]


def get_power_demand():
    """Speak the latest power demand."""
    latest = get_latest_row()

    if latest is None:
        speak("I could not load the energy data.")
        return

    if POWER_COLUMN not in latest.index:
        speak(
            f"I could not find the power column named {POWER_COLUMN} "
            "in the CSV file."
        )
        print("Available columns:", list(latest.index))
        return

    try:
        power = float(latest[POWER_COLUMN])
        speak(
            f"The latest recorded power demand for Punjab is "
            f"{power:.2f} megawatts."
        )
    except (TypeError, ValueError):
        speak("The power-demand value is not a valid number.")


def get_solar_generation():
    """Speak the latest solar-generation value."""
    latest = get_latest_row()

    if latest is None:
        speak("I could not load the energy data.")
        return

    # Accept several common solar-column names.
    possible_columns = [
        SOLAR_COLUMN,
        "solar_generation_kw",
        "solar_generation_mw",
        "solar",
        "Solar",
        "Solar Generation",
    ]

    solar_column = next(
        (column for column in possible_columns if column in latest.index),
        None,
    )

    if solar_column is None:
        speak(
            "I could not find a solar-generation column in the CSV file. "
            "Add a column named solar_generation."
        )
        print("Available columns:", list(latest.index))
        return

    try:
        solar = float(latest[solar_column])
        speak(f"The latest solar generation is {solar:.2f} megawatts.")
    except (TypeError, ValueError):
        speak("The solar-generation value is not a valid number.")


def check_anomaly_status():
    """Detect unusual power values using a two-standard-deviation rule."""
    data = load_energy_data()

    if data is None:
        speak("I could not load the energy data.")
        return

    if POWER_COLUMN not in data.columns:
        speak(f"I could not find the {POWER_COLUMN} column in the CSV file.")
        print("Available columns:", list(data.columns))
        return

    try:
        values = pd.to_numeric(data[POWER_COLUMN], errors="coerce").dropna()

        if values.empty:
            speak("There are no valid power readings to analyze.")
            return

        mean_power = values.mean()
        standard_deviation = values.std()

        # If there is only one value, standard deviation may be NaN.
        if pd.isna(standard_deviation) or standard_deviation == 0:
            speak("There are not enough different readings to detect anomalies.")
            return

        upper_limit = mean_power + (2 * standard_deviation)
        lower_limit = mean_power - (2 * standard_deviation)

        anomalies = values[
            (values > upper_limit) | (values < lower_limit)
        ]

        abnormal_count = len(anomalies)

        if abnormal_count:
            speak(
                f"Warning. I detected {abnormal_count} unusual "
                "power reading or readings in the dataset."
            )
        else:
            speak("No significant power anomalies were detected.")

    except Exception as error:
        print(f"Anomaly error: {error}")
        speak("Sorry, I could not check the anomaly status.")


def get_electrical_readings():
    """Read common electrical columns if they exist."""
    latest = get_latest_row()

    if latest is None:
        speak("I could not load the energy data.")
        return

    possible_columns = {
        "voltage": ["voltage_v", "voltage", "Voltage"],
        "current": ["current_a", "current", "Current"],
        "frequency": ["frequency_hz", "frequency", "Frequency"],
    }

    readings = {}

    for label, columns in possible_columns.items():
        selected_column = next(
            (column for column in columns if column in latest.index),
            None,
        )

        if selected_column is not None:
            try:
                readings[label] = float(latest[selected_column])
            except (TypeError, ValueError):
                pass

    if not readings:
        speak(
            "I could not find voltage, current, or frequency columns "
            "in the CSV file."
        )
        print("Available columns:", list(latest.index))
        return

    response_parts = []

    if "voltage" in readings:
        response_parts.append(f"voltage is {readings['voltage']:.2f} volts")

    if "current" in readings:
        response_parts.append(f"current is {readings['current']:.2f} amperes")

    if "frequency" in readings:
        response_parts.append(
            f"frequency is {readings['frequency']:.2f} hertz"
        )

    speak("The latest readings are " + ", ".join(response_parts) + ".")


# --------------------------------------------------
# General commands
# --------------------------------------------------

def open_site(url, site_name):
    webbrowser.open(url)
    speak(f"Opening {site_name}.")


def search_google(command):
    query = command

    for phrase in ["search google for", "search for", "google"]:
        if query.startswith(phrase):
            query = query.replace(phrase, "", 1).strip()
            break

    if not query:
        speak("What would you like me to search for?")
        return

    url = "https://www.google.com/search?q=" + urllib.parse.quote(query)
    webbrowser.open(url)
    speak(f"Searching Google for {query}.")


def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    speak(f"The time is {current_time}.")


def tell_date():
    current_date = datetime.datetime.now().strftime("%A, %d %B %Y")
    speak(f"Today is {current_date}.")


# --------------------------------------------------
# Command processing
# --------------------------------------------------

def process_command(command):
    """Process a recognized command. Return False to stop the program."""
    command = command.lower().strip()

    if command in {"stop", "exit", "quit", "goodbye", "shutdown"}:
        speak("Goodbye.")
        return False

    if "power demand" in command or "electricity demand" in command:
        get_power_demand()
        return True

    if "solar generation" in command or "solar output" in command:
        get_solar_generation()
        return True

    if "anomaly status" in command or "check anomalies" in command:
        check_anomaly_status()
        return True

    if (
        "electrical reading" in command
        or "electrical readings" in command
        or "voltage" in command
        or "current" in command
        or "frequency" in command
    ):
        get_electrical_readings()
        return True

    if command.startswith("search") or command.startswith("google"):
        search_google(command)
        return True

    if "open google" in command:
        open_site("https://www.google.com", "Google")
        return True

    if "open youtube" in command:
        open_site("https://www.youtube.com", "YouTube")
        return True

    if "open linkedin" in command:
        open_site("https://www.linkedin.com", "LinkedIn")
        return True

    if "what time" in command or "tell me the time" in command:
        tell_time()
        return True

    if "what date" in command or "today's date" in command:
        tell_date()
        return True

    speak("Sorry, I do not understand that command yet.")
    return True


# --------------------------------------------------
# Speech recognition
# --------------------------------------------------

def listen(recognizer_object, microphone, timeout, phrase_time_limit):
    """Listen once and return recognized lowercase text."""

    try:
        with microphone as source:
            print("Listening now. Please speak clearly...")

            audio = recognizer_object.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        print("Processing speech...")

        text = recognizer_object.recognize_google(
            audio,
            language="en-IN"
        )

        print(f"Heard: {text}")
        return text.lower().strip()

    except sr.WaitTimeoutError:
        print("No speech detected before timeout.")

    except sr.UnknownValueError:
        print(
            "Audio was recorded, but speech was not understood. "
            "Speak closer to the microphone."
        )

    except sr.RequestError as error:
        print(f"Google Speech Recognition error: {error}")
        speak("The speech recognition service is unavailable.")

    except Exception as error:
        print(f"Listening error: {error}")

    return ""



# --------------------------------------------------
# Main program
# --------------------------------------------------

def main():
    microphone = sr.Microphone()

    speak("Initializing Solai energy monitoring assistant.")

    try:
        with microphone as source:
            print("Adjusting microphone for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
    except Exception as error:
        print(f"Microphone setup error: {error}")
        speak("I could not access the microphone.")
        return

    print(f"{ASSISTANT_NAME} is ready.")
    speak("I am ready.")

    while True:
        print("Waiting for wake word...")

        wake_word = listen(
            recognizer,
            microphone,
            timeout=3,
            phrase_time_limit=3,
        )

        if not any(word in wake_word for word in WAKE_WORDS):
            continue

        speak("Yes, I am listening.")

        command = listen(
            recognizer,
            microphone,
            timeout=5,
            phrase_time_limit=8,
        )

        if not command:
            speak("I did not hear a command.")
            continue

        should_continue = process_command(command)

        if not should_continue:
            break


if __name__ == "__main__":
    main()
