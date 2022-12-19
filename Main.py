import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import time
import matplotlib.pyplot as plt

letters = string.ascii_lowercase
MathsExt1 = {2015: "Mathematics Extension 1", 2001: "Mathematics Extension 1 2 unit "}
MathsExt2 = {2015: "Mathematics Extension 2", 2001: "Mathematics Extension 2 2 unit "}

def fileExists(path: str)->bool:
    try:
        f = open(path, "r")
        return True
    except FileNotFoundError:
        return False

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
    path = str(year) + ".csv"
    if(fileExists(path)):
        df = pd.read_csv(str(year) + ".csv", index_col=[0]).reset_index().drop(["index"], axis=1)
        return df
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
        response = requests.get(url) #Loading in the webstie
        if response.status_code==200:
            html_doc = response.text
        else:
            raise TimeoutError("Web Page doesn't exist")

        #Parsing all the tr elements from the site
        soup = BeautifulSoup(html_doc, 'html.parser')
        elements = soup.find_all('tr')

        dict = getSubjectDictionary(year)
        rows = []

        #For each tr element, get the name, school, and subjects
        for element in elements:
            parsed = element.find_all('td')
            
            if len(parsed)<=2:
                continue
            if len(parsed)==4:
                parsed.pop(0)
            name = parsed[0].text
            school = parsed[1].text

            #Account for the different formatting before and after 2015
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
        df = pd.DataFrame(rows, columns=[str(year) + " Name", str(year) + " School", str(year) + " Subject"])
        dfs.append(df)
    print("Not read from machine")
    maindf = pd.concat(dfs, axis=0).reset_index().drop(["index"], axis=1)
    maindf.to_csv(str(year) + ".csv")
    print("getDataFrame execution time: " + str(time.time()-t0))
    return maindf

def generateCSVs():
    for year in getYears():
        getDataFrame(year)
    
def getList(year: int, item="School"):
    df = getDataFrame(year)
    main = []
    for focus in df[str(year) + " " + item]:
        if focus not in main:
            main.append(focus)
    return main

def getYears():
    years = []
    year = 2001
    while year<=2022:
        years.append(year)
        year+=1
    return years

def getSchoolYearSubjectCount(year: int, school: str, subject: str):
    df = getDataFrame(year)
    subjectList = getList(year, item="Subject")

    if subject in subjectList:
        pass
    else:
        for element in subjectList:
            if element.startswith(subject):
                subject = element
    print(str(year) + ": " + subject)
    count =0
    i = 0
    while i<len(df[str(year) + " School"]):
        if df[str(year) + " School"][i].startswith(school):
            properSchool = df[str(year) + " School"][i]
            if df[str(year) + " Subject"][i]==subject:
                count+=1
        i+=1
    return (count, properSchool, subject)

def getSchoolRecordSubject(school: str, subject: str):
    scores = []
    for year in getYears():
        score, properSchool, properSubject = getSchoolYearSubjectCount(year, school, subject)
        scores.append(score)
    return scores, properSchool, properSubject

def graphMultiple():
    school = ""
    schools = []
    subjects = []

    years = getYears()

    while school.lower()!="graph":
        school = input("School: ")
        if school=="graph":
            continue
        schools.append(school)

        subject = input("Subject: ")
        subjects.append(subject)

        print("\n")
    
    fig, ax = plt.subplots(len(schools), 1)
    for i in range(len(schools)):
        scores, properSchool, subject = getSchoolRecordSubject(schools[i], subjects[i])
        
        ax[i].plot(years, scores)
        ax[i].set_xlabel("Years")
        ax[i].set_ylabel("Band 6 count")
        ax[i].set_title(properSchool + " band 6 count for " + subject)
    
    plt.show()

graphMultiple()
