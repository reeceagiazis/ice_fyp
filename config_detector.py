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
