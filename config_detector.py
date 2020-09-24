import configparser

def increment(string):
    string = int(string) + 1
    return string

configParser = configparser.RawConfigParser()   
configFilePath = 'detector.config'
configParser.read(configFilePath)
location = configParser.get('device_configuration', 'location')
dev = configParser.get('device_configuration', 'dev_no')
lat = configParser.get('device_configuration', 'lat')
lon = configParser.get('device_configuration', 'lon')
sender_email = configParser.get('device_configuration', 'email_address')
password = configParser.get('device_configuration', 'pw')
api_key = configParser.get('device_configuration', 'api_key')

#choice 1
subject_reset = configParser.get('option_reset', 'subject')
text_reset = configParser.get('option_reset', 'text')
reset_html = open("html/reset.html", "r")
html_reset = reset_html.read()

#choice 2
subject_toggle = configParser.get('option_toggle', 'subject')
text_toggle = configParser.get('option_toggle', 'text')
toggle_html = open("html/toggle.html", "r")
html_toggle = toggle_html.read()

#choice 3
subject_report = configParser.get('option_report', 'subject')
text_report = configParser.get('option_report', 'text')
report_html = open("html/report.html", "r")
html_report = reset_html.read()

#choice 4
subject_help = configParser.get('option_help', 'subject')
text_help = configParser.get('option_help', 'text')
help_html = open("html/help.html", "r")
html_help = help_html.read()

#trigger event
trigger_html = open("html/trigger.html", "r")
html_trigger = trigger_html.read()