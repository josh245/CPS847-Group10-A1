#Adopted with modifications from https://github.com/mattmakai/slack-starterbot/blob/master/starterbot.py
#Distributed under MIT license

#don't forget to set the environmental variable SLACK_BOT_TOKEN using
#export SLACK_BOT_TOKEN='Your Bot User OAuth Access Token'
#or hardcode

import os
import time
import re
import urllib.request
import pytest
from slackclient import SlackClient

import json #used for debug printing

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 5

#Slack bot token
with open ("slackAuthCode.txt", "r") as slackAuthCode:
   SLACK_BOT_TOKEN = slackAuthCode.read()

#Weather API token 
with open ("weatherapiKey.txt", "r") as weatherapiKey:
   WEATHER_API_KEY = weatherapiKey.read()   

# instantiate Slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+)>(.*)"
QUESTION_REGEX = "[a-zA-Z]*.*\?+"
WEATHER_REGEX = "weather"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
    	#uncomment line below to debug print
    	#print json.dumps(event, indent = 2, sort_keys = True)

        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            #uncomment line below to debug print
            #print user_id, " : ", message
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"

    if re.match(QUESTION_REGEX, command):
        response = command

    if re.search(WEATHER_REGEX, command.lower()):
        weather_commandList = command.split()
        try:
            weather_request_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + weather_commandList[1] + '&APPID=' + WEATHER_API_KEY
        except StandardError:
            response = 'Failed URL'                  
        try:    
            json_response = urllib.request.urlopen(weather_request_url).read().decode('utf-8')
            weather_data = json.loads(json_response)            
            temp = weather_data['main']['temp']          
            response = 'The temperature for ' + weather_commandList[1] + ' is ' + str(int(temp - 273.15)) + ' celsius.'
        except urllib.error.HTTPError:
            response = 'Failed to get the weather for you, try saying "Weather CityName" next time you message Big Bot Green.'

        #except ValueError:  # includes simplejson.decoder.JSONDecodeError
            #response = 'Failed'

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

if __name__ == "__main__":
	# avm: connect is designed for larger teams,
	# see https://slackapi.github.io/python-slackclient/real_time_messaging.html
	# for details
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
