"""
YELP Crawler
- Crawls deatils of yelp reviews of restaurants in multiple inner districts of Vienna
- 'end_url' can be adjusted for different 'neighborhoods' 
- Utilizes BeautifulSoup & concept of Python's generators
"""

#Import
import urllib.request
from bs4 import BeautifulSoup as soup
from collections import defaultdict as dd
import json

#Start URL, important: ends with "start="
base_url = "https://www.yelp.com/search?start="
start="0"
end_url = "&cflt=restaurants&l=p:AT-9:Wien::%5BJosefstadt,Landstra%C3%9Fe,Leopoldstadt,Margareten,Mariahilf,Naschmarkt,Neubau,Spittelberg,Wieden%5D="

##PIPELINE
#Generate next base url
def generate_urls_base(page, start):
    while True:
        page = base_url +start +end_url
        print("Seite:", page)
        yield page
        start = str(int(start) + 10)

#Generate next biz url
def generate_urls_biz(pages):
    for page in pages: 
        try: 
            page_soup = generate_soup(page)
            containers = page_soup.find_all('a', {"class":'biz-name js-analytics-click'})     
            if len(containers) is not 0:
                for i in containers:
                    page = i.get("href")
                    page = "https://www.yelp.com" + page    
                    yield page 
            else: 
                break
        except AttributeError: 
            break 
        
#Generate next review url within biz url
def generate_urls_review(pages):
    for page in pages:
        try: 
            while page:
                yield page
                page_soup = generate_soup(page)
                container = page_soup.find('a', {"class":'u-decoration-none next pagination-links_anchor'})
                page = container.get("href")
        except AttributeError: 
            continue

#Generate data            
def generate_data(urls): 
    for url in urls:
        page_soup = generate_soup(url)
        name, rating, price, typ, zip_c = generate_biz_details(page_soup)
        review_dict = generate_ratings(page_soup)            
        yield {"Name": name, 
               "Preiskategorie": price,
               "Rating": rating,
               "Type": typ, 
               "Address": zip_c,
               "Kommentare": review_dict
               }


##FUNCTIONS
#Generate Soup 
def generate_soup(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read()
    page_soup = soup(html, 'html.parser')
    return page_soup

#Generate Biz Details       
def generate_biz_details(page_soup): 
    #Find Attributes
    name = page_soup.find("h1")
    price = page_soup.find("span", {"class": "business-attribute price-range"})
    rating = page_soup.find("div", {"class": "biz-rating biz-rating-very-large clearfix"})
    typ = page_soup.find("span", {"class": "category-str-list"})
    zip_c = page_soup.find("span", {"itemprop": "postalCode"})
    #Get Attributes
    try: 
        name = name.get_text()
        price = price.get_text() 
        rating = rating.div.get("title") 
        typ = typ.get_text()
        zip_c = zip_c.get_text()
        return name, rating, price, typ, zip_c
    except AttributeError: 
        return None,None,None,None,None

#Generate Ratings
def generate_ratings(page_soup): 
    try:
        c_list = []
        dt_list = []
        stars_list = []
        og_list = []
        us_list = []
        comments = page_soup.find_all('p', {"lang":'en'})
        for c in comments:
            c = c.get_text()
            c_list.append(c)
        #Comment Stars and Date
        c_details = page_soup.find_all("div", {"class": "biz-rating biz-rating-large clearfix"})
        for cd in c_details:
            date = cd.span.get_text()
            stars = cd.img.get("alt")
            stars_list.append(stars)
            dt_list.append(date)
        #Comment Origin
        c_origins = page_soup.find_all("ul", {"class": "user-passport-info"})
        for og in c_origins:
            og = og.b.get_text()
            og_list.append(og)
        #Comment-Author: Number of reviews, friends, photos and elite
        c_userstats = page_soup.find_all("ul", {"class": "user-passport-stats"})
        for us in c_userstats:
            us = us.get_text()
            us_list.append(us)
        #Schließlich noch in ein DD
        comment_dict = dd()
        for i,(a,b,c,d,e) in enumerate(zip(c_list,stars_list,dt_list,og_list,us_list)):
            comment_dict[i] = a,b,c,d,e
        return comment_dict
    except AttributeError: 
        return None 

#Posts in .txt (json) speichern
def save_post(data):
       with open('txt/data.txt', 'a') as f:
           g = json.dumps(data)     
           print("Saved")
           f.write(g)
 

#MAIN   
#Main Program
if __name__ == "__main__":  
    pages = generate_urls_base(base_url, start) 
    frame_urls = generate_urls_biz(pages)
    core_urls = generate_urls_review(frame_urls)
    data = generate_data(core_urls)
    #Save   
    for d in data:
        save_post(d)
           