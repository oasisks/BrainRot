from __future__ import annotations

import pprint
import praw
import validators
from dotenv import load_dotenv
import os
import sys

# to allow access to the source directory
sys.path.insert(0, '../')

from PostData import PostData, Reply
from DataPool.dataPool import DataPool


class RedditPost:
    def __init__(self, dataPool: DataPool):
        load_dotenv()
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        user_agent = os.getenv("USER_AGENT")

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        self._datapool = dataPool
        self._collection_name = "Reddit"

    def getPost(self, subreddit_name="",
                after: str | None = None,
                info="hot",
                limit=10,
                url: str = "",
                save_post: bool = True) -> PostData | None:
        """
        The getPost function will indefinitely go down a subreddit until it returns a submission.
        It does this by keeping track of the last ID the function has seen.

        It is recommended to keep track of the last post received and pass that into the 'after' parameter

        :param info: Choose from the list of 'hot', 'new', and 'top'
        :param subreddit_name: the subreddit we are interested in
        :param limit: The limit per request
        :param after: A string to signify after what submission do we want to look for (i.e., t3_2md312s)
        :param url: if given, then getPost will strictly return the post
        :param save_post: If the post should be saved or not, by default it is saved to the database
        :return: return a Post Data that contains the title, text, username, images, and replies
        The replies is a trees
        """
        if url:
            # TODO: Check if it is a valid post URL
            if not validators.url(url):
                raise ValueError("Invalid URL format")
            tokens = url.split("/")
            submission_id = tokens[6]
            submission = self.reddit.submission(submission_id)
            submissions = [submission]
        else:
            subreddit = self.reddit.subreddit(subreddit_name)
            function_type = {"hot": subreddit.hot, "new": subreddit.new, "top": subreddit.top}
            if info not in function_type:
                raise ValueError("Incorrect info. Must be either 'hot', 'new', or 'top'")

            params = {} if after is None else {"after": after}
            submissions = function_type[info](limit=limit, params=params)

        data = None
        most_recent_id = ""
        for submission in submissions:
            try:
                # we need to check for duplication
                # the thing that differentiates post from other posts is the submission id

                # meta data
                author = submission.author.name
                title = submission.title
                text = submission.selftext
                replies = self._get_comments(submission.comments)
                data_id = f"{subreddit_name}_{submission.id}"
                most_recent_id = f"t3_{submission.id}"

                # first check if the id already exists
                collection = self._datapool.get_from_collection(self._collection_name, {"_id": data_id})
                count = len([doc for doc in collection])

                if count > 0:
                    continue

                # next if we know it does not exist, we add it to the db
                if save_post:
                    self._datapool.add_to_collection(self._collection_name, [
                        {
                            "_id": data_id,
                        }
                    ])

                data = PostData(author, title, text, data_id, subreddit_name, [], replies)
                return data
            except AttributeError as e:
                return data

        # if I am here and I still haven't gotten a valid data, then we query again
        data = self.getPost(subreddit_name, most_recent_id, info, limit, url, save_post)
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
            # we don't necessarily care about more comments
            if isinstance(comment, praw.reddit.models.MoreComments):
                continue
            user = comment.author.name if comment.author is not None else None
            content = comment.body.encode()
            images = []

            reply = Reply(parent, user, [], content, images)
            children = self._get_comments(comment.replies, reply)
            reply.children = children
            replies.append(reply)

        return replies


if __name__ == '__main__':
    datapool = DataPool()
    redditPost = RedditPost(datapool)
    # data = redditPost.getPost("pettyrevenge")
    # pprint.pprint(data)
    data = redditPost.getPost(
        url="https://www.reddit.com/r/amiwrong/comments/1boff73/my_girlfriend_cheated_on_me_with_my_brother_and/",
        save_post=False
    )
    pprint.pprint(data)