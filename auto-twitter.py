import certifi
import base64
import hashlib
import os
import re
import json
import random
import requests
import tweepy
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session
from settings import *

app = Flask(__name__)
app.secret_key = os.urandom(50)
client_id = CLIENT_ID
client_secret = CLIENT_SECRET
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
redirect_uri = REDIRECT_URI
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

file_path = os.path.join(os.getcwd(), "pictures.json")
with open(file_path) as file:
    data: dict = json.load(file)
def make_token():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)

def choosePic():
    parent_folder = os.path.join(os.getcwd(), "images")
    subfolders = os.listdir(parent_folder)
    chosensubfolder = random.choice(subfolders)
    chosensubfolder_path = os.path.join(parent_folder,chosensubfolder)
    pictures = os.listdir(chosensubfolder_path)
    chosenpicture = random.choice(pictures)
    chosenpicture_path = os.path.join(chosensubfolder_path, chosenpicture)
    return chosenpicture_path

def upload_media():
    tweepy_auth = tweepy.OAuth1UserHandler(
        "{}".format(API_KEY),
        "{}".format(API_SECRET),
        "{}".format(ACCESS_TOKEN),
        "{}".format(ACCESS_TOKEN_SECRET),
    )
    tweepy_api = tweepy.API(tweepy_auth)
    verif = True
    while verif == True:
        img_data = choosePic()
        if img_data in data:
            verif = True
        else:
            verif = False
    post = tweepy_api.simple_upload(img_data)
    text = str(post)
    media_id = re.search("media_id=(.+?),", text).group(1)
    payload = {"media": {"media_ids": ["{}".format(media_id)]}}
    data["pictures"].append(img_data)
    with open(file_path, "w") as file:
        json.dump(data, file)
    return payload
def post_tweet(payload, new_token):
    print("Tweeting!")
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(new_token["access_token"]),
            "Content-Type": "application/json",
        },
    )
@app.route("/")
def demo():
    global twitter
    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)
@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    payload = upload_media()
    response = post_tweet(payload, token).json()
    return response

if __name__ == "__main__":

    app.run()