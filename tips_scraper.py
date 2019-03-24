import json
import requests
from bs4 import BeautifulSoup as bs
import io
from fake_useragent import UserAgent
from dateutil import parser
from random import choice
from ip_fetcher import ip_fetcher

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

""" This function gets the member name and the ranking of the member"""
def state_ranking_extractor(link):
    try:
        a_body = page_getter("https://uberpeople.net" +link)
        state = a_body.select('.u-concealed')[0].text
        ranking = a_body.select('.userTitle')[0].text
    except:
        print("user data access is blocked, imputing default values")
        state = "USA"
        ranking = "New Member"

    return state, ranking

"""" This function is used to extract all content from the """
def thread_link_extractor(page):
    threads = []
    authors = []
    authors_link = []
    author_state = []
    author_ranking = []
    start_date = []
    replies = []
    views = []
    msg_pages = []
    for block in page.select('.structItem'):
        threads.append(block.select('.structItem-title')[0].a['href'])
        authors.append(block.select('.username ')[0].text)
        authors_link.append(block.select('.username ')[0]['href'])
        link = "https://uberpeople.net" + block.select('.username ')[0]['href']
        state, ranking = state_ranking_extractor(link)
        author_state.append(state)
        author_ranking.append(ranking)
        start_date.append(str(parser.parse(block.select('.structItem-startDate')[0].time['datetime']).date()))
        replies.append(int(block.select('dd')[0].text))
        views.append(block.select('dd')[1].text)
        try:
            msg_pages.append(int(block.select('.structItem-pageJump')[0].find_all('a')[-1].text))
        except:
            msg_pages.append(0)

    return threads, authors, authors_link, author_state, author_ranking, start_date, replies, views, msg_pages

def get_thread_messages(msg_page):

    date = []
    name = []
    status = []
    message = []

    for s in msg_page.find_all('div' ,class_ = "message-inner"):

        try:
            date.append(s.time['datetime'])
            name.append(s.h4.text)
            status.append(s.h5.text)
            message.append(s.find('div', class_="bbWrapper").text)
        except:
            continue

    return date, name, status, message





url = "https://uberpeople.net/forums/Gratuity/" #url we are trying to scrape
working_proxy = ip_fetcher()

#defining storage variables
threads = {}
working_proxy = eval(open('proxies.txt', encoding='utf-8').read())
main_page = page_getter(url)
num_pages = int(main_page.select('li[class="pageNav-page "]')[0].text)

uid = 1
for i in range(num_pages+1):
    try:
        link = url + f"page-{i}"
        page = page_getter(link)

        thread_link, authors, author_link, author_state, author_ranking, start_date, replies, views, msg_pages = thread_link_extractor(page)

        print(f"Scraping page {i}")
        for j in range(len(thread_link)):
            unique_id = f"tips_{uid}"
            threads[unique_id] = {
                'thread_link': thread_link[j],
                'author': authors[j],
                'author_link': author_link[j],
                'author_state': author_state[j],
                'author_ranking': author_ranking[j],
                'start_date': start_date[j],
                'no_replies': replies[j],
                'no_views': views[j],
                'messages': {}
            }
            #print(threads)
            print(f"scraping thread number {uid}")
            num_pages_thread = msg_pages[j]
            uid += 1
            msg = 1

            for k in range(num_pages_thread+1):
                thread_page_link = "https://uberpeople.net" + thread_link[j] + f"page-{k}"
                thread_page = page_getter(thread_page_link)
                date, name, status, message = get_thread_messages(thread_page)

                for l in range(len(name)):
                    msg_id = f'msg_{msg}'
                    threads[unique_id]['messages'][msg_id] = {
                        'date': date[l],
                        'user': name[l],
                        'user_status': status[l],
                        'message': message[l],
                    }
                    print(f"scraping message number {msg}")
                    msg += 1

            with io.open('test_tips.txt', 'w', encoding='utf-8') as f:
                f.write(json.dumps(threads, ensure_ascii=False))

    except:
        print(f"loop failed at page-{i} thread-{uid} message-{msg}")
        continue