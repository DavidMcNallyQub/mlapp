# -*- coding: utf-8 -*-

# Sample Python code for youtube.commentThreads.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import googleapiclient.discovery

import json

def get_youtube_video_comments():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyD5l-RDjjcUSjSaSqMGE2YrR6WqRgZzvAA"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part="snippet, replies",
        videoId="PSWf2TjTGNY",
        maxResults=100
    )
    response = request.execute()

    all_comments = []

    comment_threads = response['items']

    for thread in comment_threads:
        top_level_comment = thread['snippet']['topLevelComment']['snippet']['textOriginal']
        print(top_level_comment)
        all_comments.append(top_level_comment)
        # print(thread)
        # print(type(thread))
        if thread['snippet']['totalReplyCount'] > 0:
            replies= thread['replies']['comments']
            for reply in replies:
                reply = reply['snippet']['textOriginal']
                print(reply)
                all_comments.append(reply)

    print(f"{len(all_comments)} comments found!")
        
    # print(response['items'])


if __name__ == "__main__":
    get_youtube_video_comments()