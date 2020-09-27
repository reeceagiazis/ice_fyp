import configparser

#increment the value of the string entered, used to update the event count in iceTestEmail
def increment(string):
    string = int(string) + 1
    return string

#sets up the read and write functionality to the config file of the device
configParser = configparser.RawConfigParser()   
configFilePath = 'detector.config'
configParser.read(configFilePath)

#device location settings
location = configParser.get('device_configuration', 'location')
dev = configParser.get('device_configuration', 'dev_no')
lat = configParser.get('device_configuration', 'lat')
lon = configParser.get('device_configuration', 'lon')

#email settings
sender_email = configParser.get('device_configuration', 'email_address')
password = configParser.get('device_configuration', 'pw')

#weatherbit api
api_key = configParser.get('device_configuration', 'api_key')

#choice: reset
subject_reset = configParser.get('option_reset', 'subject')
reset_html = open("html/reset.html", "r")
html_reset = reset_html.read()

#choice: toggle
subject_toggle = configParser.get('option_toggle', 'subject')
toggle_html = open("html/toggle.html", "r")
html_toggle = toggle_html.read()

#choice: report
subject_report = configParser.get('option_report', 'subject')
report_html = open("html/report.html", "r")
html_report = report_html.read()

#choice: help
subject_help = configParser.get('option_help', 'subject')
help_html = open("html/help.html", "r")
html_help = help_html.read()

#trigger event
trigger_html = open("html/trigger.html", "r")
html_trigger = trigger_html.read()