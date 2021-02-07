from bs4 import BeautifulSoup
import urllib.request
import sqlite3
import smtplib
import re
import itertools
from rich.table import Table
from rich.console import Console


# TODO: Parse mask price

user_agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.487'}

def search_query(search_name):
    search_name = search_name.lower()
    keyword = search_name.split()
    keyword = '+'.join(keyword)
    search_url = f"https://www.amazon.com/s?k={keyword}"
    return search_url

def get_url_soup(url):
    req_url = urllib.request.Request(url, data=None, headers=user_agent)
    page = urllib.request.urlopen(req_url).read()
    soup = BeautifulSoup(page, "html.parser")
    return soup


def get_product_url(soup):
    urls = []
    product_urls = soup.find_all("a", class_="a-link-normal a-text-normal")
    for url in product_urls:
        url = "https://www.amazon.com/" + url.attrs['href']
        urls += [url]
    return urls
        
def get_product_name(soup):
    names = []
    product_names = soup.find_all("span", class_="a-size-base-plus a-color-base a-text-normal")
    for name in product_names:
        name = name.get_text()
        names += [name]
    return names
        
def get_product_price(soup):
    prices = []
    product_prices = soup.find_all(lambda tag: tag.name == "span" and tag.get('class') == ['a-price'])
    for price in product_prices:
        price = price.get_text()
        price = re.sub("\\b\$\d+.\d+", '', price)
        price = re.sub('\$|\.', '', price)
        prices += [price]
    return prices


search_name = input("Enter the product to search: ")
search_url = search_query(search_name)
soup = get_url_soup(search_url)

urls = get_product_url(soup)
names = get_product_name(soup)
prices = get_product_price(soup)

wanted_price = 1000

table_id = 0
console = Console()
table = Table(show_header=True, header_style="bold magenta")
table.add_column("ID", style="bold", justify="center")
table.add_column("Product Name")
table.add_column("Price", justify="right")
table.add_column("Amazon URL", style="dim")


for (url, name, price) in itertools.zip_longest(urls, names, prices, fillvalue=""):
    table_id = table_id + 1
    formatted_price = "$" + price[:-2] + "." + price[-2:]   
    if int(price) > wanted_price:
        table.add_row(
            f"{table_id+1}",
            f"{name}",
            f"{formatted_price}",
            f"{url}")
    else:
        table.add_row(f"[yellow]{table_id+1}[/yellow]",
                      f"[yellow]{name}[/yellow]",
                      f"[yellow]{formatted_price}[/yellow]",
                      f"[yellow]{url}[/yellow]")

console.print(table)

# TODO: Send email alerts to users


# TODO: Database for daily checker
"""
CONNECTION = sqlite3.connect('emp.sqlite3')
cur = CONNECTION.cursor()
cur.execute('CREATE TABLE Employees(LastName TEXT, FirstName TEXT, CloseContact TEXT, Symptoms TEXT, COVIDTest TEXT)')
print("1 ----- I have been in close contact with anyone experiencing COVID symptoms or that has tested positive for COVID")
print("2 ----- I have been NOT in close contact with anyone experiencing COVID symptoms or that has tested positive for COVID")
closeContact = input("Please enter the following number (1 or 2) indicating the scenario that applies to you: ")
if closeContact == "1":
  lName = input("Please enter your last name: ")
  fName = input("Please enter your first name: ")
  cur.execute("INSERT INTO Employees (LastName, FirstName, CloseContact, Symptoms, COVIDTest) VALUES (?, ?, ?, ?, ?)", (lName, fName, "YES", "NA", "NA"))
  print("Please stay home and quarantine.")
"""

# TODO: Vaccine status of employees


# TODO: Scrape for general COVID data in the country
    # *: Information about businesses in this part of town has .. covid cases
    # *: leveraging data that we have to enhance our app.

# TODO: Vaccine status of employees

# TODO: Scrape for general COVID data in the country
