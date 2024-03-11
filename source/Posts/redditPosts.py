from __future__ import annotations

import praw
from dotenv import load_dotenv
import os
import sys

sys.path.append("../")
from PostData import PostData, Reply


class RedditPost:
    def __init__(self):
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        user_agent = os.getenv("USER_AGENT")

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def getPost(self, subreddit_name="", info="hot") -> PostData:
        """
        :param info: Choose from the list of 'hot', 'new', and 'top'
        :param subreddit_name: the subreddit we are interested in
        :return: return a Post Data that contains the title, text, username, images, and replies
        The replies is a trees
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        function_type = {"hot": subreddit.hot, }


if __name__ == '__main__':
    redditPost = RedditPost()
    redditPost.getPost("pettyrevenge")
    data = PostData("hello")
    print(data)
