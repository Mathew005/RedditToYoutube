from imports import time
from imports import TimeoutException, ElementNotInteractableException, NoSuchElementException
from imports import EC, WebDriverWait, By

class Screenshot:
    def __init__(self, driver):
        # Config
        self.screenshotDir = "Screenshots"
        self.screenWidth = 400
        self.screenHeight = 800
        self.attempt = 0
        self.driver = driver.driver

    def getPostScreenshots(self, filePrefix, script):
        print("Taking screenshots...")
        self.driver, wait = self.__setupDriver(script.url)
        script.titleSCFile = self.__takeScreenshot(filePrefix, self.driver, wait)
        # expand_buttons = [button.click() for button in wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'icon-expand')))]
        for count,commentFrame in enumerate(script.frames):
            print(f"[{count+1}/{len(script.frames)}] ", end='')
            commentFrame.screenShotFile = self.__takeScreenshot(filePrefix, self.driver, wait, f"t1_{commentFrame.commentId}")
        print()
        # driver.quit()
        self.driver.set_window_size(width=self.screenWidth*3, height=self.screenHeight*1.2)
        self.driver.minimize_window()

    def __takeScreenshot(self, filePrefix, driver, wait, handle="Post"):
        try:
            method = By.CLASS_NAME if (handle == "Post") else By.ID
            search = wait.until(EC.presence_of_element_located((method, handle)))
            search = wait.until(EC.visibility_of_element_located((method, handle)))
            try:
                if (handle != "Post") : 
                    try: 
                        button = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="{handle}"]/div[2]/button')))
                        if (button.is_displayed()) : button.click()
                        search = wait.until(EC.presence_of_element_located((method, handle)))
                    except NoSuchElementException: 
                        pass
            except ElementNotInteractableException:
                pass
            self.driver.execute_script("window.focus();")

            fileName = f"{self.screenshotDir}/{filePrefix}-{handle}.png"
            fp = open(fileName, "wb")
            fp.write(search.screenshot_as_png)
            fp.close()
            time.sleep(0.2)
            return fileName
        except TimeoutException:
            print("Sreenshot Timedout. Retrying...")
            self.__takeScreenshot(filePrefix, driver, wait, handle)
            attempt += 1
            if attempt == 3:
                print("Program Failed")


    def __setupDriver(self, url: str):
        self.wait = WebDriverWait(self.driver, 20)

        self.driver.set_window_size(width=self.screenWidth, height=self.screenHeight)
        self.driver.get(url)

        return self.driver, self.wait