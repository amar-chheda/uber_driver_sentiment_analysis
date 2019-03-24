"""This program scrapes the uber driver reviews from Indeed website"""

#imoprts all dependencies
import requests
from bs4 import BeautifulSoup as bs
from fake_useragent import UserAgent
from dateutil import parser
from random import choice
from ip_fetcher import ip_fetcher #refer to ip_fetcher.py
import pandas as pd

""" this function gets new set of IPs """
def new_ip(working_proxy):
    ip = choice(working_proxy)
    return ip

"""" This page gets the HTML body for the given link """
def page_getter(url):

    try:
        ip = new_ip(working_proxy)
        proxy = {'http': f'http://{ip}', 'https': f'https://{ip}', }  # creates a proxy JSON
        ua = UserAgent()  # gets a random user agent
        page = requests.get(url=url)
        soup = bs(page.content, "html.parser")
    except:
        print("Proxy IP failed! Finding new proxy to get you going.......")
        ip = new_ip(working_proxy)
        proxy = {'http': f'http://{ip}', 'https': f'https://{ip}', }  # creates a proxy JSON
        ua = UserAgent()  # gets a random user agent
        page = requests.get(url=url)
        soup = bs(page.content, "html.parser")

    return soup

""""fetches all the data from the review block"""
def review_block_fetcher(block):
    try:
        rating = block.select('.cmp-ratingNumber')[0].text
        location = block.select('.cmp-reviewer-job-location')[0].text
        date = parser.parse(block.select('.cmp-review-date-created')[0].text).date()
        try:
            pro = block.select('.cmp-review-pro-text')[0].text
        except:
            pro = ""
        try:
            con = block.select('.cmp-review-con-text')[0].text
        except:
            con = ""

        try:
            up_vote = block.find_all('span',{'name':"upVoteCount"})[0].text
        except:
            up_vote = 0
        try:
            down_vote = block.find_all('span',{'name':"downVoteCount"})[0].text
        except:
            down_vote = 0
        message = block.select('.cmp-review-text')[0].text
    except:
        print("something went wrong with the block fetcher function")

    return rating, location, date, pro, con, up_vote, down_vote, message

"""The main block starts from here"""

working_proxy = ip_fetcher()
reviews = {}
start = 0
msg = 1
pg = 1
base = "https://www.indeed.com"

#creating empty lists
rating = []
location = []
date = []
pro = []
con = []
up_vote = []
down_vote = []
message = []

"""Extracts all the reviews in the Indeed website pages"""
for i in range(135):
    try:
        extension = f"/cmp/Uber-Partner-Drivers/reviews?fjobtitle=Driver&start={start}"
        start += 20
        page = page_getter(base +extension)
        for block in page.select('.cmp-review-container'):
            ra, l, dat, pr, co, up_, down_, mes = review_block_fetcher(block)
            rating.append(ra) #driver ratings given on indeed
            location.append(l) #location where the review was written at
            date.append(dat) #date of writing the review
            pro.append(pr) #pros of the review
            con.append(co) #cons of the review
            up_vote.append(up_) #number of up_votes for the review
            down_vote.append(down_) #number of down_votes for the review
            message.append(mes) #the review message
            #converts the lists to a dataframe for processing
            reviews = pd.DataFrame({
                'ratings': rating,
                'location': location,
                'date': date,
                'pro': pro,
                'con': con,
                'up_vote': up_vote,
                'down_vote': down_vote,
                'message': message,
            })

            reviews.to_csv('indeed_uber_data_final.csv')

            print(f"scraping page-{pg}: message - {msg}") #ensuring the loop is working porperly
            msg += 1

        pg += 1

    except:
        continue

""" Similarly this block downloads all the independent contractor drivers from the website """"
start = 0
for i in range(82):
    try:
        extension = f"/cmp/Uber-Partner-Drivers/reviews?fjobtitle=Driver+(Independent+Contractor)&start={start}"
        start += 20
        page = page_getter(base + extension)
        for block in page.select('.cmp-review-container'):
            ra, l, dat, pr, co, up_, down_, mes = review_block_fetcher(block)
            rating.append(ra)
            location.append(l)
            date.append(dat)
            pro.append(pr)
            con.append(co)
            up_vote.append(up_)
            down_vote.append(down_)
            message.append(mes)

            reviews = pd.DataFrame({
                'ratings': rating,
                'location': location,
                'date': date,
                'pro': pro,
                'con': con,
                'up_vote': up_vote,
                'down_vote': down_vote,
                'message': message,
            })

            reviews.to_csv('indeed_uber_data_final.csv')

            print(f"scraping page-{pg}: message - {msg}")
            msg += 1

        pg += 1

    except:
        continue
