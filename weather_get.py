import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import json
from api import Api
import datetime as dt



class get_weather_forecast(object):
    def __init__(self, latitude, longitude):
        api_key = "b5c28d04b9bf4e8f80836b1c1ec446af"
        self.lat = latitude
        self.lon = longitude
        self.api = Api(api_key)
    
    def queryWeather(self):
        #set franulalirty of Api (options: daily, hourly, 3hourly
        self.api.set_granularity('hourly')
        # Query by lat/lon
        self.forecast = self.api.get_forecast(lat=self.lat, lon=self.lon, units = "M")
        # To get a daily forecast of temperature, and precipitation:
        self.forecast_data = self.forecast.get_series(['temp','precip'])
        print(self.forecast_data)
    

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

        print(self.store_list)
        return self.temp, self.datetime;

curr_weat = get_weather_forecast(-36.8658814, 147.2869802)
curr_weat.queryWeather()
# get_weather_forecast.plot()
temp, datetime = curr_weat.parse_weather()

#import date and hour and then use that for x-axis
hour_current = dt.datetime.now().hour
hour_plot = []

for n in range(len(temp)):
    hour_plot.append(hour_current + n)

plt.figure()
plt.plot(hour_plot, temp)
plt.show()


fig, ax = plt.subplots()
ax.plot('date', 'adj_close', data=temp)

# format the ticks
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(years_fmt)
ax.xaxis.set_minor_locator(months)

# round to nearest years.
datemin = np.datetime64(hour_plot['date'][0], 'H')
datemax = np.datetime64(hour_plot['date'][-1], 'H') + np.timedelta64(1, 'H')
ax.set_xlim(datemin, datemax)

# format the coords message box
ax.format_xdata = mdates.DateFormatter('%H')
ax.format_ydata = lambda x: '$%1.2f' % x  # format the price.
ax.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

plt.savefig('temperature_date.png')

