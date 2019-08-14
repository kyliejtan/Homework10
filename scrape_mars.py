# Dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import re
import requests
import pandas as pd


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()
    
    # Scraping NASA Mars News
    news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(news_url)
    
    latest_news_title = browser.find_by_tag("div[class='content_title']").first.text
    latest_news_p = browser.find_by_tag("div[class='article_teaser_body']").first.text
    latest_news_link_html = browser.find_by_tag("div[class='image_and_description_container']").html
    news_soup = BeautifulSoup(latest_news_link_html, "html.parser")
    latest_news_url = "https://mars.nasa.gov" + news_soup.a["href"]
    
    # Scraping JPL Featured Mars Image
    jpl_url= "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)

    latest_mars_image_html = browser.find_by_tag("li[class='slide']").html
    jpl_soup = BeautifulSoup(latest_mars_image_html, "html.parser")
    latest_mars_image_url = "https://www.jpl.nasa.gov" + jpl_soup.a["data-fancybox-href"]
    
    # Scraping Mars Weather
    mars_weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(mars_weather_url)
    mars_weather_html = browser.find_by_tag("p[class='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text']").html
    weather_soup_text = BeautifulSoup(mars_weather_html, "html.parser").text
    weather_first_split = ("S" + weather_soup_text.split("InSight s")[1])
    mars_weather_string = weather_first_split.split("hPa")[0] + "hPa"
    
    # Scraping Mars Facts
    mars_facts_url = "https://space-facts.com/mars/"
    tables = pd.read_html(mars_facts_url)
    mars_facts_df = tables[1]
    mars_facts_df.columns = ["Description", "Value"]
    mars_facts_df = mars_facts_df.set_index("Description")
    mars_facts_html = mars_facts_df.to_html()
    
    # Scrpaing Mars Hemisphere Images
    mars_hemispheres_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(mars_hemispheres_url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    hemisphere_img_urls = []

    hemisphere_names = ["Cerberus", "Schiaparelli", "Syrtis", "Valles"]
    ind = 0

    for i in range(4):
    
        browser.click_link_by_partial_text(hemisphere_names[ind])
        html = browser.html
        soup = BeautifulSoup(html, "html.parser")
        title_text = browser.find_by_tag("h2[class='title']").text.split(" Enhanced")[0]
        img_text = str(soup.find_all("img", class_="wide-image")[0])
        img_url = 'https://astrogeology.usgs.gov' + img_text.split('src="')[1].split('"/>')[0]
    
        title_link_dict = {"title": title_text, "img_url": img_url}
        hemisphere_img_urls.append(title_link_dict)
    
        browser.visit(mars_hemispheres_url)
        ind+=1   
        
    # Storing scraped data in a dictionary
    mars_data = {"news_title": latest_news_title, 
                 "news_p": latest_news_p,
                 "news_url": latest_news_url,
                 "featured_image_url": latest_mars_image_url,
                 "mars_weather": mars_weather_string,
                 "mars_facts_table": mars_facts_html,
                 "hemisphere_image_urls": hemisphere_img_urls
    }
    
    # Returning scraped data
    return mars_data
