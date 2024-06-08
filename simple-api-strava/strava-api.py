import requests
from dotenv import load_dotenv
import os
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np
import polyline
import csv

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# different scopes links
# "https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost&response_type=code&scope=activity:read_all"
# https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri=http://localhost&response_type=code&scope=profile:read_all

# copy 'code' from url of this link and make this POST request on postman:
# https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&code={code_copied_above}&grant_type=authorization_code

# use refresh token from postman 
activity_refresh_token = os.getenv('ACTIVITY_REFRESH_TOKEN')
profile_refresh_token = os.getenv('PROFILE_REFRESH_TOKEN')


# params sent to post request
data = {
  'client_id': client_id,
  'client_secret': client_secret,
  'refresh_token': activity_refresh_token,
  'grant_type': "refresh_token",
  'f': 'json'
}

# suppress warning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

auth_code_url = "https://www.strava.com/api/v3/oauth/token"
access_token_request = requests.post(auth_code_url, data=data, verify=False)

# get access token from post request json
access_token = access_token_request.json()['access_token']
header = {'Authorization': f'Bearer {access_token}'}


# get all activities and their stats
all_activities_url = "https://www.strava.com/api/v3/athlete/activities"
activities_response = requests.get(all_activities_url, headers=header)
all_activities = activities_response.json()


# mysql must be installed on computer

existing_database = None

while existing_database not in {'1','2'}:
  existing_database = input("Do you have an existing database:\ntype 1 for yes\n"
    "type 2 for no\n"
    "> ")
  if existing_database not in {'1','2'}:
        print("Please enter 1 or 2")

db_name = None
sql_password = os.getenv('SQL_PASSWORD')

if (existing_database == 2):
  db_name = input("What would you like to name your database: ")
  my_database = mysql.connector.connect(
  host='localhost',
  user='root',
  passwd=sql_password
  )
  
  my_cursor = my_database.cursor()
  my_cursor.execute(f"CREATE DATABASE {db_name}")

else: #just establish name
  db_name = input("What is the name of your database: ")


my_database = mysql.connector.connect(
  host='localhost',
  user='root',
  passwd=sql_password,
  database=db_name
  )

my_cursor = my_database.cursor()
   



# my_cursor.execute("CREATE TABLE ")




user_choice_of_activity = None
while (user_choice_of_activity not in {'1','2','3'}):
  user_choice_of_activity = input(
      "What activity data would you like to access:\n"
      "type 1 for all activities\n"
      "type 2 for running\n"
      "type 3 for walking\n"
      "> "
  )
  if user_choice_of_activity not in {'1','2','3'}:
    print("Please enter 1, 2, 3")


for i in range(len(all_activities)):
  activity_id = all_activities[i]['id']
  # get request gets extra information of activity if you give it its id
  get_all_activity_data_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
  get_all_activity_data_response = requests.get(get_all_activity_data_url, headers=header)
  activity = get_all_activity_data_response.json()

  # get a map of your activity
  # https://nddoornekamp.medium.com/plotting-strava-data-with-python-7aaf0cf0a9c3
  summary_polyline = activity['map']['summary_polyline']
  # print(summary_polyline, "\n")
  print(activity, "\n")





# scope=activity:read_all
# streams_url = f"https://www.strava.com/api/v3/activities/{first_activity_id}/streams"
# streams_response = requests.get(streams_url, headers=header)
# streams = streams_response.json()
# print(streams[0]['data'])


my_cursor.close()




# set refresh token to one with scope=profile:read_all
data = {
  'client_id': client_id,
  'client_secret': client_secret,
  'refresh_token': profile_refresh_token,
  'grant_type': "refresh_token",
  'f': 'json'
}

auth_code_url = "https://www.strava.com/api/v3/oauth/token"
access_token_request = requests.post(auth_code_url, data=data, verify=False)

# get new access token from post request
access_token = access_token_request.json()['access_token']


header = {'Authorization': f'Bearer {access_token}'}

athlete_zones_url = "https://www.strava.com/api/v3/athlete/zones"
athlete_zones_response = requests.get(athlete_zones_url, headers=header)
athlete_zones = athlete_zones_response.json()
# print(athlete_zones)



# df = pd.DataFrame.from_records(all_activities)
# df = df[["id", "type", "distance", "elapsed_time", "average_cadence", "average_watts", "max_watts",
# "calories", "average_speed", "max_speed", ]]
# if (has_heartrate) {"average_heartrate", "max_heartrate"}


# sql_query = "SELECT * FROM df WHERE distance <> 0.0"
# df = pdsql.sqldf(sql_query, locals())
# print(df)
