############################################
# host/port binding for http server
HOST = '127.0.0.1'
PORT = 5000
############################################

from flask import Flask, request, render_template
import urllib
import plivohelper
import os
from xml.dom import minidom

WEATHER_API_URL = "http://weather.yahooapis.com/forecastrss?p="
WEATHER_API_NS = "http://xml.weather.yahoo.com/ns/rss/1.0"


def fetch_weather(zipcode):
    weather_url = WEATHER_API_URL + zipcode
    f = urllib.urlopen(weather_url)
    weather_xml = f.read()
    return weather_xml


def parse(xml):
    dom = minidom.parseString(xml)
    conditions = dom.getElementsByTagNameNS(WEATHER_API_NS,
        'condition')[0]
    location = dom.getElementsByTagNameNS(WEATHER_API_NS,
        'location')[0]
    return {
        'location': '%s, %s' % (location.getAttribute('city'),
            location.getAttribute('region')),
        'conditions': conditions.getAttribute('text'),
        'temp': conditions.getAttribute('temp')
    }    

response_server = Flask("ResponseServer")
response_server.debug = True

"""
This is a simple example which demonstrate how easy you can build a light HTTP
server using Flask which will return formatted XML to command the Plivo Server

By default the HTTP Server will be listening on http://127.0.0.1:5000

The following URLs are implemented:
    * /answered/
    * /weather/
"""


@response_server.route('/weather/', methods=['GET', 'POST'])
def weather():
    # Get destination from url query string:
    # 'node' : destination
    # 'Digits' : input digits from user
    if request.method == 'POST':
        dtmf = request.form.get('Digits', -1)
    else:
        dtmf = -1
    try:
        dtmf = int(dtmf)
    except ValueError:
        dtmf = -1
    
    zipcode = str(dtmf)
    zipcode = zipcode.replace('#', '').replace('*', '')[:5]
    if len(zipcode)!=5: #todo check zipcode format
        r = plivohelper.Response()
        r.addSpeak("Invalid Zipcode")
    else:
        print "zipcode %s" % zipcode
        r = plivohelper.Response()
        xml_weather = fetch_weather(zipcode)
        if xml_weather and xml_weather.find('City not found')==-1:
            weather = parse(xml_weather)
            r.addSpeak("It is currently %s degrees fahrenheit and %s in %s." %
                (weather['temp'], weather['conditions'], weather['location']))
        else:
            r.addSpeak("Error getting the weather forecast for zipcode %s." %
                zipcode)

    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)
    

@response_server.route('/answered/', methods=['GET', 'POST'])
def answered():
    # Get destination from url query string:
    # 'node' : destination
    # 'Digits' : input digits from user
    
    r = plivohelper.Response()
    g = r.addGetDigits(numDigits=5,
               action='http://127.0.0.1:5000/weather/')
    g.addSpeak("Welcome to Plivo Weather Forecast")
    g.addSpeak("please enter your Zip Code")

    print "RESTXML Response => %s" % r
    return render_template('response_template.xml', response=r)



if __name__ == '__main__':
    if not os.path.isfile("templates/response_template.xml"):
        print "Error : Can't find the XML template : templates/response_template.xml"
    else:
        response_server.run(host=HOST, port=PORT)
