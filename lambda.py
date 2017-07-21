"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
from __future__ import print_function
from datetime import datetime, date, time
import urllib
import random
import string

# --------------- API Interface ----------------------

oauth_consumer_key = "oauth_consumer_key=88705826bc964b5185709b58777d9b34"
oauth_signature_method = "oauth_signature_method=HMAC-SHA1"
oauth_timestamp = time.time()
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
        return "With your height and weigth we calculate that you should consume daily: " + calories + "!"
      except RuntimeError:
        return "I'm having troubles communicating with the server. Please try again later."  
    else:
      return "I'm not sure what your height and weight is. Please try again."

  def is_valid(self):
    if self.height != None and self.weight != None:
      return True
    return False

class SofiaAPI:
  def __init__(self, intent_request, session):
    client = myfitnesspal.Client('intern_hackathon')
    self.session = session
    self.request_date = datetime.strptime(intent_request['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

  def send(self, data):
    req = urllib.request.Request(request_url, data)
    response = urllib.request.urlopen(req)
    html = response.read()
    return html

  def calculate_oauth_signature(self):
      # DON'T KNOW HOW TO DO THIS


  def encode(self, list):
    request_list = []
    request_list.append(oauth_consumer_key)
    request_list.append(oauth_signature_method)
    request_list.append(oauth_timestamp)
    request_list.append(oauth_nonce)
    request_list.append(oauth_version)
    request_list.append(format)

    request_list = sort(request_list)

    data = urllib.parse.urlencode(request_list)
    return send(data)



  # ------- Interface with the Intents ----------
  def save_exercise(self, exercise_name, duration):
    method = "method=exercises.get"
    response = encode([method])
    if response not null:
        exercise_name = response.exercise_types.exercise[0].exercise_name
    method = "exercise_entries.commit_day"
    #return encode([method, self.auth_token])


  def calculate(self, response_type):
    if calorie_count < 500:
        return "You have eaten way too little today! Only "+ calorie_count + " calories!"
    elif calorie_count < 1000 and calorie_count > 500:
        return "You are doing well today. You have eaten "+ calorie_count + " calories!"
    elif calorie_count > 1000:
        return "You have eaten way too much, you fatty!"

  def add_food(self, food_name, servings):
    method = "method=food.search"
    response = encode([method])
    if response not null:
        food_description = response.foods.food[0].food_description
        food_id = "food_id=" + response.foods.food[0].food_id
        food_name = "food_entry_name=" + response.foods.food[0].food_name
        method = "method=food_entry.create"
        serving_id = "serving_id=0"
        number_of_units = "number_of_units=1"
        meal = "meal=breakfast"
        response = encode([food_id, method, food_name, serving_id, number_of_units, meal, self.auth_token])
        get_calories(food_description)
        return food_description
    return "Could not find this food type."

  def get_calories(self, str):
      index = str.find("Calories: ")
      if index != -1:
        str(index, 4)
        cals = str.strip(['k','c', 'a', 'l', ' '])
        calorie_count = calorie_count + int(cals)
      else:
          return 0

  def configure_me(self, height, weight, age, gender):
    method = "method=profile.create"
    response = encode([method])
    self.auth_token = "oauth_token=" + response.profile.auth_token
    self.auth_secret = "oauth_secret=" + response.profile.auth_secret
    if weight:
        if height:
            return set_weight(weight, height)
        else:
            return set_weight(weight, 180)

    #return self.calculate("calories")

  def set_weight(self, weight, height):
      method = "method=weight.update"
      current_weight_kg = "current_weight_kg="+weight
      goal_weight_kg = "goal_weight_kg=100"
      current_height_cm = "current_height_cm="+height

      list = [method, current_height_cm, current_weight_kg, goal_weight_kg, self.oauth_token]
      return encode(list)



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
        return get_color_from_session(intent, session)
    elif intent_name == "Exercise":
        return get_color_from_session(intent, session)
    elif intent_name == "Calculate":
        return set_color_in_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
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
