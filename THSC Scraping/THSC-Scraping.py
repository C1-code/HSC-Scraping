import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import os

currentYear = 2022
def getYears():
    i = 2019
    years = []
    while i<=currentYear:
        years.append(str(i))
        i+=1
    return years
def getResponse(url):
    response = requests.get(url)
    if response.status_code==200:
        return response.text
    else:
        raise TimeoutError("Web page doesn't exist")


def getLinks():
    links = []
    baseURL = "https://thsconline.github.io/s/yr12/Maths/"
    html_doc = getResponse(baseURL)

    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.find_all('a')
    for element in elements:
        if element["href"].endswith(".html"):
            links.append(baseURL + element["href"])
    return links

def getFiles():
    links = getLinks()
    timeoutlinks = []
    downloadLinks = []

    prelink = "https://thsconline.github.io/s/d/"
    for link in links:
        try:
            html_doc = getResponse(link)

            soup = BeautifulSoup(html_doc, 'html.parser')
            elements = soup.find_all('a')
            for element in elements:
                try:
                    number = element["onclick"][-5:-1]
                    splitName = element.text.split(" ")

                    suffix = ""
                    for s in splitName:
                        suffix+=s + "%20"
                    
                    suffix = suffix.strip("%20")

                    downloadLink = prelink + number + "/" + suffix

                    for year in getYears():
                        if "20" + year in downloadLink:
                            downloadLinks.append(downloadLink)
                            continue

                except KeyError:
                    continue
        except TimeoutError:
            timeoutlinks.append(link)
            print(timeoutlinks)
            continue
    return downloadLinks

def downloadLinks():
    links = getFiles()
    path = os.getcwd()

    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory": path}
    chromeOptions.add_experimental_option("prefs", prefs)
    chromedriver = path + "\\chromedriver.exe"

    driver = webdriver.Chrome(executable_path=chromedriver, options=chromeOptions)
    
    for link in links:
        driver.get(link)

        driver.implicitly_wait(60)
        element = driver.find_element(By.TAG_NAME, "b")
        print(link)
    driver.close()
    
downloadLinks()
        
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService

# # Set the path to the ChromeDriver executable
# chrome_driver_path = "C:\\Users\\elias\\Desktop\\HSC-Scraping\\THSC Scraping\\chromedriver.exe"

# # Create a ChromeService object with the path to the executable
# service = ChromeService(executable_path=chrome_driver_path)

# # Start the service
# service.start()

# # Create a new ChromeDriver session
# driver = webdriver.Chrome(service=service)

# # Navigate to the webpage
# driver.get("https://thsconline.github.io/s/d/5348/Ascham%202001%20w.%20sol")

# #Pause for the downlaod to take place
# time.sleep(30)

# # Close the ChromeDriver session
# driver.close()

# # Stop the service
# service.stop()