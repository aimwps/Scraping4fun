import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil.parser import parse
import matplotlib.pyplot as plt



def get_page_data(input_url):
    # request url
    page = requests.get(url=input_url)

    # create a BeautifulSoup object
    soup = BeautifulSoup(page.content, 'html.parser')

    #page title -- WORKS
    title = soup.find('title')
    # data['title'] = title.string


    #get rating -- WORKS
    ratings_container = soup.find_all(class_='lister-item-content')
    ratings = []
    for movie in ratings_container:
        rating_div = movie.find(class_="inline-block ratings-imdb-rating")
        if rating_div !=None:
            rating = float(rating_div.attrs.get("data-value"))
            ratings.append(rating)
        else:
            ratings.append("NaN")


    #release-date



    #get genre --WORKS
    genre_container = soup.find_all(class_='genre')
    gr = [title.get_text() for title in genre_container]
    gr = [title.split('\n') for title in gr]
    genre = [title[1] for title in gr]




    #get titles -- WORKS
    chart_list = soup.find_all(class_="lister-item-content")
    chart_list = []
    for movie in chart_list:
        chart_div = movie.find(class_="lister-item-index unbold text-primary").get_text()
        chart_list.append(int(chart_div))





    titles_container = soup.find_all(class_= "lister-item-header")
    titles = [title.get_text() for title in titles_container ] #loop to getText in days_container
    titles = [title.split('\n') for title in titles] #split by \n
    titles_names = [title[2] for title in titles] #split by \n




    #Actors & Directors
    movie_list = soup.find_all(class_="lister-item-content")
    actor_links_by_movie = [movie.select('a[href*="/name"]') for movie in movie_list]
    actor_names_by_movie = [[href_link.get_text() for href_link in movie_list] for movie_list in actor_links_by_movie]
    directors =[] ## This one for PD
    actors =[] ## This one for pd
    for movie in actor_names_by_movie:
        if len(movie)>0:
            directors.append(movie[0])
            actors.append(", ".join(movie[1:]))
        else:
            directors.append("NaN")
            actors.append("NaN")

    ####### duration ########

    dur_movies = soup.find_all(class_='lister-item-content')
    movie_durs =[] ###this one
    #print(len(dur_movies))
    for movie in dur_movies:

        duration_span = movie.find(class_="runtime")
        if duration_span != None:
            get_text = duration_span.get_text()
            get_int_text = "".join([i for i in get_text if i.isnumeric()])
            movie_durs.append(int(get_int_text))
        else:
            movie_durs.append("NaN")


    #filming date -- WORKS
    film_release = soup.find_all(class_='lister-item-content')
    release_year =  []
    for movie in film_release:
        year_div = movie.find(class_='lister-item-year text-muted unbold')
        if year_div != None and len(year_div.get_text()) > 4:
            get_ints = [i for i in year_div.get_text() if i.isnumeric()]
            #print(get_ints)
            year = "".join(get_ints[0:4])
            release_year.append(year)
        else:
            release_year.append("NaN")



    return [chart_list,titles_names, release_year, movie_durs, genre, ratings,directors,actors]

## returns the lists of data for the first 50
first_50 = get_page_data("https://www.imdb.com/search/title/?genres=western&genres=Adventure&explore=title_type,genres&ref_=adv_explore_rhs")
## returns the lists of data for the second 50
second_50 = get_page_data("https://www.imdb.com/search/title/?genres=western,adventure&start=51&explore=title_type,genres&ref_=adv_nxt")

# Combines them both into a dictionary containing all 100
data_dict = {'Chart Number': first_50[0]+second_50[0],
                    'Title': first_50[1]+second_50[1],
                    'Release Date': first_50[2]+second_50[2],
                    'Duration(min)': first_50[3]+second_50[3],
                    'Genre': first_50[4]+second_50[4],
                    'Rating': first_50[5]+second_50[5],
                    'Director': first_50[6]+second_50[6],
                    'Actors': first_50[7]+second_50[7]}

# creates dataframe from the dictionary
df = pd.DataFrame(data_dict)
