import praw
from dotenv import load_dotenv
import os
import pprint

class RedditPost:
    def __init__(self, subreddit=""):
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        user_agent = os.getenv("USER_AGENT")

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.subreddit = subreddit

    def getPost(self):
        pass