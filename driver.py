from imports import webdriver, ChromeDriverManager, WebDriverWait, By, EC
from imports import requests, pytubedownloader

class Driver:
    def __init__(self):

        self.options = webdriver.ChromeOptions()

        self.options.add_argument("--lang=en")
        # options.add_argument("--start-maximized")
        # options.add_argument('--headless')
        # options.add_experimental_option('detach', True)
        self.options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(), options=self.options)

        self.driver.minimize_window()
        

        self.watch_link = 'https://www.youtube.com/watch?v=%s'

        self.embed_link = 'https://www.youtube.com/oembed?url=%s&format=json'

    def reset_driver(self):
        self.driver.quit()
        self.driver = webdriver.Chrome(
            executable_path=ChromeDriverManager().install(), options=self.options)

    def embed(self, url):
        return requests.get(self.embed_link % str(self.watch_link % url)).json()

    def charFilter(self, string):
        return ''.join(
            e if e in ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ#()!' else '' for e in string)

    def show_window(self):
        w, h = self.driver.get_window_size().values()
        self.driver.set_window_size(width=w, height=h)

    def get(self, url):
        return self.driver.get(url)

    def wait_for_Xpath(self, xpath):
        try:
            search = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
            search = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, xpath)))
            return search
        except Exception as e:
            print(f"Browser Failed: {e}")

    def download_video(self, id):
        link = self.watch_link % id
        youtubeObject = pytubedownloader(link)
        youtubeObject = youtubeObject.streams.get_highest_resolution()
        try:
            youtubeObject.download('./videos', id+'.mp4')
        except:
            print("An error has occurred")
        print(id + ".mp4 Saved")
