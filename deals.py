STEAM_DEALS_URL = "http://store.steampowered.com/search/?specials=1&sort_by=&sort_order=ASC"


# twitter_auth.py should contain auth keys to access Twitter API
#
# OAUTH_TOKEN = ""
# OAUTH_SECRET = ""
# CONSUMER_KEY = ""
# CONSUMER_SECRET = ""
#
from twitter_auth import *
from twitter import *
from bs4 import BeautifulSoup
import urllib.request
import os
import re


def get_last_page(sales_link):
    try:
        souped_link = get_souped_page(sales_link)
        last_pages = souped_link.find_all("a", {"onclick": "SearchLinkClick( this ); return false;"})
        return int(last_pages[-2].string) + 1
    except IndexError:
        return 2


def get_souped_page(page_url):
    try:
        req = urllib.request.Request(page_url)
        req.add_header("Cookie", "birthtime=662688000;")
        f = urllib.request.urlopen(req)
        return BeautifulSoup(f.read().decode("utf-8"))
    except urllib.request.HTTPError:
        print("HTTP error")
    except urllib.request.URLError:
        print("URL error")


def get_app_data(app_page):
    appname = app_page.find("div", {"class": "apphub_AppName"}).string
    pct = app_page.find("div", {"class": "discount_pct"}).string[1:]
    price = app_page.find("div", {"class": "discount_final_price"}).string
    link = app_page.head.link["href"]
    return appname, price, pct, link


def make_message(app_page):
    souped_page = get_souped_page(app_page)
    appname, price, pct, link = get_app_data(souped_page)
    return appname + ", цена " + price + " #скидка " + pct + " " + link


def get_sales_list(sales_link):
    deals_url = []
    pages = get_last_page(sales_link)
    for page in range(1, pages):
        deals_souped = get_souped_page(sales_link + "&page=" + str(page))
        deals = deals_souped.find_all("a", {"class": "search_result_row"})
        for deal in deals:
            deals_url.append("http://store.steampowered.com/app/" + re.findall("\d+", deal["href"])[0] + "/")
    return deals_url


def save_sales_list(deals_list):
    list_new = open("list_new", "w")
    for item in deals_list:
        list_new.write("%s\n" % item)


def load_sales_list():
    list = open("list", "r")
    list_out = []
    for line in list:
        list_out.append(line.rstrip("\r\n"))
    return list_out


def diff_new_old(list_new, list):
    old_list = set(list)
    message_list = [x for x in list_new if x not in old_list]
    return message_list


def add_duplicate(link):
    add_to = open("list_new", "a")
    add_to.write("%s\n" % link)
    add_to.close()

t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

list_new = get_sales_list(STEAM_DEALS_URL)
save_sales_list(list_new)
list_old = load_sales_list()

messages_list = diff_new_old(list_new, list_old)

for message in messages_list:
    try:
        # print(make_message(message))
        t.statuses.update(status=make_message(message))
    except AttributeError:
        e = 1
    except TwitterHTTPError:
        add_duplicate(message)

os.remove("list")
os.rename("list_new", "list")
print("Done!")