from imports import ImageClip, VideoFileClip, CompositeVideoClip, concatenate_videoclips, vfx
from imports import time, subprocess, random, configparser, sys, os
from imports import Reddit, Driver, Youtube, Screenshot


class RedditToYoutube:
    def __init__(self, channel_index):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.outputDir = self.config["General"]["OutputDirectory"]
        if not os.path.isdir(self.outputDir):
            os.makedirs(self.outputDir)

        self.bgDir = self.config["General"]["BackgroundDirectory"]
        self.bgPrefix = self.config["General"]["BackgroundFilePrefix"]
        self.bgCount = len(os.listdir(self.bgDir)) - 1

        self.bitrate = self.config["Video"]["Bitrate"]
        self.threads = self.config["Video"]["Threads"]

        self.driver = Driver()
        self.reddit = Reddit()
        self.screenshot = Screenshot(self.driver)
        self.youtube = Youtube(self.driver, self.reddit)
        self.channel_index = channel_index

    def __createClip(self, screenShotFile, audioClip, marginSize, w, h):
        imageClip = ImageClip(
            screenShotFile,
            duration=audioClip.duration
        ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip

    def upload_leftover(self):
        try:
            self.youtube.upload_leftover()
        except Exception as e:
            print(f"\nLeftover Upload Failed: {e}")

    def createVideo(self, id=None):

        startTime = time.time()

        # Get script from reddit
        # If a post id is listed, use that. Otherwise query top posts
        if id != None:
            script = self.reddit.getContentFromId(self.outputDir, id)
        elif (len(sys.argv) == 2):
            script = self.reddit.getContentFromId(self.outputDir, sys.argv[1])
        else:
            postOptionCount = int(
                self.config["Reddit"]["NumberOfPostsToSelectFrom"])
            script = self.reddit.getContent(self.outputDir, postOptionCount)
            if script == None:
                return
        fileName = script.getFileName()
        # fileName = fileName + "\"%s\""%script.title
        # print(fileName)

        self.driver.show_window()

        # Create screenshots
        self.screenshot.getPostScreenshots(fileName, script)

        # Setup background clip
        if self.bgCount == 0:
            print(
                f"Insifficient Background Videos Avaiable in the directory \"{self.bgDir}\"")
        bgIndex = random.randint(1, self.bgCount)
        backgroundVideo = VideoFileClip(
            filename=f"{self.bgDir}/{self.bgPrefix}{bgIndex}.mp4",
            audio=False)
        if backgroundVideo.duration > script.getDuration():
            backgroundVideo = backgroundVideo.subclip(0, script.getDuration())
        backgroundVideo = vfx.loop(
            backgroundVideo, duration=script.getDuration())
        w, h = backgroundVideo.size

        # Create video clips
        print("Editing clips together...")
        clips = []
        marginSize = int(self.config["Video"]["MarginSize"])
        clips.append(self.__createClip(script.titleSCFile,
                     script.titleAudioClip, marginSize, w, h))
        for comment in script.frames:
            clips.append(self.__createClip(comment.screenShotFile,
                         comment.audioClip, marginSize, w, h))

        # Merge clips into single track
        contentOverlay = concatenate_videoclips(
            clips).set_position(("center", "center"))

        # Compose background/foreground
        final = CompositeVideoClip(
            clips=[backgroundVideo, contentOverlay],
            size=backgroundVideo.size).set_audio(contentOverlay.audio)
        final.duration = script.getDuration()
        final.set_fps(backgroundVideo.fps)

        # Write output to file
        print("Rendering final video...")
        outputFile = f"{self.outputDir}/{fileName}.mp4"
        final.write_videofile(
            outputFile,
            codec='mpeg4',
            threads=self.threads,
            bitrate=self.bitrate
        )
        print(f"Video completed in {time.time() - startTime}")

        # Preview in VLC for approval before uploading
        if (self.config["General"].getboolean("PreviewBeforeUpload")):
            vlcPath = self.config["General"]["VideoPlayerPath"]
            p = subprocess.Popen([vlcPath, outputFile])
            print("Waiting for video review. Type anything to continue")
            wait = input(
                "[0] Upload\n[1] Ignore\n[2] Delete\n[3] Redo\n[4] Exit Program\n")
            wait = int(wait) if wait.isdigit() else 0
            if wait == 1:
                self.youtube.dummyFile(f"{self.outputDir}/{fileName}.mp4")
                print("The Video Has Been Ignored")
                return
            if wait == 2:
                os.remove(outputFile)
                print("The Video Has Been Deleted")
                return
            if wait == 3:
                os.remove(outputFile)
                print(f"Remaking :{script.title}")
                self.createVideo(script.fileID)
                return
            if wait == 4:
                print("Exiting Program...")
                return

        print("Video is ready to upload!")
        print(f"Title: {script.title}  File: {outputFile}")
        endTime = time.time()
        print(f"Total time: {endTime - startTime}")

        print("\nUploaing Process Started..")

        self.youtube.login()
        self.youtube.select_channel(self.channel_index)

        for file in os.listdir(f'{self.outputDir}'):
            if os.path.getsize(f'{self.outputDir}\{file}') == 0:
                continue
            self.youtube.upload(file)

            print('Completed Uploading.. ')


class App:
    def run(self):
        app = RedditToYoutube(channel_index=2)
        if app.youtube.upload_leftover(app.channel_index):
            return
        app.createVideo()


if __name__ == "__main__":
    app = App()
    app.run()
