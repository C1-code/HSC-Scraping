import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import time

letters = string.ascii_lowercase

def getLinks(year: int):
    url = "https://www.boardofstudies.nsw.edu.au/ebos/static/DSACH_" + str(year) + "_12.html"
    response = requests.get(url)
    if response.status_code==200:
            html_doc = response.text
    else:
        raise TimeoutError("Web Page doesn't exist")
    soup = BeautifulSoup(html_doc, 'html.parser')
    elements = soup.find_all('tr')

    linksResult = []

    for element in elements:
        links = element.find_all('a')
        for link in links:
            if year!=2011:
                linksResult.append("https://www.boardofstudies.nsw.edu.au/ebos/static/" + link['href'])
            elif year==2011:
                linksResult.append("https://www.boardofstudies.nsw.edu.au" + link['href'])
    return linksResult

def getSubjectDictionary(year: int):
    url = "https://www.boardofstudies.nsw.edu.au/ebos/static/BDHSC_" + str(year) + "_12.html"
    response = requests.get(url)
    if response.status_code==200:
        html_doc = response.text
    else:
        raise TimeoutError("Web Page doesn't exist")
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    if year>=2012:
        elements = soup.find_all('li')
    elif year<2012:
        elements = soup.find_all('td')
    dict = {}

    for element in elements:
        subjects = element.text
        dict[subjects[-6:-1]] = subjects[:-7]
    
    dict["16150"] = "Accounting 2 unit "
    dict["25010"] = "Comparative Literature - Distinction Course"
    dict["25020"] = "Cosmology - Distinction Course"
    dict["25030"] = "Philosophy - Distinction Course"
    return dict

def getDataFrame(year: int) -> pd.DataFrame:
    t0 = time.time()
    urls = []
    if 2018<=year and year<=2022:
        for letter in string.ascii_lowercase:
            urls.append("https://educationstandards.nsw.edu.au/wps/portal/nesa/about/events/merit-lists/distinguished-achievers/" + str(year) +"/" + letter)
    elif year==2017:
        for letter in string.ascii_lowercase:
            urls.append("https://educationstandards.nsw.edu.au/wps/portal/nesa/about/events/merit-lists/distinguished-achievers/2017/hsc-2017-" + letter)
    elif year==2016:
        for letter in string.ascii_lowercase:
            urls.append("https://www.boardofstudies.nsw.edu.au/ebos/static/DSACH_2016_12_" + letter.upper() + ".html")
    elif year<=2015 and year>=2001:
        urls = getLinks(year)
    dfs = []
    for url in urls:
        response = requests.get(url)
        if response.status_code==200:
            html_doc = response.text
        else:
            print(url)
            raise TimeoutError("Web Page doesn't exist")

        soup = BeautifulSoup(html_doc, 'html.parser')
        elements = soup.find_all('tr')

        dict = getSubjectDictionary(year)
        rows = []

        for element in elements:
            parsed = element.find_all('td')
            
            if len(parsed)<=2:
                continue
            if len(parsed)==4:
                parsed.pop(0)
            name = parsed[0].text
            school = parsed[1].text

            if year>=2015:
                subjects = parsed[2].get_text().split(' - ')
                subjects.pop(0)
                i = 0
                while i<len(subjects)-1:
                    subjects[i] = subjects[i][:len(subjects[i])-6]
                    i+=1
                i = 0
                while i<len(subjects):
                    rows.append([name,school,subjects[i]])
                    i+=1
            
            elif year<2015 and year>=2001:
                subjects = parsed[2].get_text().split(", ")
                if len(subjects[0])!=5:
                    subjects[0] = subjects[0][1:]
                i = 0
                while i<len(subjects):
                    try:
                        rows.append([name,school,dict[subjects[i]]])
                    except KeyError:
                        print(subjects[i])
                        print(name + " " + school + " " + subjects[i])
                    i+=1
        print(url + " appended")
        df = pd.DataFrame(rows, columns=["Name", "School", "Subject"])
        dfs.append(df)
    maindf = pd.concat(dfs, axis=0)
    maindf.to_csv(str(year) + ".csv")
    print("getDataFrame execution time: " + str(time.time()-t0))
    return maindf

def generateCSVs():
    year = 2001
    while year<=2022:
        getDataFrame(year)
        year+=1

