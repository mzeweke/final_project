from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
import json
import sqlite3

def get_nfl(year):
    '''
    Takes in one imput, year.
    Retraves data from ESPN.com of City, games played in a season, total attendance at games, and average game attendance.
    Retruns a list of [City, Year, League, Total Game Attendance, Average Game Attenance]
    '''

    url = 'http://www.espn.com/nfl/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = [] #lsit will be filled with all of the team data
    r_list = [] #will be filled with data we wish to return
    for i in soup.find_all('tr'):
        l.append(i.text.strip().split('\n'))
    for team in l[2:]:
        if team[1] == 'NY Jets' or team[1] == 'NY Giants':
            name = 'New York'
        else:    
            name = team[1]
        try:   
            games = int(team[2])
        except:
            games = 'N/A'
        try:   
            total = int(team[3].replace(',',''))
        except:
            total = 'N/A'
        try:   
            average = int(team[4].replace(',',''))
        except:
            average = 'N/A'
        r_list.append([name, year, 'NFL', games, total, average])
    return r_list

def get_mlb(year):
    '''
    Takes in one imput, year.
    Retraves data from ESPN.com of City, games played in a season, total attendance at games, and average game attendance.
    Retruns a list of [City, Year, League, Total Game Attendance, Average Game Attenance]
    '''

    url = 'http://www.espn.com/mlb/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = [] #lsit will be filled with all of the team data
    r_list = [] #will be filled with data we wish to return
    for i in soup.find_all('tr'):
        team = []
        text = i.text
        try:
            #rank
            team.append(re.findall(r'\b([1-9](|[0-9]))\D', text)[0][0])
            #name
            team.append(re.findall(r'\d([\D]+)\d{3}', text)[0].strip())
            #games
            team.append(re.findall(r'(\b|\w)(([78][0-9]))', text)[0][1])
            #total
            team.append(re.findall(r'\d{2}((?:\d\,)?\d{3}\,\d{3})', text)[0])
            #average
            team.append(re.findall(r'(\d{2}\,\d{3})\d{1,3}\.', text)[0])
            #pct
            team.append(re.findall(r'\d{2}\,\d{3}(\d{1,3}\.\d)', text)[0])
        except:
            continue
        l.append(team)

    for team in l[1:]:
        name = team[1].strip('LA ')
        try:   
            games = int(team[2])
        except:
            games = 'N/A'
        try:   
            total = int(team[3].replace(',',''))
        except:
            total = 'N/A'
        try:   
            average = int(team[4].replace(',',''))
        except:
            average = 'N/A'
        r_list.append([name, year, 'MLB', games, total, average])
    return r_list

def get_nba(year):
    '''
    Takes in one imput, year.
    Retraves data from ESPN.com of City, games played in a season, total attendance at games, and average game attendance.
    Retruns a list of [City, Year, League, Total Game Attendance, Average Game Attenance]
    '''

    url = 'http://www.espn.com/nba/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = [] #lsit will be filled with all of the team data
    r_list = [] #will be filled with data we wish to return
    line_counter = 0
    team = []
    for i in soup.find_all('td'):
        if line_counter > 15 and line_counter < 424:
            if (line_counter-16)%12 == 0:
                team = []
                team.append(i.text)
            if (line_counter-16)%12 == 1:
                team.append(i.text)
            if (line_counter-16)%12 == 2:
                team.append(i.text)
            if (line_counter-16)%12 == 3:
                team.append(i.text)
            if (line_counter-16)%12 == 4:
                team.append(i.text)
            if (line_counter-16)%12 == 5:
                team.append(i.text)
                l.append(team)
        line_counter+=1
    
    for team in l[1:]:
        name = team[1]
        try:   
            games = int(team[2])
        except:
            games = 'N/A'
        try:   
            total = int(team[3].replace(',',''))
        except:
            total = 'N/A'
        try:   
            average = int(team[4].replace(',',''))
        except:
            average = 'N/A'
        r_list.append([name, year, 'NBA', games, total, average])

    return r_list

