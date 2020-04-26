from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
import json
import sqlite3

# First we are setting up the databases that we will need to be using later
# This is basically copied and paisted from Homework #8

# This section pulls data from the espn websight on attendance data
def get_nfl(year, curr, conn):
    #data base setup
    cur.execute('''CREATE TABLE IF NOT EXISTS NFL_{} (team TEXT PRIMARY KEY, games INTEGER, total INTEGER, average INTEGER, year INTEGER)'''.format(year))
    db_conn = sqlite3.connect("attendace.db")
    db_cur = db_conn.cursor()
    
    #Getting the Data
    url = 'http://www.espn.com/nfl/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = []
    for i in soup.find_all('tr'):
        l.append(i.text.strip().split('\n'))
    
    for team in l[2:]:
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
        cur.execute("INSERT OR IGNORE INTO NFL_{} (team, games, total, average, year) VALUES (?,?,?,?,?)".format(year),(name, games, total, average, year))
    conn.commit()
    
    return l

def get_mlb(year, curr, conn):
    #data base setup
    cur.execute('''CREATE TABLE IF NOT EXISTS MLB_{} (team TEXT PRIMARY KEY, games INTEGER, total INTEGER, average INTEGER, year INTEGER)'''.format(year))
    db_conn = sqlite3.connect("attendace.db")
    db_cur = db_conn.cursor()
    
    #getting the data
    url = 'http://www.espn.com/mlb/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = []
    #appending headers
    l.append(['RK','TEAM','GMS','TOTAL','AVG','PCT'])
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
        cur.execute("INSERT OR IGNORE INTO MLB_{} (team, games, total, average, year) VALUES (?,?,?,?,?)".format(year),(name, games, total, average, year))
    conn.commit()

    return l

def get_nba(year, curr, conn):
    #data base setup
    cur.execute('''CREATE TABLE IF NOT EXISTS NBA_{} (team TEXT PRIMARY KEY, games INTEGER, total INTEGER, average INTEGER, year INTEGER)'''.format(year))
    db_conn = sqlite3.connect("attendace.db")
    db_cur = db_conn.cursor()
    
    #getting the data
    url = 'http://www.espn.com/nba/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = []
    line_counter = 0
    head = ['RK','TEAM','GMS','TOTAL','AVG','PCT']
    l.append(head)
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
        cur.execute("INSERT OR IGNORE INTO NBA_{} (team, games, total, average, year) VALUES (?,?,?,?,?)".format(year),(name, games, total, average, year))
    conn.commit()

    return l

def get_nhl(year, curr, conn):
    #data base setup
    cur.execute('''CREATE TABLE IF NOT EXISTS NHL_{} (team TEXT PRIMARY KEY, games INTEGER, total INTEGER, average INTEGER, year INTEGER)'''.format(year))
    db_conn = sqlite3.connect("attendace.db")
    db_cur = db_conn.cursor()
    
    #getting the data
    url = 'http://www.espn.com/nhl/attendance/_/year/' + str(year)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    l = []
    l.append(['RK','TEAM','GMS','TOTAL','AVG','PCT'])
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
        cur.execute("INSERT OR IGNORE INTO NHL_{} (team, games, total, average, year) VALUES (?,?,?,?,?)".format(year),(name, games, total, average, year))
    conn.commit()
    return l


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

if __name__ == '__main__':
    setUpDatabase("attendace.db")
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'attendace.db')
    cur = conn.cursor()
   
    for i in range(1,20):
        year = 2000+i
        get_nfl(year, cur, conn)
        get_mlb(year, cur, conn)
        get_nba(year, cur, conn)
        get_nhl(year, cur, conn)
    



