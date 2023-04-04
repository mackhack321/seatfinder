from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import sys

MASTER_SCHEDULE_URL = "https://mybanner.msstate.edu/BannerExtensibility/customPage/page/msuPublicMasterSchedule"

SEMESTER = "Fall Semester 2023"

def getRawHTML(driver, code, num):
    driver.get(MASTER_SCHEDULE_URL)
    
    semDropdown = Select(driver.find_element("id", "pbid-msuSelectTerm"))
    semDropdown.select_by_visible_text(SEMESTER)

    subjDropdown = driver.find_element("id", "pbid-msuSelectSubject")
    subjDropdown.click()
    subjDropdown.send_keys(code)
    subjDropdown.send_keys(Keys.ENTER)

    driver.find_element("id", "pbid-msuTextCourseNumber").send_keys(num)

    driver.find_element("id", "pbid-msuButtonViewSections").click()

    sleep(0.30)

    html = driver.page_source
    return html

def getSeats(html, sectionToFind = "-1"):
    tableStrainer = SoupStrainer("table", attrs={"id": "msuMasterScheduleDataTable"}) # only parse the table
    soup = BeautifulSoup(html, "html.parser", parse_only=tableStrainer)
    table = soup.find("tbody")
    rows = table.findChildren("tr")
    
    for row in rows:
        cols = row.findChildren("td")

        if cols[0].text == "No records found matching search criteria.":
            print("The specified course does not exist\n")

        else:
            code = " ".join(cols[0].text.split(" - "))
            title = cols[5].text
            section = cols[1].text
            if sectionToFind != "-1" and section != sectionToFind: continue
            seatsTotal = cols[9].text
            seatsAvail = cols[10].text

            print(f"{code} {title}")
            print(f"Section: {section}")
            print(f"Total seats: {seatsTotal}")
            print(f"Seats available: {seatsAvail}\n")

# file content should look like
# [subj] [code] [section (optional)]
# pythonic comments are allowed
# stop execution by adding a line with a single word
def parseFromFile(driver):
    with open("courses.txt", "r") as f:
        courses = [line.strip().split(" ") for line in f.readlines() if line[0] != "#"]
        while True:
            for course in courses:
                if len(course) == 1: # stop execution by adding a line with one word to the file
                    return
                if len(course) > 3: # skip a line with more than 3 chunks
                    continue

                html = getRawHTML(driver, course[0], course[1])
                if len(course) == 3: # course section specified
                    getSeats(html, course[2])
                else: # course section not specified
                    getSeats(html)
            
            if len(sys.argv) == 1 or sys.argv[1] != "monitor": break
            else: sleep(600)
                
    driver.close()
    input("enter to exit")
                
ops = Options()
ops.add_argument("--headless")
ops.add_argument("--log-level=3") # hide extra logging that comes with headless mode
ops.add_experimental_option('excludeSwitches', ['enable-logging']) # hide "devtools listening on..."
# driver = webdriver.Chrome('./chromedriver', options=ops)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=ops)

# getSeats(getRawHTML(driver, "CSE", 3183))
parseFromFile(driver)


