import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from api import Api
import config_detector as cf

#Get Weather Forecast class that uses the weatherbit API and a library from github by wxflights and cacraig (https://github.com/weatherbit/weatherbit-python)
#to compile and use the weather data for the configured location
class get_weather_forecast(object):
    def __init__(self):        
        #initiate api
        self.api = Api(cf.api_key)
    
    #sets the time resolution of the service and receives a forecast and weather data based on the input coordinates
    def queryWeather(self):
        #set franulalirty of Api (options: daily, hourly, 3hourly
        self.api.set_granularity('hourly')
        # Query by lat/lon
        self.forecast = self.api.get_forecast(lat=cf.lat, lon=cf.lon, units = "M")
        # To get a daily forecast of temperature, and precipitation. snow:
        self.forecast_data = self.forecast.get_series(['rh','temp','precip','uv','snow_depth','wind_cdir_full','wind_spd','weather','snow6h','precip6h','clouds'])
        return self.forecast_data
    
 #saves a plot of the weather forecast for the next x hrs depending on licence level used   
    def save_data(object):
        object.queryWeather()
        # get_weather_forecast.plot()
        temp
        datetime = object.parse_weather()

        #import date and hour and then use that for x-axis
        now = dt.datetime.now()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(datetime, temp)
        plt.axhline(y=0, color = 'r', linestyle = ':') #plot 0 degree line
        plt.title('Temperature Forecast at ' + cf.location + ' (Device #' + cf.dev + ')') #add title 
        plt.xlabel("Time day-month-year H:M") #label x axis 
        plt.ylabel("Temperature ($^\circ$C)") #label y axis
        plt.xlim([datetime[0], datetime[-1]]) #set limits to that of time data
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m -%H:%M'))
        fig.autofmt_xdate()
        save_filename = 'weather/weather_' + now.strftime("%d-%m-%Y") + '.jpg'
        plt.savefig(save_filename, figsize = (3.6, 3.6) , dpi = 300 )
        plt.close('all')
        return save_filename
            

# weather = get_weather_forecast()
# info = weather.queryWeather()
# print(info[0]['temp'])
