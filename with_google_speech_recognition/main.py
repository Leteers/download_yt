import moviepy.editor as mp
import moviepy.audio as audio
import speech_recognition as sr

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pytubefix import YouTube

from pathlib import Path

import os
from pydub import AudioSegment
import speech_recognition as sr
import config

# Function to split audio into chunks
def split_audio(audio_path, chunk_length_ms=10000):
    audio = AudioSegment.from_file(audio_path)  # Load the audio file
    audio_chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_name = f"chunk{i//chunk_length_ms}.wav"
        chunk.export(chunk_name, format="wav")
        audio_chunks.append(chunk_name)
    return audio_chunks

# Function to transcribe each chunk
def transcribe_chunks(chunks):
    recognizer = sr.Recognizer()
    full_text = ""
    for chunk in chunks:
        with sr.AudioFile(chunk) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                full_text += text + " "
            except sr.UnknownValueError:
                full_text += "[Unrecognized Speech] "
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    full_text += '\n'
    return full_text

# Function to clean up (delete) the chunk files
def cleanup_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)

# Main function to split, transcribe, and merge the results
def process_audio(audio_path):
    # 1. Split the audio into smaller chunks
    chunks = split_audio(audio_path, chunk_length_ms=60*1000)  # 10 seconds per chunk (~10MB)
    
    # 2. Transcribe each chunk and merge the text
    full_text = transcribe_chunks(chunks)
    
    # 3. Save the transcribed text to a file
    with open("transcribed_text.txt", "a", encoding="utf-8") as f:
        f.write(audio_path[:audio_path.rfind('.')] + '\n')
        f.write(full_text)
    print("Transcription complete. Saved to 'transcribed_text.txt'.")

    # 4. Clean up the chunk files
    cleanup_files(chunks)
    print("Temporary audio chunks deleted.")

f_path = config.folder_path
folder_path = Path(f_path)
my_url = config.playlist_url
output_file = "result_text.txt"

driver = webdriver.Chrome()
driver.get(my_url)
delay = 10
try:
    wait = WebDriverWait(driver,delay)
    p_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,".yt-simple-endpoint.style-scope.ytd-playlist-panel-video-renderer")))
    p = driver.find_elements(By.CSS_SELECTOR,".yt-simple-endpoint.style-scope.ytd-playlist-panel-video-renderer")
    tittles = [i.text for i in p]
    links = [i.get_attribute("href") for i in p]
    driver.close()
except TimeoutException:
    print("No playlist found on current page!")
    driver.close()
    
def find_2nd(string, substring):
   return string.find(substring, string.find(substring) + 1)


for i,link in enumerate(links):
    if str(tittles[i]).count('\n') == 3:
        tittle = tittles[i][find_2nd(tittles[i],'\n')+1:tittles[i].rfind('\n')]
    else:
        tittle = tittles[i][tittles[i].find('\n')+1:tittles[i].rfind('\n')]
    print(tittle)
    yt = YouTube(link)
    stream = yt.streams.first()
    stream.download(f_path)
    video = mp.VideoFileClip(filename=f'{f_path}/{tittle}.mp4')
    audio_file = video.audio 
    audio_file.write_audiofile(f"{tittle}.wav") 
    video.close()
    for mp4_file in folder_path.glob("*.mp4"):
        mp4_file.unlink()  # Удаляет файл
        print(f"Удален файл: {mp4_file}")
    audio_path = f'{tittle}.wav'
    print(audio_path[:audio_path.rfind('.')])
    process_audio(f'{tittle}.wav')