from bs4 import BeautifulSoup
import urllib.request
import requests
import sqlite3
import smtplib
import re
import itertools
from rich.table import Table
from rich.console import Console
from time import localtime, strftime

currentDate = strftime("%m-%d-%Y", localtime())
currentTime = strftime("%H:%M:%S %Z", localtime())

# TODO: Scrape product prices for 
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
        url = make_tiny(url)
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

def make_tiny(url_long): 
    tiny_url = ('http://tinyurl.com/api-create.php?' + urllib.parse.urlencode({'url':url_long}))   
    res = requests.get(tiny_url)
    return res.text

# TODO: Send email alerts to users

def send_mail(wanted_price):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(user="test.wu255@gmail.com", password="wearyourmask")

    subject = f"Price fell below {wanted_price}"
    low_price_product_links = open("low_price_products.txt").read()
    body = "Check the amazon links\n" + low_price_product_links

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        'test.wu255@gmail.com',
        'vlzz25800@gmail.com',
        msg
    )
    print("Emails have been sent!")

    server.quit()

# TODO: Database for daily checker
CONNECTION = sqlite3.connect('covidInfo.sqlite3')
cur = CONNECTION.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS Employees(EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT, LastName TEXT, FirstName TEXT, CloseContact TEXT, Symptoms TEXT, COVIDTest TEXT, Date TEXT, Time TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS EmployeesVaccine(EmployeeVaccineID INTEGER PRIMARY KEY AUTOINCREMENT, LastName TEXT, FirstName TEXT, FirstDose TEXT, SecondDose TEXT, Manufacturer TEXT, Date TEXT, Time TEXT)')

def employeeCheckIn():
    cur = CONNECTION.cursor()
    
    print("EMPLOYEE CHECK-IN")
    fName = input("Please enter your first name: ")
    lName = input("Please enter your last name: ")
    print("Have you been in close contact with someone experiencing COVID symptoms or that has tested positive for COVID? Enter '1' for 'YES' or '2' for 'NO'.")

    while True:
        closeContact = input("Please enter the following number (1 or 2) indicating the scenario that applies to you: ")
        if closeContact == "1":
            closeContact = "YES"
            break;
        elif closeContact == "2":
            closeContact = "NO"
            break;
        else:
            print("Sorry, that is not a valid input. Please enter either '1' or '2'.")
            continue
    print("Have you recently experienced symptoms of COVID including, but not limited to coughing, fever or chills, and shortness of breath? Enter '1' for 'YES' or '2' for 'NO'.")

    while True:
        covidSymptoms = input("Please enter the following number (1 or 2) indicating the scenario that applies to you: ")
        if covidSymptoms == "1":
            covidSymptoms = "YES"
            break;
        elif covidSymptoms == "2":
            covidSymptoms = "NO"
            break;
        else:
            print("Sorry, that is not a valid input. Please enter either '1' or '2'.")
            continue
    print("Have you recently tested positive for COVID? Enter '1' for 'YES' or '2' for 'NO'.")

    while True:
        covidTest = input("Please enter the following number (1 or 2) indicating the scenario that applies to you: ")
        if covidTest == "1":
            covidTest = "YES"
            break;
        elif covidTest == "2":
            covidTest = "NO"
            break;
        else:
            print("Sorry, that is not a valid input. Please enter either '1' or '2'.")
            continue

    cur.execute("INSERT INTO Employees(LastName, FirstName, CloseContact, Symptoms, COVIDTest, Date, Time) VALUES (?, ?, ?, ?, ?, ?, ?)", (lName, fName, closeContact, covidSymptoms, covidTest, currentDate, currentTime))
    CONNECTION.commit()
    cur.close()  


def employeeLookUp():
    cur = CONNECTION.cursor()    
    cur.execute("SELECT FirstName, LastName, CloseContact, Symptoms, COVIDTest, Date, Time FROM Employees")
    rows = cur.fetchall()    

    for row in rows:
        if row[2] == "YES":
            print("As of " + row[5] + " at " + row[6] + ", " + row[0] + ' ' + row[1] + " has been in close contact with someone experiencing COVID symptoms or that has tested positive for COVID.")
        if row[3] == "YES":
            print("As of " + row[5] + " at " + row[6] + ", " + row[0] + ' ' + row[1] + " has recently experienced symptoms of COVID including, but not limited to coughing, fever or chills, and shortness of breath.")
        if row[4] == "YES":
            print("As of " + row[5] + " at " + row[6] + ", " + row[0] + ' ' + row[1] + " has recently tested positive for COVID.")
    cur.close()


def showCovidRiskMenu():
    selection = ""
    while selection != "3":
        print("\n" + ('*' * 25) + "COVID RISK MENU" + ('*' * 25))
        print("1 - Employee check-in")
        print("2 - Search for employees that may introduce a risk for COVID")
        print("3 - Quit")
        selection = input("Please enter a menu number: ")
        if selection == "1":
            employeeCheckIn()
        elif selection == "2":
            employeeLookUp()
        elif selection == "3":
            break;
        else:
            print("That is not a valid option.")

# TODO: Vaccine status of employees
def employeeVaccineCheckIn():
    cur = CONNECTION.cursor()
    
    print("EMPLOYEE VACCINE CHECK-IN")
    fName = input("Please enter your first name: ")
    lName = input("Please enter your last name: ")
    print("Is this your first dose? Enter '1' for 'YES' or '2' for 'NO'.")

    while True:
        firstDose = input("Please enter the following number (1 or 2) indicating the scenario that applies to you: ")
        if firstDose == "1":
            firstDose = "YES"
            break;
        elif firstDose == "2":
            firstDose = "NO"
            break;
        else:
            print("Sorry, that is not a valid input. Please enter either '1' or '2'.")
            continue
    print("Is this your second dose? Enter '1' for 'YES' or '2' for 'NO'.")

    while True:
        secondDose = input("Please enter the following number (1 or 2) indicating the scenario that applies to you: ")
        if secondDose == "1":
            secondDose = "YES"
            break;
        elif secondDose == "2":
            secondDose = "NO"
            break;
        else:
            print("Sorry, that is not a valid input. Please enter either '1' or '2'.")
            continue

    if firstDose == "NO" and secondDose == "NO":
        print("You have not yet received any doses of your vaccine. This program will end.")
        cur.close()
        return(None)
    elif firstDose == "YES" or secondDose == "YES":
        vaccineManufacturer = input("Please specify the manufacturer of your vaccine: ")
        cur.execute("INSERT INTO EmployeesVaccine(LastName, FirstName, FirstDose, SecondDose, Manufacturer, Date, Time) VALUES (?, ?, ?, ?, ?, ?, ?)", (lName, fName, firstDose, secondDose, vaccineManufacturer, currentDate, currentTime))
        CONNECTION.commit()
        cur.close()  


def employeeVaccineLookUp():
    cur = CONNECTION.cursor()    
    cur.execute("SELECT FirstName, LastName, FirstDose, SecondDose, Manufacturer, Date, Time FROM EmployeesVaccine")
    rows = cur.fetchall()    
    for row in rows:
        if row[2] == "YES":
            print("As of " + row[5] + " at " + row[6] + ", " + row[0] + ' ' + row[1] + " has received his/her first dose of the " + row[4] + " vaccine.")
        if row[3] == "YES":
            print("As of " + row[5] + " at " + row[6] + ", " + row[0] + ' ' + row[1] + " has received his/her second dose of the " + row[4] + " vaccine.")
        if row[2] == "YES" and row[3] == "YES":
            print("As of " + row[5] + " at " + row[6] + ", " + row[0] + ' ' + row[1] + " has received both of his/her doses of the " + row[4] + " vaccine.")
    cur.close()


def showCovidVaccineMenu():
    selection = ""
    while selection != "3":
        print("\n" + ('*' * 25) + "COVID VACCINE MENU" + ('*' * 25))
        print("1 - Employee vaccine reporting")
        print("2 - Search for employees that have been received at least one dose of a COVID vaccine")
        print("3 - Quit")
        selection = input("Please enter a menu number: ")
        if selection == "1":
            employeeVaccineCheckIn()
        elif selection == "2":
            employeeVaccineLookUp()
        elif selection == "3":
            break;
        else:
            print("That is not a valid option.")


# TODO: Scrape for general COVID data in the country
    # *: Information about businesses in this part of town has .. covid cases
    # *: leveraging data that we have to enhance our app.

#! MENU
console = Console()

table = Table(show_header=True, header_style="bold magenta")
table.add_column("OPTION")
table.add_column("FUNCTION DESCRIPTION", justify="left")

table.add_row(
    "1", 
    "PARSE AMAZON FOR PPE PRICES"
)
table.add_row(
    "2",
    "SEND E-MAIL NOTIFICATIONS TO USERS"
)
table.add_row(
    "3",
    "EMPLOYEE DAILY CHECK IN OR SEARCH FOR EMPLOYEES THAT MAY INTRODUCE A RISK FOR COVID"
)
table.add_row(
    "4",
    "EMPLOYEE VACCINE REPORTING OR SEARCH FOR EMPLOYEES THAT HAVE BEEN VACCINATED"
)
table.add_row(
    "5",
    "PARSE THE WEB FOR GENERAL COVID DATA"
)
table.add_row(
    "6",
    "EXIT THE PROGRAM"
)

def showMainMenu():
    selection = " "
    while selection != "6":
        console.print(table)
        selection = input("Enter the function number you would like to execute: ")
        if selection == "1":
            #FUNCTION CALL TO PARSE AMAZON
            search_name = input("Enter the product to search: ")
            while True:
                wanted_price = input("Enter the wanted price: ")
                if wanted_price.isdigit():
                    wanted_price = int(wanted_price)
                    break
                else:
                    print("Please enter the price without the dollar sign and dot")
            search_url = search_query(search_name)
            soup = get_url_soup(search_url)

            urls = get_product_url(soup)
            names = get_product_name(soup)
            prices = get_product_price(soup)

            table_amz_id = 0
            console_amz = Console()
            table_amz = Table(show_header=True, header_style="bold magenta")
            table_amz.add_column("ID", style="bold", justify="center")
            table_amz.add_column("Product Name")
            table_amz.add_column("Price", justify="right")
            table_amz.add_column("Amazon URL")


            for (url, name, price) in itertools.zip_longest(urls, names, prices, fillvalue=""):
                table_amz_id = table_amz_id + 1
                formatted_price = "$" + price[:-2] + "." + price[-2:]
                if int(price) > wanted_price:
                    table_amz.add_row(
                        f"{table_amz_id}",
                        f"{name}",
                        f"{formatted_price}",
                        f"{url}")
                else:
                    with open("low_price_products.txt", "a") as file:
                        file.write(url + "\t" + formatted_price + "\n")
                    table_amz.add_row(f"[yellow]{table_amz_id}[/yellow]",
                                f"[yellow]{name}[/yellow]",
                                f"[yellow]{formatted_price}[/yellow]",
                                f"[yellow]{url}[/yellow]")
            console_amz.print(table_amz)            
        elif selection == "2":
            #FUNCTION TO CALL EMAIL
            while True:
                wanted_price = input("Enter the wanted price: ")
                if wanted_price.isdigit():
                    wanted_price = int(wanted_price)
                    break
                else:
                    print("Please enter the price without the dollar sign and dot")
            send_mail(wanted_price)
        elif selection == "3":
            showCovidRiskMenu()
        elif selection == "4":
            showCovidVaccineMenu()
        elif selection == "5":
            print("This function is currently in progress.")
            #FUNCTION TO CALL PARSING GENERAL WEB
        elif selection == "6":
            break;
        else:
            print("Sorry, that is not a valid input. Please try again: ")
showMainMenu()