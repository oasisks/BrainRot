from __future__ import annotations

import pprint
import praw
from dotenv import load_dotenv
import os


from PostData import PostData, Reply
from DataPool.DataPool import DataPool


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

        self._datapool = DataPool()
        self._collection_name = "Reddit"

    def getPost(self, subreddit_name="", info="hot", limit=10, after: str | None = None) -> PostData | None:
        """
        The getPost function will indefinitely go down a subreddit until it returns a submission.
        It does this by keeping track of the last ID the function has seen.

        It is recommended to keep track of the last post received and pass that into the 'after' parameter

        :param info: Choose from the list of 'hot', 'new', and 'top'
        :param subreddit_name: the subreddit we are interested in
        :param limit: The limit per request
        :param after: A string to signify after what submission do we want to look for (i.e., t3_2md312s)
        :return: return a Post Data that contains the title, text, username, images, and replies
        The replies is a trees
        """
        subreddit = self.reddit.subreddit(subreddit_name)
        function_type = {"hot": subreddit.hot, "new": subreddit.new, "top": subreddit.top}

        if info not in function_type:
            raise ValueError("Incorrect info. Must be either 'hot', 'new', or 'top'")

        data = None
        params = {} if after is None else {"after": after}
        most_recent_id = ""
        for submission in function_type[info](limit=limit, params=params):
            try:
                # we need to check for duplication
                # the thing that differentiates post from other posts is the submission id

                # meta data
                author = submission.author.name
                title = submission.title
                text = submission.selftext
                replies = self._get_comments(submission.comments)
                id = f"{subreddit_name}_{submission.id}"
                most_recent_id = f"t3_{submission.id}"
                # first check if the id already exists
                collection = self._datapool.get_from_collection(self._collection_name, {"_id": id})
                count = len([doc for doc in collection])

                if count > 0:
                    continue

                # next if we know it does not exist, we add it to the db
                self._datapool.add_to_collection(self._collection_name, [
                    {
                        "_id": id,
                    }
                ])
                data = PostData(author, title, text, id, subreddit_name, [], replies)
                return data
            except AttributeError as E:
                return data

        # if I am here and I still haven't gotten a valid data, then we query again
        data = self.getPost(subreddit_name, info, limit, most_recent_id)
        return data

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
