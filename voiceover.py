from imports import pyttsx3, random

voiceoverDir = "Voiceovers"

def create_voice_over(fileName, text):
    filePath = f"{voiceoverDir}/{fileName}.mp3"
    engine = pyttsx3.init()
    # voices = engine.getProperty('voices')
    # voice = random.randint(0,1)
    # engine.setProperty('voice', voices[voice].id)
    # if voice: engine.setProperty('rate', random.randint(180,190)) 
    engine.save_to_file(text, filePath)
    engine.runAndWait()
    return filePath