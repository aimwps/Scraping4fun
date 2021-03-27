import requests
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import numpy as np
week_days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
today_date = dt.date.today().weekday()
today = week_days[dt.date.today().weekday()]


# Converts the day into a date

def get_date(day):
    day_idx = week_days.index(day)
    today_idx = dt.date.today().weekday()
    date = None
    if day_idx > today_idx:
        date = dt.date.today() + dt.timedelta(days=day_idx - today_idx)
    elif day_idx < today_idx:
        date = dt.date.today() + dt.timedelta(days=len(week_days[week_days.index(today):]) + day_idx)
    else:
        date = dt.date.today()
    return date

def get_celcius(f):
    return int(f*(5/9))


page = requests.get('https://forecast.weather.gov/MapClick.php?lat=37.777120000000025&lon=-122.41963999999996#.YFsuGEP7RhE')
soup = BeautifulSoup(page.content, 'html.parser')
content = soup.find(id="detailed-forecast-body")
#print(content)

c1 = list(content.children)[1:-1]


scraped = {"day_name": [], "report": [], "temp": []}
for child in c1:
    day_name_locator = child.find('div', class_="col-sm-2 forecast-label")
    day_name_tag = "b"
    day_name = day_name_locator.find(day_name_tag).text
    report = child.find('div', class_="col-sm-10 forecast-text").text
    temp = [int(temp) for temp in report.replace(".", " ").split(" ") if temp.isnumeric()][0]
    scraped["day_name"].append(day_name)
    scraped["report"].append(report)
    scraped["temp"].append(temp)

groups = {}


### For working out day and night indexes
for x, day in enumerate(scraped.get('day_name')):
    for y, night in enumerate(scraped.get('day_name')):
        if day in night and day != night:
            groups[day]=[x,y]

    if day == 'Today' or day == 'This Afternoon':
        if today in groups.keys():
            groups[today].insert(0,x)
        else:
            groups[today] =[x,None]
    elif day == 'Tonight':
        if today in groups.keys():
            groups[today].insert(1, x)
        else:
            groups[today] = [None, x]

### Check for missing days of weeks that are missing data:
for day in week_days:
    if day not in groups.keys():
        day_idx = scraped["day_name"].index(day)
        groups[day] = [day_idx]



### for consolodating the day and nights
pd_data = {"day":[], "date":[],"high": [], "low": [], "day_report": [], "night_report": [], }

for day, data in groups.items():
    if len(data) >= 2:
        pd_data["day"].append(day)
        pd_data["date"].append(get_date(day))
        pd_data["high"].append(get_celcius(scraped["temp"][data[0]]))
        pd_data["low"].append(get_celcius(scraped["temp"][data[1]]))
        pd_data["day_report"].append(scraped.get("report")[data[0]])
        pd_data["night_report"].append(scraped.get("report")[data[1]])
    else:
        pd_data["day"].append(day)
        pd_data["date"].append(get_date(day))
        pd_data["high"].append(get_celcius(scraped["temp"][0]))
        pd_data["low"].append(None)
        pd_data["day_report"].append(scraped.get("report")[data[0]])
        pd_data["night_report"].append(None)


for v in pd_data.values():
    print(len(v))


## add tags

pd_data['day_tag'] = ['"col-sm-2 forecast-label"' for i in range(7)]
pd_data['report_tag']=['"col-sm-10 forecast-text"' for i in range(7)]



df = pd.DataFrame(pd_data)



print(df)
