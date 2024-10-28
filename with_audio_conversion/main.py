import moviepy.editor as mp
import moviepy.audio as audio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pytubefix import YouTube
from pathlib import Path
import os
from pydub import AudioSegment
import config


# Путь к папке
f_path = config.folder_path

folder_path = Path(f_path)
# output_file = "resultant_text2.txt"
# Поиск и удаление всех .mp4 файлов

my_url = config.playlist_url
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
    print("Timeout!")
    

for i,link in enumerate(tittles):
    tittle = tittles[i][tittles[i].find(config.lecture_tittle_start_letter):tittles[i].rfind('\n')]
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
        
    # Initialize recognizer 
    # r = sr.Recognizer() 
    
    # Load the audio file 
    # with sr.AudioFile(f"{tittle}.wav") as source: 
    #     data = r.record(source) 
    # try:
    #     text = r.recognize_google(data)
    #     print(f"\nThe resultant text from video {tittle} is:\n")
    #     print(text)

    #     # Запись текста в файл
    #     file.write(f"Text from video {tittle}:\n{text}\n\n")
    # except sr.UnknownValueError:
    #     print("Google Speech Recognition не смог распознать аудио")
    # except sr.RequestError as e:
    #     print(f"Ошибка при запросе к Google Speech Recognition service; {e}")
    # audio_path = f'{tittle}.wav'
    # print(audio_path[:audio_path.rfind('.')])
    # process_audio(f'{tittle}.wav')