from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
import pandas as pd
import polyline
import json
import csv

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_url = os.getenv('REDIRECT_WEBSITE')

session = OAuth2Session(client_id=client_id, redirect_uri=redirect_url)

auth_base_url = "https://www.strava.com/oauth/authorize"
# what is able to be accessed from user profile
session.scope = ["activity:read_all"]

auth_link = session.authorization_url(auth_base_url)

print(f"Auth Link: {auth_link[0]}")





# parse redirect url
redirect_response = input(f"Paste redirect url here: ")

token_url = "https://www.strava.com/api/v3/oauth/token"

session.fetch_token(
  token_url=token_url,
  client_id=client_id,
  client_secret=client_secret,
  authorization_response=redirect_response,
  include_client_id=True
)

response = session.get("https://www.strava.com/api/v3/athlete/activities")

all_activities = json.loads(response.text)


df = pd.DataFrame.from_records(all_activities)
print(df[["id", "type", "distance", "elapsed_time", "total_elevation_gain",
           "average_speed", "max_speed"]])

# activity represents one json object

# for activity in all_activities:
#   print(activity['type'])

# https://nddoornekamp.medium.com/plotting-strava-data-with-python-7aaf0cf0a9c3
# coordinates = polyline.decode(activity['map']['summary_polyline'])










