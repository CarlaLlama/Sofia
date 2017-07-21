"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
import json
from datetime import datetime, date, time
import urllib
import random
import string
from hashlib import sha1
import hmac
import time
from fatsecret import Fatsecret

# --------------- API Interface ----------------------

oauth_consumer_key = "88705826bc964b5185709b58777d9b34"
oauth_secret_key = "e053a5709b5243569f730e5a5200e9ee"
oauth_signature_method = "oauth_signature_method=HMAC-SHA1"
oauth_timestamp = int(time.time())
oauth_nonce = "oauth_nonce=" + ''.join(random.choice(string.lowercase) for i in range(7))
oauth_version = "oauth_version=1.0"
request_url = "http://platform.fatsecret.com/rest/server.api"
format = "format=json"
calorie_count = 0

class Request:
  def parse_slots(self, intent):
    print(intent['slots'])
    for slot in intent['slots'].keys():
      if 'value' in intent['slots'][slot]:
        setattr(self, slot, intent['slots'][slot]['value'])

class CalculateRequest(Request):
  def __init__(self, api, intent):
    self.parse_slots(intent)
    self.api = api
    self.card_title = 'Calculate'
  
  def reprompt_text(self):
    return self.speech_output()
  
  def speech_output(self):
    if self.is_valid:
      try:
        calories = self.api.calculate(getattr(self, 'height'), getattr(self, 'weight'), None, None)
        return "Today you have already eaten: " + calories + "!"
      except RuntimeError:
        return "I'm having troubles communicating with the server. Please try again later."  
    else:
      return "I'm not quite sure what you want. Please say it again"

  def is_valid(self):
    if getattr(self, 'type') != None:
      return True
    return False

    
class ConfigureMeRequest(Request):
  def __init__(self, api, intent, session):
    self.parse_slots(intent)
    self.api = api
    self.card_title = 'ConfigureMe'
  
  def reprompt_text(self):
    if self.is_valid:
      return self.speech_output()
    else:
      return "I'm not sure what your height and weight is. " \
              "You can tell me by saying, " \
              "I am x centimeters high and I weight y kilos"
  
  def speech_output(self):
    if self.is_valid:
      try:
        calories = self.api.configure_me(getattr(self, 'height'), getattr(self, 'weight'), None, None)
        return "With your height and weigth you should consume daily: " + calories + "!"
      except RuntimeError:
        return "I'm having troubles communicating with the server. Please try again later."  
    else:
      return "I'm not sure what your height and weight is. Please try again."

  def is_valid(self):
    if getattr(self, 'height') is not None, getattr(self, 'weight') != None:
      return True
    return False


## TODO: ABSTRACT
class WhatIAteRequest(Request):
  def __init__(self, api, intent, session):
    self.parse_slots(intent)
    self.api = api
    self.card_title = 'WhatIAte'
    self.servings = 1

  def reprompt_text(self):
    return False
    if self.is_valid:
      return self.speech_output()
    else:
      return "I'm not sure what did you eat" \
              "You can tell me for example, I ate 4 donuts"

  def speech_output(self):
    try:
      calories = self.api.add_food(getattr(self, 'food_name'))
      return "Ok, you just had" + calories + " calories"
    except RuntimeError:
      return "I'm having troubles communicating with the server. Please try again later."  

def what_I_ate(api, intent, session):
  should_end_session = False
  what_I_ate_request = WhatIAteRequest(api, intent, session)  
  return build_response({}, build_speechlet_response(
        what_I_ate_request.card_title, what_I_ate_request.speech_output(), what_I_ate_request.reprompt_text(), should_end_session))


## TODO: ABSTRACT
class Exercise(Request):
  def __init__(self, API, intent, session):
    self.parse_slots(intent)
    self.api = api
    self.card_title = 'Exercise'

  def reprompt_text(self):
    if self.is_valid:
      return self.speech_output()
    else:
      return "I'm not sure what exercise did you do" \
              "You can tell me for example, I played yoga for an hour"

  def speech_output(self):
    try:
      self.api.add_food(getattr(self, 'exercise_name'), getattr(self, 'duration'))
      return "Good for you"
    except RuntimeError:
      return "I'm having troubles communicating with the server. Please try again later."  

def exercise(api, intent, session):
  should_end_session = False
  exercise = Exercise(api, intent, session)  
  return build_response({}, build_speechlet_response(
        exercise.card_title, exercise.speech_output(), exercise.reprompt_text(), should_end_session))

