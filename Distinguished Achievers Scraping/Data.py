import subprocess
try:
    import requests
except ModuleNotFoundError:
    subprocess.run(["pip","install","requests"])

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    subprocess.run(["pip","install","bs4"])

try:
    import pandas as pd
except ModuleNotFoundError:
    subprocess.run(["pip","install","pandas"])

import string
import time
import os
import datetime as dt

#All the lowercase letters as an array
letters = string.ascii_lowercase

#Ensuring the files are in a seperate folder to the code
current_dir = os.path.dirname(__file__)
pathToCSV = current_dir + "\\data\\"

today = dt.datetime.today()
if today.month>=12 and today.day>=20:
    CURRENT_YEAR = today.year
else:
    CURRENT_YEAR = today.year-1

def fileExists(path: str)->bool:
    '''Checks if the file given exists'''
    try:
        current_dir = os.path.dirname(__file__)
        path = current_dir + "\\data\\" + path
        f = open(path, "r")
        
        return True
    except FileNotFoundError:
        return False

def getLinks(year: int):
    '''Returns a list containing the urls that the getDataFrame needs to go through for older distinguished achievers lists'''
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
        #Links is all the link elements stored as an array
        links = element.find_all('a')
        for link in links:
            if year!=2011:
                linksResult.append("https://www.boardofstudies.nsw.edu.au/ebos/static/" + link['href'])
            elif year==2011:
                linksResult.append("https://www.boardofstudies.nsw.edu.au" + link['href'])
    return linksResult

def getSubjectDictionary(year: int)->dict:
    '''Returns a dictionary mapping NESA course codes to the course name'''
    url = "https://www.boardofstudies.nsw.edu.au/ebos/static/BDHSC_" + str(year) + "_12.html"
    response = requests.get(url)
    if response.status_code==200:
        html_doc = response.text
    else:
        raise TimeoutError("Web Page doesn't exist")
    
    soup = BeautifulSoup(html_doc, 'html.parser')
    #The format of storing the subject codes from 2001-2012 was using td tags, from 2012 onwards it was li tags
    if year>=2012:
        elements = soup.find_all('li')
    elif year<2012:
        elements = soup.find_all('td')
    dict = {}

    for element in elements:
        subjects = element.text
        #Mapping the course codes to the names of the subjects
        dict[subjects[-6:-1]] = subjects[:-7]
    
    dict["16150"] = "Accounting 2 unit "
    dict["25010"] = "Comparative Literature - Distinction Course"
    dict["25020"] = "Cosmology - Distinction Course"
    dict["25030"] = "Philosophy - Distinction Course"
    return dict

def getDataFrame(year: int) -> pd.DataFrame:
    '''Returns the dataframe of results for that year'''
    '''E.g.'''
    '''Name         | School   | Band 6'''
    '''Alyssa Jones | Danebank | Mathematics Advanced'''
    '''Alyssa Jones | Danebank | English Advanced'''
    '''Alysse Baker | Danebank | English Advanced'''

    t0 = time.time()
    #If the dataframe already exists, just return it to save processing time
    path = str(year) + ".csv"
    if(fileExists(path)):
        path = pathToCSV + path
        df = pd.read_csv(path, index_col=[0]).reset_index().drop(["index"], axis=1)
        return df
    #The urls array will contain every link to go through and read the data from, the format of which changes from 2001-2015, 2016, 2017, 2018-CURRENT_YEAR
    urls = []
    if 2018<=year and year<=CURRENT_YEAR:
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
    #dfs is an array of dataframes each of which is the dataframe for a specific url
    dfs = []
    for url in urls: #For each url, append to dataframe
        response = requests.get(url) #Loading in the webstie
        if response.status_code==200:
            html_doc = response.text
        else:
            raise TimeoutError("Web Page doesn't exist")

        #Parsing all the tr elements from the site
        soup = BeautifulSoup(html_doc, 'html.parser')
        elements = soup.find_all('tr')

        dict = getSubjectDictionary(year)
        #Rows contains arrays which are of the format [name, school, band 6 subject]
        rows = []

        #For each tr element, get the name, school, and subjects
        for element in elements:
            parsed = element.find_all('td')
            
            if len(parsed)<=2:
                continue
            if len(parsed)==4:
                parsed.pop(0)
            
            #Name and school is easy to parse, always the first and second element of the table
            name = parsed[0].text
            school = parsed[1].text.strip()

            #Account for the different formatting before and after 2015
            if year>=2015:
                subjects = parsed[2].get_text().strip().split(' - ')
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
        #Convert the rows object into a dataframe with columns according to the year
        df = pd.DataFrame(rows, columns=[str(year) + " Name", str(year) + " School", str(year) + " Subject"])
        #Append this dataframe to the big dfs array containing all these arrays
        dfs.append(df)
    #Combine all the dataframes from that year into one big data frame, write to csv, then return it
    maindf = pd.concat(dfs, axis=0).reset_index().drop(["index"], axis=1)
    maindf.to_csv(pathToCSV + str(year) + ".csv")
    print("getDataFrame execution time: " + str(time.time()-t0))
    return maindf

def getYears():
    '''Get all the years from 2001 to CURRENT_YEAR as a list for iteration'''
    years = []
    year = 2001
    while year<=CURRENT_YEAR:
        years.append(year)
        year+=1
    return years

def generateCSVs()->None:
    '''If the csv for a specific year doesn't exist, create it. Else retrieve it from local storage'''
    for year in getYears():
        getDataFrame(year)

generateCSVs()
