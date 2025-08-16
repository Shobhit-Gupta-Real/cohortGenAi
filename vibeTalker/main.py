import speech_recognition as sr


def main():
    r = sr.Recognizer()  # speech to text

    with sr.Microphone() as source:  # mic access
        r.adjust_for_ambient_noise(source=source)
        r.pause_threshold = 0.5  # seconds of non-speaking before considering the input finished
        print("Listening...")
        audio = r.listen(source)  # listen for the first phrase
        print("Recognizing...")

        stt = r.recognize_google(audio)  # recognize speech using Google Web Speech API
        print(f"You said: {stt}")


main()
