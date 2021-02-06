from bs4 import BeautifulSoup
import sqlite3
CONNECTION = sqlite3.connect('emp.sqlite3')
cur = CONNECTION.cursor()
cur.execute('CREATE TABLE Employees(LastName TEXT, FirstName TEXT, CloseContact TEXT, Symptoms TEXT, COVIDTest TEXT)')
# TODO: Parse mask price

# TODO: Send email alerts to users

# TODO: Database for daily checker
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
