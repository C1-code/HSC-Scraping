import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import time
import plotly.express as px
import plotly
import os

#All the lowercase letters as an array
letters = string.ascii_lowercase
current_dir = os.path.dirname(__file__)
pathToCSV = current_dir + "\\data\\"

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
    #The urls array will contain every link to go through and read the data from, the format of which changes from 2001-2015, 2016, 2017, 2018-2022
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
        #Convert the rows object into a dataframe with columns according to the year
        df = pd.DataFrame(rows, columns=[str(year) + " Name", str(year) + " School", str(year) + " Subject"])
        #Append this dataframe to the big dfs array containing all these arrays
        dfs.append(df)
    #Combine all the dataframes from that year into one big data frame, write to csv, then return it
    maindf = pd.concat(dfs, axis=0).reset_index().drop(["index"], axis=1)
    maindf.to_csv(pathToCSV + str(year) + ".csv")
    print("getDataFrame execution time: " + str(time.time()-t0))
    return maindf

def generateCSVs()->None:
    '''If the csv for a specific year doesn't exist, create it. Else retrieve it from local storage'''
    for year in getYears():
        getDataFrame(year)
    
def getList(year: int, item="School")->list:
    '''Get either the school or subject list for a specified year'''
    if item!="School" and item!="Subject":
        raise ValueError("The item is not a suitable argument")
    df = getDataFrame(year)
    #main is the list of either the schools or subjects of a specific year
    main = []
    for focus in df[str(year) + " " + item]:
        if focus not in main:
            if year>=2015 and year<=2022:
                main.append(focus.strip().strip("\n").strip("\r"))
            if year>=2001 and year<=2014:
                main.append(focus)
    #Alphabetically sort it
    main.sort()
    return main

def getYears():
    '''Get all the years from 2001 to 2022 as a list for iteration'''
    years = []
    year = 2001
    while year<=2022:
        years.append(year)
        year+=1
    return years

def successive(main: list):
    '''Returns an array with the different components of the list concated together'''
    #E.g. ["Math", "Ext", "1"] -> ["Math", "Math Ext", "Math Ext 1"]
    successive = []
    i = 0
    while i<len(main):
        j = 0
        toAppend = ""
        while j<=len(successive):
            toAppend+=main[j] + " " 
            j+=1
        toAppend = toAppend.strip()
        successive.append(toAppend)
        i+=1
    return successive

def filter(year: int, rawInput: str, item="School")->str:
    '''Given a user input and a year, find the subject the user was most likely trying to get'''
    # We seperate the rawInput string into parts e.g.
    # 'Math Ext 1' -> ['Math','Ext','1']
    # Then check, for each subject, if 'Math', 'Ext', or '1' is in the subject
    # Increase the "count" for that subject for each time any element in the rawInputs array appears
    # The count is a measure of how likely it is that the subject is the subject the user is after 
    if type(year)!=int or type(rawInput)!=str or type(item)!=str:
        raise TypeError("One input into filter is not of the correct type")
    
    if item!="School" and item!="Subject":
        raise ValueError("item parameter needs to be either 'School' or 'Subject'")

    mainList = getList(year, item=item)
    potentialMatches = []

    rawInputs = rawInput.split(" ")
    power = successive(rawInputs)
    
    #Assigning a 'count' score to each element in mainList
    for element in mainList:
        if rawInput.lower()==element.lower():
            return element
        count = 0 
        for splited in rawInputs:
            if splited.lower() in element.lower():
                count+=element.lower().count(splited.lower())
            
            for success in power:
                if element.lower().startswith(success.lower()):
                    count+=1
        if count>1:
            potentialMatches.append([element, count])

    if len(potentialMatches)==0:
        print("No potential matches for the year")
        return ""
    
    #Finding the element with the highest count. If there is no single element, return an empty string
    maxCount = 0
    finals = []
    for element in potentialMatches:
        if element[1]>maxCount:
            finals.clear()
            finals.append(element)
            maxCount = element[1]
        elif element[1]==maxCount:
            finals.append(element)
    
    if len(finals)!=1:
        print("School didn't exist in " + str(year) + ".")
        return ""
    
    return finals[0][0]

def getSchoolYearSubjectCount(year: int, school: str, subject: str):
    '''Get the amount of band 6's for school in subject for the year'''
    df = getDataFrame(year)

    school = filter(year, school, item="School")
    subject = filter(year, subject, item="Subject")

    if school=="" or subject=="":
        print("School or subject not identified")
        return 0

    # print("*****************")
    # print(str(year))
    # print(school)
    # print(subject)
    # print("*****************")
    
    count = 0
    i = 0
    while i<len(df[str(year) + " School"]):
        if df[str(year) + " School"][i]==school:
            if df[str(year) + " Subject"][i]==subject:
                count+=1
        i+=1
    return count

def getSchoolRecordSubject(school: str, subject: str):
    years = getYears()
    main = {"Years": [], "Band 6 Count": []}
    for year in years:
        main["Years"].append(year)
        main["Band 6 Count"].append(getSchoolYearSubjectCount(year, school, subject))
    scores = pd.DataFrame(main)
    return scores, school, subject

def graph(school: str, subject: str) -> str:
    '''Returns the html code of the graph if it was a div object (used in index.html)'''
    scores, schoolName, subjectName = getSchoolRecordSubject(school, subject)
    fig = px.scatter(scores, x="Years", y="Band 6 Count", title=schoolName + " band 6 count for " + subjectName)
    graphDiv = plotly.offline.plot(fig, auto_open=False, output_type="div")
    return graphDiv