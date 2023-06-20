"""Web Scraper for 'https://pitchfork.com/reviews/best/tracks'

This web scraper uses the BeautifulSoup library to get the title and 
artist(s) from all entries on the Best New Songs page of the music 
review website Pitchfork.
"""

import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import HTTPError

# Allow printing of messages
verbose = False

def get_track(item_link):
    """Gets track information from 'Pitchfork Best New Songs' entry

    Parameters
    ----------
    item_link (bs4.element.Tag): html <a> element (hyperlink) with 
    attribute class="title-link" or "track-collection-item__track-link"

    Returns
    -------
    list: a list of 2 strings representing title and artist
    """
    
    #Get title string in <h2> element
    title_raw = item_link.h2.string
    #Remove unwanted characters 
    title = title_raw.translate({ord(i): None for i in "“”\""})
    #Get list of artists in <li> elements of the <ul> parent element
    artist_list = item_link.ul.find_all("li")
    #Join multiple artists into one string
    artists = ", ".join([artist.string for artist in artist_list])
    
    return title, artists

def scrape_songs(start_page=1, end_page=300, verbose=True):
    """Gets songs from 'Pitchfork Best New Songs' pages
    
    Parameters
    ----------
    start_page (int): page number to start at.
        default=1
    end_page (int): page number to stop at.
        default=300
    verbose (bool): Boolean to allow printing messages.
        default=True

    Returns
    -------
    dataframe: pandas DataFrame with 2 columns representing title and artist
    """

    #Initialize empty list with header
    all_tracks = [('title', 'artist')]
    #Set page number to starting page
    page_no = start_page
    if not isinstance(start_page, int):
        raise ValueError("Page number must be an integer.")
    elif start_page<=0:
        raise ValueError("First page number must be 1 or higher.")     
    #Set page number to end on
    end_page = end_page
    if not isinstance(end_page, int):
        raise ValueError("Page number must be an integer.")
    elif end_page<start_page:
        raise ValueError("Final page number must be higher than the first page number.")

    while page_no<=end_page:
        url = f"https://pitchfork.com/reviews/best/tracks/?page={page_no}"
        #Try opening url. After reaching the final page, urlopen will raise HHTPError.
        try: 
            page = urlopen(url)
            if verbose:
                print(f"Getting tracks from page {page_no}...")
        except HTTPError:
            if verbose:
                print(f"Finished scraping at page {page_no-1}.")
            break
            
        #read url page and parse     
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        #find links containing track information
        item_links = soup.find_all("a",
                                   {"class": 
                                    ["title-link",
                                     "track-collection-item__track-link"
                                    ]})
        #extract information as strings and add to dataframe
        tracks = [get_track(item_link) for item_link in item_links] 
        all_tracks = all_tracks+tracks
        #go to the next page
        page_no += 1
    else:
        if verbose:
            print(f"Page limit {end_page} reached.")
        
    return all_tracks
    
#get songs and write to json file
songs = scrape_songs()

with open("songs.json", "w") as outfile:
    json.dump(songs, outfile)

#TODO: Could generalize for albums and reissues.