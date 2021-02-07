from bs4 import BeautifulSoup
import urllib.request
import sqlite3
import smtplib
import re


# TODO: Parse mask price
user_agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.487'}

#search_name = input("Enter the product: ")
search_name = "face masks"
search_name = search_name.lower()

keyword = search_name.split()
keyword = '+'.join(keyword)
seach_url = f"https://www.amazon.com/s?k={keyword}"

def get_url(url):
    req_url = urllib.request.Request(url, data=None, headers=user_agent)
    page = urllib.request.urlopen(req_url).read()
    soup = BeautifulSoup(page, "html.parser")
    return soup

soup = get_url(seach_url)

product_urls = soup.find_all("a", class_="a-link-normal a-text-normal")

for url in product_urls:
    product_url = "https://www.amazon.com/" + url.attrs['href']
    print(product_url)

product_names = soup.find_all("span", class_="a-size-base-plus a-color-base a-text-normal")
for name in product_names:
    name.get_text()

product_prices = soup.find_all(lambda tag: tag.name == "span" and tag.get('class') == ['a-price'])
count = 0
for price in product_prices:
    price = price.get_text()
    price = re.sub("\\b\$\d+.\d+", '', price)
    price = re.sub('\$|\.', '', price)
    print(price)


# TODO: Send email alerts to users


# TODO: Database for daily checker
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


# TODO: Vaccine status of employees


# TODO: Scrape for general COVID data in the country
    # *: Information about businesses in this part of town has .. covid cases
    # *: leveraging data that we have to enhance our app.

# TODO: Vaccine status of employees

# TODO: Scrape for general COVID data in the country