class SofiaAPI:
  def __init__(self, intent_request, session):
    self.session = session
    self.fs = Fatsecret(oauth_consumer_key, oauth_secret_key)
    self.calorie_count = 0
    # self.request_date = datetime.strptime(intent_request['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

  # ------- Interface with the Intents ----------
  #def save_exercise(self, exercise_name, duration):
    #method = "method":"exercises.get"
   # response = encode([method])
   # if response is not None:
   #     exercise_name = response.exercise_types.exercise[0].exercise_name
   # method = "exercise_entries.commit_day"
   # #return encode([method, self.auth_token])

  def calculate(self, response_type):
    if self.calorie_count < 500:
        return "You have eaten way too little today! Only "+ calorie_count + " calories!"
    elif self.calorie_count < 1000 and calorie_count > 500:
        return "You are doing well today. You have eaten "+ calorie_count + " calories!"
    elif self.calorie_count > 1000:
        return "You have eaten way too much, you fatty!"

  def add_food(self, food_name):
    foods = self.fs.foods_search(food_name)
    if foods is not None:
        food_description = foods[0]['food_description']
        print(food_description)
        food_id = foods[0]['food_id']
        food_name = foods[0]['food_name']
        #self.fs.food_entry_create(food_id, food_name, 0, 1, "breakfast", date=None)
        print(food_description)
        return self.get_calories(food_description)
    return "Could not find this food type."

  def get_calories(self, str):
      index = str.find("Calories: ")
      if index != -1:
        str = str[index+9: index+13]
        cals = str.strip(' ')
        self.calorie_count = self.calorie_count + int(cals)
      else:
          return 0

  def configure_me(self, height, weight, age, gender):
      return "2000"
    # self.fs.profile_create(user_id=None)
    # if weight:
    #     if height:
    #         return self.set_weight(weight, height)
    #     else:
    #         return self.set_weight(weight, 180)

  def set_weight(self, weight, height):
      self.fs.weight_update(weight, date=None, weight_type='kg', height_type='cm', goal_weight_kg=None, current_height_cm=None, comment=None)



# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_help_response():
  """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
  configure_me_msg = "You can tell me your height, weight, age and gender so that I can help you plan your calories " 
  what_i_ate_msg = "or, you can tell if you ate something "
  calculate_msg = "or even ask me how many calories you had today "
  card_title = "Help"
  speech_output = "Hey, Sofia here, " + configure_me_msg + what_i_ate_msg + calculate_msg + ". Yes, I know I am cool"
                  
  # If the user either does not reply to the welcome message or says something
  # that is not understood, they will be prompted again with this text.
  reprompt_text = configure_me_msg + what_i_ate_msg + calculate_msg

  should_end_session = False
  return build_response({}, build_speechlet_response(
      card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
  """ If we wanted to initialize the session to have some attributes we could
  add those here
  """

  session_attributes = {}
  card_title = "Welcome"
  speech_output = "Welcome to Sofia! " \
                  "Please tell me your height, weight, age and gender" \
                  "so that I can help you plan your calories"
  # If the user either does not reply to the welcome message or says something
  # that is not understood, they will be prompted again with this text.
  reprompt_text = "Please tell me your height, weight, age and gender" \
                  "so that I can help you plan your calories"
  should_end_session = False
  return build_response(session_attributes, build_speechlet_response(
      card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}

# Alexa Intent (ConfigureMe)
def configure(api, intent, session):
  """ Configures user data
  """
  should_end_session = False
  configure_me_request = ConfigureMeRequest(api, intent, session)  
  return build_response({}, build_speechlet_response(
        configure_me_request.card_title, configure_me_request.speech_output(), configure_me_request.reprompt_text(), should_end_session))

# Alexa Intent (Calculate)
def calculate(api, intent, session):
  should_end_session = False
  calculate_request = CalculateRequest(api, intent, session)  
  return build_response({}, build_speechlet_response(
        calculate_request.card_title, calculate_request.speech_output(), calculate_request.reprompt_text(), should_end_session))

def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    api = SofiaAPI(intent_request, session)

    # Dispatch to your skill's intent handlers
    if intent_name == "ConfigureMe":
        return configure(api, intent, session)
    elif intent_name == "WhatIAte":
        return what_I_ate(api, intent, session)
    elif intent_name == "Exercise":
        return exercise(api, intent, session)
    elif intent_name == "Calculate":
        return set_color_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.85e484a6-4f2d-4479-b4da-9531ca7ce86e"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


event = json.loads("{\"session\":{\"sessionId\":\"SessionId.e17cc3f0-94aa-4b47-a30a-55bf8be958ac\",\"application\":{\"applicationId\":\"amzn1.ask.skill.85e484a6-4f2d-4479-b4da-9531ca7ce86e\"},\"attributes\":{},\"user\":{\"userId\":\"amzn1.ask.account.AFHYM6OD3H6B47CWKJBUX3SUJRAQAGGULBZS3LLZRTVWIHTFSREZ5JYATHVYV5KJM2IJOW7GRJRU55IOWOREMVQGAC4Q2YP7CYE2ETQKK2LUGOPFOCJWJOUQLIDUSYL5W6AGQTLZKAPVTYTHNA7HHPCWWVW4M33BUECLFOCLFOWD5JQ6M3HAIDVXRJTJ7HGMGECE7L2EYNTUB6A\"},\"new\":true},\"request\":{\"type\":\"IntentRequest\",\"requestId\":\"EdwRequestId.8fc14d74-595d-4d25-b1ce-27c2db537db2\",\"locale\":\"en-US\",\"timestamp\":\"2017-07-21T13:39:03Z\",\"intent\":{\"name\":\"WhatIAte\",\"slots\":{\"food_name\":{\"name\":\"food_name\",\"value\":\"donut\"},\"servings\":{\"name\":\"servings\"}}}},\"version\":\"1.0\"}")
lambda_handler(event, None)