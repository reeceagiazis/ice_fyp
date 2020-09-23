import configparser

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
subject_1 = configParser.get('option_1_text', 'subject')
text_1 = configParser.get('option_1_text', 'text')
html_1 = configParser.get('option_1_text', 'html')

#choice 2
subject_2 = configParser.get('option_2_text', 'subject')
text_2 = configParser.get('option_2_text', 'text')
html_2 = configParser.get('option_2_text', 'html')

#choice 3
subject_3 = configParser.get('option_3_text', 'subject')
text_3 = configParser.get('option_3_text', 'text')
html_3 = configParser.get('option_3_text', 'html')

#choice 4
subject_4 = configParser.get('option_4_text', 'subject')
text_4 = configParser.get('option_4_text', 'text')
html_4 = configParser.get('option_4_text', 'html')