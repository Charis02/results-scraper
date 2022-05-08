from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json # for saving the data
from colorama import init, Fore, Back, Style # for pretty printing
import re # use to remove double spaces

# Initializes Colorama
init(autoreset=True)

print(Style.BRIGHT + Fore.WHITE + "Starting...")
print(Style.BRIGHT + Fore.CYAN + "Setting up the browser...")

URL = "https://eservices.moec.gov.cy/ypexams/pagkypries/ypopsifioi/2020/vathmologies"

options = Options()
#options.headless = True
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)
driver.get(URL)

print(Style.BRIGHT + Fore.CYAN + "Browser is ready!")
print(Style.BRIGHT + Fore.CYAN + "Scraping data...")

def extract_data(soup):
    """
    Extracts data from the page.
    Returns a pair of the new candidates dictionary and
    the id of the last candidate on the page
    """
    result = []
    last = 0
    candidates = soup.findAll('tr', class_='dxgvDataRow_DevEx')
    for candidate in candidates:
        candidate_id = candidate.find('td', class_='dxgv').text
        last = int(candidate_id)
        candidate_grades = candidate.findAll('td', class_='dxgv')
        
        new_cand = {}
        new_cand["code"] = candidate_id

        cnt = 0
        first= True
        for grade in candidate_grades:
            if first:
                first = False
                continue
            if grade.text == " ":
                break

            cnt += 1
            new_cand["Lesson"+str(cnt)] = re.sub(' +',' ',grade.text)

        result.append(new_cand)

    return result,last

final_dict = {}
final_dict["Candidates"] = []
while True:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    new_candidates,id = extract_data(soup)
    final_dict["Candidates"].extend(new_candidates)
    try:
        looking_for = "ctl00_ctl00_MainPane_Content_MainContent_ASPxGrid_grid_DXDataRow" + str(id)
        driver.execute_script("ASPx.GVPagerOnClick('ctl00_ctl00_MainPane_Content_MainContent_ASPxGrid_grid','PBN');")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, looking_for)))
    except:
        print(Style.BRIGHT + Fore.CYAN + "I have scraped all the data!")
        print(Style.BRIGHT + Fore.YELLOW + "Last candidate id: " + str(id))
        break

driver.close()

print(Style.BRIGHT + Fore.CYAN + "Dumping data...")

with open("raw_data.json", "w") as f:
    json.dump(final_dict, f,ensure_ascii=False, indent=2)

print(Style.BRIGHT + Fore.CYAN + "Data dumped!")
print(Style.BRIGHT + Fore.WHITE + "Done!")