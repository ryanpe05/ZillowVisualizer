import pandas as pd
from datetime import datetime
from dateutil.parser import parse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import re

# Make this the path to your data, this code should work with "Metro & U.S" or "City" geographies
path_to_excel = "./Metro_Zhvi_AllHomes.csv"
# Add cities you're interested in here
interested_cities = ["Atlanta", "Denver"]

home_df = pd.read_csv(path_to_excel, encoding='latin-1')

# Find which column home values start
first_value = 0
date_format_dash = True
for col in home_df.columns:
	date_pattern = re.compile("[0-9]+-[0-9]+-[0-9]+")
	if date_pattern.match(col.strip()):
		date_format_dash = True
		break
	date_pattern = re.compile("[0-9]+/[0-9]+/[0-9]+")
	if date_pattern.match(col.strip()):
		date_format_dash = False
		break
	first_value += 1
x_data = home_df.columns[first_value:].tolist()
if date_format_dash == True:
	x_data = [datetime.strptime(x, "%Y-%m-%d") for x in x_data if x]
else:
	# Old style
	x_data = [datetime.strptime(x, "%m/%d/%y") for x in x_data if x]

# If you downloaded something other than Metro or City Data, you may have to change RegionName to be something else
# You may also need to change the variable 'interested_cities'
found_cities = home_df["RegionName"]
city_mapping = {}
# Map the cities we want to the ones available
for int_city in interested_cities:
	for found_city in found_cities:
		if int_city in found_city:
			city_mapping[int_city] = found_city
			break

cities = {}
fig, axs = plt.subplots(nrows=1, ncols=2)
ax = axs[0]
for city, found_city in city_mapping.items():
	# Convert data frame to list
	y_data = home_df[home_df.RegionName == city_mapping[city]].values.tolist()[0]
	# Get the price data only
	y_data = y_data[first_value:]
	max_y = max(y_data[0:int(len(y_data)*2/3)])
	max_ind = y_data.index(max_y)
	max_date = x_data[max_ind]
	post_max_min = min(y_data[max_ind:])
	percent_drop = 100*(1-float(post_max_min)/float(max_y))
	pr = "In {}, houses peaked at ${} on {} and fell to ${} afterwards, a decrease of {}%"
	print(pr.format(found_city, max_y, max_date, post_max_min, percent_drop))
	min_ind = y_data.index(post_max_min)
	# most recent value
	later_max = y_data[-1]
	change_since_high = 100*(1-float(max_y)/float(later_max))
	print("If you invested at the peak, your current return would be {}%".format(
		change_since_high))
	cities[found_city] = {
		"recession_drop": percent_drop,
		"pre_recession_high": max_y,
		"recession_low": post_max_min,
		"change_since_high": change_since_high
		}
	ax.plot(x_data, y_data, label=found_city)

# Set first subplot titles
ax.legend()
ax.set_title("Historical Housing Values")
ax.set_ylabel("'Typical' Home Price")
ax.set_xlabel("Year")
ax = axs[1]

# Set second subplot titls and x_ticks
labels = cities.keys()
x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars
recession_drops = []
change_since_high = []
x_data = []
for city, data in cities.items():
	x_data.append(city)
	recession_drops.append(data["recession_drop"])
	change_since_high.append(data["change_since_high"])
rects1 = ax.bar(x - width/2, recession_drops, width, label='Loss in Recession')
rects2 = ax.bar(x + width/2, change_since_high, width, label='Worst Case Gain')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Gains/Losses')
ax.set_title('Gains by City')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
plt.xticks(rotation=60)
fig.tight_layout()
plt.show()