def get_nhl(year):
    '''
    Takes in one imput, year.
    Retraves data from ESPN.com of City, games played in a season, total attendance at games, and average game attendance.
    Retruns a list of [City, Year, League, Total Game Attendance, Average Game Attenance]
    '''

    url = 'http://www.espn.com/nhl/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = []
    l = [] #lsit will be filled with all of the team data
    r_list = [] #will be filled with data we wish to return
    for i in soup.find_all('tr'):
        team = []
        text = i.text
        try:
            #rank
            team.append(re.findall(r'\b([1-9][0-9]?)\D', text)[0])
            #name
            team.append(re.findall(r'\d([\D]+)\d{3}', text)[0].strip())
            #games
            team.append(re.findall(r'[3,4][0,1]', text)[0])
            #total
            team.append(re.findall(r'\d{2}((?:\d\,)?\d{3}\,\d{3})', text)[0])
            #average
            team.append(re.findall(r'(\d{2}\,\d{3})', text)[1])
            #pct
            team.append(re.findall(r'\d{2}\,\d{3}\d{2}\,\d{3}(.+)[3-4][0-1]', text)[0])
        except:
            continue
        l.append(team)

    for team in l[1:]:
        if team[1] == 'NY Islanders' or team[1] == 'NY Rangers':
            name = 'New York'
        else:
            name = team[1]
        try:   
            games = int(team[2])
        except:
            games = 'N/A'
        try:   
            total = int(team[3].replace(',',''))
        except:
            total = 'N/A'
        try:   
            average = int(team[4].replace(',',''))
        except:
            average = 'N/A'
        r_list.append([name, year, 'NHL', games, total, average])
    return r_list

#These next two funcitons were written by Mariah Zeweke. They are coppied for consistancy acrosse the entire project.

def load_to_file(filename, list):
    '''Takes a filename and a list as input.  Saves the data passed by list into filename, so
    that it can be accessed later without making more api requests.  Does not return.'''

    dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir, filename), 'w', newline = '') as outfile:
        csv_writer = csv.writer(outfile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        for item in list:
            csv_writer.writerow(item)
    outfile.close()

def read_file_into_list(filename):

    '''Takes a filename as input.  Reads the data from filename into a list.  Returns this list.'''

    dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(dir, filename)) as csvfile:
        csv_reader = csv.reader(csvfile)
        lines = []
        for rows in csv_reader:
            lines.append(rows)
    csvfile.close()
    return lines

def setUpDatabase(db_name):
    '''Takes a database name as input.  Gets the database set up and ready to go.  Returns a
    cursor and a connect object.'''

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def add_records_to_db(teams_masterlist):
    ''' Takes a list and a starting index as input.  Fetches the next 20 terms from the passed
    list, beginning at 'start' and loads them into the database. If there are less than 20
    terms left to load, loads the remaining terms into the database.  If there are no more
    terms to load, alerts the user.  Returns a new index that you should use next time. '''
    
    cur.execute('''CREATE TABLE IF NOT EXISTS sports_attend (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    name TEXT, 
                                                                    year INTEGER, 
                                                                    league TEXT, 
                                                                    games INTEGER, 
                                                                    total INTEGER, 
                                                                    average INTEGER)''')
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()
    for team in teams_masterlist:
        insertion = (None, team[0], team[1], team[2], team[3], team[4], team[5])
        statement = "INSERT OR IGNORE INTO sports_attend "
        statement += "VALUES (?,?,?,?,?,?,?)"
        cur.execute(statement,insertion)
    conn.commit()
    conn.close()
    return 12

if __name__ == '__main__':
    setUpDatabase('sports_records')
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'sports_records.db')
    cur = conn.cursor()

    #( 1 )===============================================================================================#
    #( 1 )First I loaded the lists of team information into CSV files, so I'm not making requests for the
    # same information over and over again.  I only did this ONCE.
    '''
    # 2017 data
    data_2017 = get_nfl(2017) + get_mlb(2017) + get_nba(2017) + get_nhl(2017)
    load_to_file("legues_17.csv", data_2017)

    # 2018 data
    data_2018 = get_nfl(2018) + get_mlb(2018) + get_nba(2018) + get_nhl(2018)
    load_to_file("legues_18.csv", data_2018)

    # 2019 data
    data_2019 = get_nfl(2019) + get_mlb(2019) + get_nba(2019) + get_nhl(2019)
    load_to_file("legues_19.csv", data_2019)
    '''
    
    #( 2 )===============================================================================================#

    #( 2 )Now I will load all sports records data for the past 3 years 20 at a time into tables.

    legues_17 = read_file_into_list("legues_17.csv")
    legues_18 = read_file_into_list("legues_18.csv")
    legues_19 = read_file_into_list("legues_19.csv")
    legues_list = legues_17 + legues_18 + legues_19
    print(len(legues_list))
    x = add_records_to_db(legues_list)

    # Now everything is loaded in the database

    #===============================================================================================#
    



