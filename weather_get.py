import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import json
import datetime as dt
from api import Api
import config_detector as cf


class get_weather_forecast(object):
    def __init__(self):        
        #initiate api
        self.api = Api(cf.api_key)

    
    def queryWeather(self):
        #set franulalirty of Api (options: daily, hourly, 3hourly
        self.api.set_granularity('hourly')
        # Query by lat/lon
        self.forecast = self.api.get_forecast(lat=cf.lat, lon=cf.lon, units = "M")
        # To get a daily forecast of temperature, and precipitation. snow:
        self.forecast_data = self.forecast.get_series(['temp','precip','snow_depth','wind_dir','wind_spd'])

    def parse_weather(self):
        self.store_list = []
        self.temp = []
        self.datetime = []
        
        for item in self.forecast_data:
            store_details = {"temp":None, "precip":None, "datetime":None}
            store_details['temp'] = item['temp']
            self.temp.append(item['temp'])
            
            store_details['precip'] = item['precip']
            
            
            store_details['datetime'] = item['datetime']
            self.datetime.append(item['datetime'])

            
            self.store_list.append(store_details)

        return self.temp, self.datetime;
    
    def save_data(object):
        object.queryWeather()
        # get_weather_forecast.plot()
        temp, datetime = object.parse_weather()

        #import date and hour and then use that for x-axis
        now = dt.datetime.now()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(datetime, temp)
        plt.axhline(y=0, color = 'r', linestyle = ':')
        plt.title('Temperature Forecast at ' + cf.location + ' (Device #' + cf.dev + ')')
        plt.xlabel("Time")
        plt.ylabel("Temperature ($^\circ$C)")
        plt.xlim([datetime[0], datetime[-1]])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m -%H:%M'))
        fig.autofmt_xdate()
        save_filename = 'weather/weather_' + now.strftime("%d-%m-%Y") + '.jpg'
        plt.savefig(save_filename, figsize = (3.6, 3.6) , dpi = 300 )
        return save_filename
            


