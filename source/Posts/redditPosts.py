from __future__ import annotations

import pprint

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

    def getPost(self, subreddit_name="", info="hot", limit=1) -> PostData:
        """
        :param info: Choose from the list of 'hot', 'new', and 'top'
        :param subreddit_name: the subreddit we are interested in
        :return: return a Post Data that contains the title, text, username, images, and replies
        The replies is a trees
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        function_type = {"hot": subreddit.hot, "new": subreddit.new, "top": subreddit.top}

        if info not in function_type:
            raise ValueError("Incorrect info. Must be either 'hot', 'new', or 'top'")

        for submission in function_type[info](limit=limit):
            # TODO: Add a checker to check whether the current submission already exists
            # For now, it will return the very first submission and call it a day
            # it is not guarantee that the author and title will remain the same
            try:
                author = submission.author.name
                title = submission.title
                text = submission.selftext
                replies = self._get_comments(submission.comments)
                id = submission.id
                data = PostData(author, title, text, id, [], replies)
                return data
            except AttributeError as E:
                print(E)

    def _get_comments(self, comments: praw.models.comment_forest.CommentForest, parent: Reply | None = None):
        """
        Returns a similar Forest of Tree implementation but with the Reply struct
        :param comments: CommonForest
        :param parent: The current Parent
        :return: A list of replies in a forest of Tree implementation
        """
        replies = []
        for comment in comments:
            user = comment.author.name if comment.author is not None else None
            content = comment.body
            images = []

            reply = Reply(parent, user, [], content, images)
            children = self._get_comments(comment.replies, reply)
            reply.children = children
            replies.append(reply)

        return replies


if __name__ == '__main__':
    redditPost = RedditPost()
    data = redditPost.getPost("pettyrevenge")
    pprint.pprint(data)