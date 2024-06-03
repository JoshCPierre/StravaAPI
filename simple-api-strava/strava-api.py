import requests
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import pandasql as pdsql
import matplotlib.pyplot as plt
import numpy as np
import polyline
import csv

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# "https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost&response_type=code&scope=activity:read_all"
# copy 'code' from url of this link and make this POST request on postman:
# https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&code={code_copied_above}&grant_type=authorization_code

# use refresh token from postman 
refresh_token = os.getenv('REFRESH_TOKEN')

# params sent to post request
params = {
  'client_id': client_id,
  'client_secret': client_secret,
  'refresh_token': refresh_token,
  'grant_type': "refresh_token",
  'f': 'json'
}

# suppress warning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

auth_code_url = "https://www.strava.com/api/v3/oauth/token"
access_token_request = requests.post(auth_code_url, data=params, verify=False)

# get access token from post request json
access_token = access_token_request.json()['access_token']

header = {'Authorization': f'Bearer {access_token}'}

all_activities_url = "https://www.strava.com/api/v3/athlete/activities"


activities_response = requests.get(all_activities_url, headers=header)
all_activities = activities_response.json()


# print(all_activities[0]['id'])

# df = pd.DataFrame.from_records(all_activities)
# df = df[["id", "type", "distance", "elapsed_time", "total_elevation_gain",
#            "average_speed", "max_speed"]]

# sql_query = "SELECT * FROM df WHERE distance <> 0.0"
# df = pdsql.sqldf(sql_query, locals())
# print(df)


# https://nddoornekamp.medium.com/plotting-strava-data-with-python-7aaf0cf0a9c3
# coordinates = polyline.decode(activity['map']['summary_polyline'])

# https://www.strava.com/api/v3/activities/{id}/streams/heartrate
# get extra information






