from imports import os, time, configparser
from imports import By, Keys, EC, TimeoutException

class Youtube:
    def __init__(self, driver, reddit):
                
        self.config = configparser.ConfigParser()
        self.config.read('privateconfig.ini')

        self.MAIL_ID = self.config["Youtube"]["Gmail"]
        self.PASSWORD = self.config["Youtube"]["Password"]
        self.config2 = configparser.ConfigParser()
        self.config.read('config.ini')
        self.UPLOAD_FOLDER = self.config["General"]["OutputDirectory"]

        self.YT_URL = "https://studio.youtube.com/"

        self.LOGIN_EMAIL_XPATH = '/html/body/div[1]/div[1]/div[2]/div/c-wiz/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input'
        self.LOGIN_PASSWORD_XPATH = '/html/body/div[1]/div[1]/div[2]/div/c-wiz/div/div[2]/div/div[1]/div/form/span/section[2]/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input'

        self.PROFILE_BUTTON_XPATH = '/html/body/ytcp-app/ytcp-entity-page/div/ytcp-header/header/div/ytd-topbar-menu-button-renderer/button'
        self.SWITCH_CHANNEL_XPATH = '/html/body/ytcp-app/ytcp-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer[1]/div[2]/ytd-compact-link-renderer[3]'
        self.CHANNEL_XPATH = "/html/body/ytcp-app/ytcp-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[4]/ytd-multi-page-menu-renderer/div[3]/div[1]/ytd-account-section-list-renderer/div[2]/ytd-account-item-section-renderer/div[2]/ytd-account-item-renderer[?]"

        self.driver = driver
        self.wait_for_Xpath = self.driver.wait_for_Xpath
        self.reddit = reddit.reddit_handle
    
        
    def login(self):

        try:
            self.driver.get(self.YT_URL)

            print("\nLoggin In...")

            login_email = self.wait_for_Xpath(self.LOGIN_EMAIL_XPATH)
            time.sleep(1)
            login_email.send_keys(self.MAIL_ID)
            time.sleep(1)
            login_email.send_keys(Keys.ENTER)
            time.sleep(1)

            login_password = self.wait_for_Xpath(self.LOGIN_PASSWORD_XPATH)
            time.sleep(1)
            login_password.send_keys(self.PASSWORD)
            time.sleep(1)
            login_password.send_keys(Keys.ENTER)
            time.sleep(1)

            print("\nLog-In successful...")
        except Exception as e:
            print(f"\nLogin Failed..{e}")
            print("\nRetring...")
            self.driver.driver.switch_to.window(self.driver.driver.current_window_handle)
            self.login()
    
        
    def select_channel(self, channel_id):
        time.sleep(5)

        self.wait_for_Xpath(self.PROFILE_BUTTON_XPATH).click();time.sleep(2)
        self.wait_for_Xpath(self.SWITCH_CHANNEL_XPATH).click();time.sleep(2)
        self.wait_for_Xpath(self.CHANNEL_XPATH.replace('?',str(channel_id))).click()
        print(f'\nChannel Switched to index : {channel_id}')
    
        
    def getTitle(self, filename):
        id = filename[:-4:].split('-')[-1]
        title = self.reddit.submission(id).title
        return title

    def dummyFile(self, file):
        os.remove(f"./{self.UPLOAD_FOLDER}/%s"%file)

        with open(f"./{self.UPLOAD_FOLDER}/%s"%file, 'wb') as f:         
            
            print("\n" + "File Replaced With Dummy File :" + f"./{self.UPLOAD_FOLDER}/%s"%file)

    def find_element(self, method, handle):
        return self.driver.driver.find_element(method, handle)

    def upload(self, file):
        try:
            print("\nUpload Initialized... ")
            time.sleep(3)
            upload_button = self.find_element(By.XPATH, '//*[@id="upload-icon"]')
            upload_button.click()
            time.sleep(5)

            nameofvid = file[:-4:]
            title = self.getTitle(file)
            file_input = self.find_element(By.XPATH, '//*[@id="content"]/input')
            simp_path = f'{self.UPLOAD_FOLDER}/%s.mp4' % nameofvid
            abs_path = os.path.abspath(simp_path)

            print("\n" + "Upload Started: " + title)
            
            file_input.send_keys(abs_path)
            time.sleep(7)

            title_text = self.find_element(By.XPATH, '//*[@id="textbox"]')
            title_text.clear()
            title_text.send_keys(title + " #shorts #reddit" if len(title + "#shorts #reddit") < 99 else title[:90:])

            next_button = self.find_element(By.XPATH, '//*[@id="next-button"]')
            for i in range(3):
                time.sleep(5)
                next_button.click()
                if i == 0: print("Confirmation 1")
                if i == 1: print("Confirmation 2")
                if i == 2: print("Confirmation Complete")

            done_button = self.find_element(By.XPATH, '//*[@id="done-button"]')
            done_button.click()
            time.sleep(5)

            print("\n" + "Upload Finished: " + title)

            self.dummyFile(file)

            time.sleep(5)
        except TimeoutException:
            print("\nTimed Out - Retring Upload")
            self.driver.get(self.YT_URL)
            self.upload(file)
    
    
    def upload_leftover(self, channel_index):
        for file in os.listdir(f'{self.UPLOAD_FOLDER}'):
            if os.path.getsize(f'{self.UPLOAD_FOLDER}\{file}') == 0:
                continue
            else:
                print("\nLeftover Video Found..")
                self.login()
                self.select_channel(channel_index)
                self.upload(file)
                self.driver.driver.minimize_window()
                return True
            break
