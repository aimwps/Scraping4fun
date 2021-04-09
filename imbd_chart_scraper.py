import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil.parser import parse
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

def get_genre_urls():
    page = requests.get(url="https://www.imdb.com/chart/top/?ref_=nv_mv_250")
    soup = BeautifulSoup(page.content, 'html.parser')
    page_section = soup.find(id="sidebar")
    genre_links = page_section.find_all('li', class_="subnav_item_main")
    url_dict = {}
    for genre in genre_links:
        url = genre.find('a', href=True)
        genre_key = url.get_text().replace("\n", "").strip()
        url_dict[genre_key] = "https://www.imdb.com" + url['href'] + "&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=5aab685f-35eb-40f3-95f7-c53f09d542c3&pf_rd_r=BFTF5NMZ7QJX327P95J6&pf_rd_s=right-6&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_gnr_1"
    # for key, value in url_dict.items():
    #     print(key + " " + value)
    return url_dict




def get_page_data(input_url):
    page = requests.get(url=input_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    movie_split = soup.find_all(class_='lister-item-content')

    # Genres
    genres = [movie.find('span', class_="genre").get_text().replace("\n", "").strip() for movie in movie_split]

    # Get the rank by convert to an integer the findings of the rank located in the span and class. Take the text exluding the last as it is punctuation.
    movie_ranks = [int(movie.find('span', class_="lister-item-index unbold text-primary").get_text()[:-1]) for movie in movie_split]

    # Get the title
    movie_titles = [movie.find('a').get_text() for movie in movie_split]

    # Get release year
    release_date_unclean = [movie.find('span', class_="lister-item-year text-muted unbold").get_text() for movie in movie_split]
    release_date = [int("".join([i for i in movie if i.isnumeric()])) for movie in release_date_unclean]

    # get duration
    movie_durs_unclean =[movie.find(class_="runtime").get_text() for movie in movie_split]
    movie_durs = [int("".join([i for i in movie if i.isnumeric()])) for movie in movie_durs_unclean]

    movie_rating = [float(movie.find(class_="inline-block ratings-imdb-rating")["data-value"]) for movie in movie_split]

    #Actors & Directors
    stars_by_movie_unclean = [movie.select('a[href*="/name"]') for movie in movie_split]
    stars_by_movie = [[href_link.get_text() for href_link in movie_list] for movie_list in stars_by_movie_unclean]
    directors = [star[0] for star in stars_by_movie]
    actors =[", ".join([star for star in movie[1:]]) for movie in stars_by_movie]

    # Return data from page
    data_dict = {"genre": genres,
                 "genre_rank": movie_ranks,
                 "title": movie_titles,
                 "release_year": release_date,
                 "duration": movie_durs,
                 "ratings": movie_rating,
                 "director": directors,
                 "starring": actors,
                 }
    print(f"{genres[0].strip().zfill(50)}: genres:{len(genres)}, movie_ranks:{len(movie_ranks)}, movie_titles:{len(movie_titles)}, release_date:{len(release_date)}, movie_durs:{len(movie_durs)}, movie_rating:{len(movie_rating)},  directors{len(directors)}, actors:{len(actors)}")
    return data_dict



def data_length_validator(movie_data):
    invalid_fields = []
    for field, data in movie_data.items():
        if len(data)!= 50:
            invalid_fields.append(field)

    if len(invalid_fields) == 0:
        return (True, invalid_fields)
    else:
        return (False, invalid_fields)


def merge_data_dicts(list_of_dictionaries):
    all_data = {}
    for dict in list_of_dictionaries:
        #print(f"working on the dict: {dict}")
        for key, value in dict.items():
            #print(f"Current key {key}, current data{value}")
            if key in all_data.keys():
                current_data = all_data[key]
                #print(current_data)
                combined_data = current_data + value
                all_data[key] = combined_data
            else:
                #print(False)
                all_data[key] = value
        #print(all_data)
    return all_data

def gather_check_combine_web_data():
    get_urls = get_genre_urls()
    accepted_genres = []
    rejected_genres = []
    for genre, url in get_urls.items():
        movie_data_dict = get_page_data(url)
        check_data = data_length_validator(movie_data_dict)
        if check_data[0] == True:
            accepted_genres.append(movie_data_dict)
            print("Accepted Genre")
        else:
            rejected_genres.append((genre, check_data[0]))
            print("**********WARNING******* Rejected a Genre")
    combined_data = merge_data_dicts(accepted_genres)
    return combined_data



imdb = pd.DataFrame(gather_check_combine_web_data())
now = dt.date.today()
file_name = f"top_50_genre_movies_{now}.csv"
## Saves file by date scraper was run in the parent directory where scraper is located
imdb.to_csv(f'../{file_name}', index = False, header=True)
