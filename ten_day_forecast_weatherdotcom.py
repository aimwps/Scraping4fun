import requests
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import numpy as np

## Matches the dates provided by weather.com format ("Wed 29") by finding
## the following 10 days dates from today and matching the "DD"
def date_calculator(date):
    today = dt.date.today()
    potential_dates = [today + dt.timedelta(days=i) for i in range(1,11)]
    date_day_str = [x for x in str(date).split() if x.isnumeric()][0]
    return_date = None
    for date in potential_dates:
        if date_day_str == str(date)[-2:]:
            return_date = date
    return return_date

## Calculates Celcius and reformats
def get_celcius(f_str):
    int_part = int(f_str[:-1])
    convert = int(int_part*5/9)
    format_c = f"{str(convert)}{f_str[-1]}C"
    return format_c

# The dictionary to store data I am trying to capture
pddata = {"date": [], "description":[], "low_temp":[], "high_temp":[], "wind_speed":[], "rain_percent":[]}

# Request the data from the website
page = requests.get('https://weather.com/weather/tenday/l/San+Francisco+CA?canonicalCityId=dfdaba8cbe3a4d12a8796e1f7b1ccc7174b4b0a2d5ddb1c8566ae9f154fa638c')

# soup the data
soup = BeautifulSoup(page.content, 'html.parser')

# Find the smallestm div that contains all the data I need
content = soup.find('div',class_="DailyForecast--DisclosureList--350ZO")


### Find all the days - the source code has a list of days wheather with an ID detailIndex + a number 0- 15 in length, we want the options  1-10
all_days = []
for i in range(1,11):
    detail = content.find(id=f"detailIndex{i}")
    all_days.append(detail)

# Locates the individual data points with in eachh detailIndex saves them to the dictionary
for day in all_days:
    #These all take the following format, acces the dictionary saving data for my dataframe.
        # each key has a list as a value, append the the found data into that list.
            # use bs4. find() to find the tag and then the class inside the tag.
                #
    pddata['wind_speed'].append(day.find('span', class_="Wind--windWrapper--1Va1P undefined").text)
    pddata['low_temp'].append(get_celcius(day.find('span', class_="DetailsSummary--lowTempValue--1DlJK").text))
    pddata['high_temp'].append(get_celcius(day.find('span', class_="DetailsSummary--highTempValue--3x6cL").text))
    pddata['date'].append(date_calculator(day.find('h2', class_="DetailsSummary--daypartName--1Mebr").text))
    pddata['description'].append(day.find('span', "DetailsSummary--extendedData--aaFeV").text)

    # The rain % is slighly different because it has no class but a generated "data-testid" I can use the select method instead of find.
            ## the tag type + a list containing the identifier all in quotes. 'span[data-testid="PercentageValue"]'
                ## it then converts it to a string and finds the numbers out of it  ising isnumeric (The percentage chance of rain)
                 ## as it is a list comprehension to to perform the loop through the string it returns a list.
                    ## access the firs and only element [0] which is the rain %

    pddata['rain_percent'].append([int(i) for i in str(day.select('span[data-testid="PercentageValue"]')) if i.isnumeric()][0])


## for checking list size before creating dataframe
check =[]
for ls in pddata.values():
    check.append(len(ls))
if check.count(check[0]) == len(check):
    df = pd.DataFrame(pddata)

print(df)
