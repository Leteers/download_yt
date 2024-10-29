import moviepy.editor as mp
import moviepy.audio as audio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pytubefix import YouTube
from pathlib import Path
from pydub import AudioSegment
import config


# folder_path
f_path = config.folder_path

folder_path = Path(f_path)
# output_file = "resultant_text2.txt"


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
    print("No playlist found on current page!")
    driver.close()
    
def find_2nd(string, substring):
   return string.find(substring, string.find(substring) + 1)

for i,link in enumerate(links):
    if str(tittles[i]).count('\n') == 3:
        tittle = tittles[i][find_2nd(tittles[i],'\n')+1:tittles[i].rfind('\n')]
    else:
        tittle = tittles[i][tittles[i].find('\n')+1:tittles[i].rfind('\n')]
    yt = YouTube(link)
    stream = yt.streams.first()
    stream.download(f_path)
    video = mp.VideoFileClip(filename=f'{f_path}/{tittle}.mp4')
    video.close()
