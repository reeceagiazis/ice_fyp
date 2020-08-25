from weatherbit.api import Api
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
api_key = "b5c28d04b9bf4e8f80836b1c1ec446af"
lat = -36.8658814
lon = 147.2869802

api = Api(api_key)

#set franulalirty of Api (options: daily, hourly, 3hourly
api.set 

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