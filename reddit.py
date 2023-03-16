from imports import os, re, time
from imports import praw, markdown_to_text, VideoScript, MoreComments


class Reddit:
    def __init__(self):

        self.config.read('privateconfig.ini')
        self.client_id = self.config["Reddit"]["CLIENTID"]
        self.client_secret = self.config["Reddit"]["CLIENTSECREAT"]

        self.redditUrl = "https://www.reddit.com/"
        self.subreddit = "askreddit"
        self.reddit_handle = self.__getReddit()

    def __getReddit(self):
        return praw.Reddit(
            client_id=self.client_id, 
            client_secret=self.client_secret,
            # user_agent sounds scary, but it's just a string to identify what your using it for
            # It's common courtesy to use something like <platform>:<name>:<version> by <your name>
            # ex. "Window11:TestApp:v0.1 by u/Shifty-The-Dev"
            user_agent="YOUR_USER_AGENT_HERE"
        )

    def getContent(self, outputDir, postOptionCount) -> VideoScript:
        reddit = self.__getReddit()
        existingPostIds = self.__getExistingPostIds(outputDir)

        now = int(time.time())
        autoSelect = postOptionCount == 0
        posts = []

        print("[0] Exit The Program")
        for submission in reddit.subreddit(self.subreddit).top(time_filter="day", limit=postOptionCount*3):
            if (f"{submission.id}.mp4" in existingPostIds or submission.over_18):
                continue
            hoursAgoPosted = (now - submission.created_utc) / 3600
            print(
                f"[{len(posts) + 1}] {submission.title}     {submission.score}    {'{:.1f}'.format(hoursAgoPosted)} hours ago")
            posts.append(submission)
            if (autoSelect or len(posts) >= postOptionCount):
                break

        if len(posts) == 0:
            print("\nThere are no posts available at the moment..")
            return None

        if (autoSelect):
            return self.__getContentFromPost(posts[0])
        else:
            postSelection = int(input())
            if postSelection == 0:
                print("Exiting The Program...")
                return None
            selectedPost = posts[postSelection - 1]
            return self.__getContentFromPost(selectedPost)

    def getContentFromId(self, outputDir, submissionId) -> VideoScript:
        reddit = self.__getReddit()
        existingPostIds = self.__getExistingPostIds(outputDir)

        if (submissionId in existingPostIds):
            print("Video already exists!")
            exit()
        try:
            submission = reddit.submission(submissionId)
        except:
            print(f"Submission with id '{submissionId}' not found!")
            exit()
        return self.__getContentFromPost(submission)

    def __getContentFromPost(self, submission) -> VideoScript:
        content = VideoScript(submission.url, submission.title, submission.id)
        print(f"Creating video for post: {submission.title}")
        print(f"Url: {submission.url}")
        print(f"Post ID: {submission.id}")

        failedAttempts = 0
        # print(dir(submission.comments[0]))
        for comment in submission.comments:
            if isinstance(comment, MoreComments):
                continue
            if (content.addCommentScene(markdown_to_text(comment.body), comment.id)):
                failedAttempts += 1
            if (content.canQuickFinish() or (failedAttempts > 2 and content.canBeFinished())):
                break
        return content

    def __getExistingPostIds(self, outputDir):
        files = os.listdir(outputDir)
        # I'm sure anyone knowledgable on python hates this. I had some weird
        # issues and frankly didn't care to troubleshoot. It works though...
        files = [f for f in files if os.path.isfile(outputDir+'/'+f)]
        return [re.sub(r'.*?-', '', file) for file in files]
