import requests
from dotenv import load_dotenv
import os
from urllib3.exceptions import InsecureRequestWarning
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import numpy as np
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
if (existing_database == '2'): 
  # create new database
  db_name = input("What would you like to name your database: ")
  my_database = mysql.connector.connect(
  host='localhost',
  user='root',
  passwd=sql_password
  )
  
  my_cursor = my_database.cursor()
  my_cursor.execute(f"CREATE DATABASE {db_name}")
  print(f"Database '{db_name}' created successfully.")
else: 
  db_name = input("What is the name of your database: ")

unit_conversion = None

while unit_conversion not in {'1','2'}:
  unit_conversion = input("What unit would you like to use for distance?:\ntype 1 for meters\n"
    "type 2 for miles\n"
    "> ")
  if unit_conversion not in {'1','2'}:
        print("Please enter 1 or 2")

speed_conversion = 1
distance_conversion = 1
if (unit_conversion == '2'):
  speed_conversion = 2.236936
  distance_conversion = 0.0006213712

my_database = mysql.connector.connect(
  host='localhost',
  user='root',
  passwd=sql_password,
  database=db_name
  )

my_cursor = my_database.cursor()
   
table_query = """
    CREATE TABLE IF NOT EXISTS user_data (
        activity_id BIGINT,
        start_date VARCHAR(10),
        type VARCHAR(20),
        distance_m DECIMAL(4,2),
        elapsed_time_s INT,
        average_cadence DECIMAL(3,1),
        average_watts DECIMAL(4,1),
        max_watts INT,
        calories SMALLINT,
        average_speed_mps DECIMAL(4,2),
        max_speed_mps DECIMAL(4,2),
        average_heartrate DECIMAL(4,1),
        max_heartrate SMALLINT,
        summary_polyline VARCHAR(1500),
        PRIMARY KEY(activity_id)
    )
"""
my_cursor.execute(table_query)

header = {'Authorization': f'Bearer {access_token}'}
# get all activities and their stats
all_activities_url = "https://www.strava.com/api/v3/athlete/activities"

print("INSERTING VALUES...")
# ensure you can access all activities and not api request limit
page_num = 1
while True:
  param = {'per_page': 100, 'page': page_num}
  activities_response = requests.get(all_activities_url, headers=header, params=param)
  all_activities = activities_response.json()

  if (len(all_activities) == 0):
    break

  # each individual activity in all of them
  for activity_data in all_activities:
    activity_id = activity_data['id']
  
    # get request gets extra information of activity by giving its id
    get_all_activity_data_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    get_all_activity_data_response = requests.get(get_all_activity_data_url, headers=header)
    activity = get_all_activity_data_response.json()

    # set to default value if there is a key error
    values = (
    activity_id,
    activity.get('start_date', '0000-00-00'),
    activity.get('type', 'N/A'),
    activity.get('distance', 0) * distance_conversion,
    activity.get('elapsed_time', 0),
    activity.get('average_cadence', 0),
    activity.get('average_watts', 0),
    activity.get('max_watts', 0),
    activity.get('calories', 0),
    activity.get('average_speed', 0) * speed_conversion,
    activity.get('max_speed', 0) * speed_conversion,
    activity.get('average_heartrate', 0),
    activity.get('max_heartrate', 0),
    activity.get('map', {}).get('summary_polyline', '')
    )

    query = "INSERT IGNORE INTO user_data (activity_id, start_date, type, distance_m, elapsed_time_s, average_cadence, average_watts, max_watts, calories, average_speed_mps, max_speed_mps, average_heartrate, max_heartrate, summary_polyline) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    my_cursor.execute(query, values)
  
  page_num += 1

# alter unit of measurements to user preference if need to be changed
if (unit_conversion == '2'):
  my_cursor.execute("ALTER TABLE user_data RENAME COLUMN distance_m to distance_miles")
  my_cursor.execute("ALTER TABLE user_data RENAME COLUMN average_speed_mps to average_speed_mph")
  my_cursor.execute("ALTER TABLE user_data RENAME COLUMN max_speed_mps to max_speed_mph")
  print("unit conversion occurred")

print("VALUES INSERTED")

# my_cursor.execute("SELECT distance FROM user_data ")  
# for one_activity in my_cursor:
#   # returns a tuple so only want to collect first value
#   one_activity[0]
  

my_cursor.fetchall()
my_database.commit()


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
    print("Please enter 1, 2, or 3")

if user_choice_of_activity == '2':
  my_cursor.execute("SELECT * FROM user_data WHERE type=%s LIMIT 50", ('Run',))
  print("RUN SELECTED")

elif user_choice_of_activity == '3':
  my_cursor.execute("SELECT * FROM user_data WHERE type=%s LIMIT 50", ('Walk',))
  print("WALK SELECTED")

else:
  my_cursor.execute("SELECT * FROM user_data LIMIT 50")
  print("ALL ACTIVITIES SELECTED")

result = my_cursor.fetchall()
my_database.commit()

for row in result:
  print(row)

file = "data.csv"



with open(file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(result)

new_file = pd.read_csv(file)


# plot data

my_database.close()
my_cursor.close()




# # references
# # https://nddoornekamp.medium.com/plotting-strava-data-with-python-7aaf0cf0a9c3

#  # heartrate zones request
#     get_heartrate_zones_url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
#     get_heartrate_zones_response = requests.get(get_heartrate_zones_url, headers=header)
#     heartrate_zones = get_heartrate_zones_response.json()