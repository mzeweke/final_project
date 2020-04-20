from bs4 import BeautifulSoup
from sportsreference.mlb.teams import Teams as mlbteams
from sportsreference.nfl.teams import Teams as nflteams
from sportsreference.nba.teams import Teams as NBAteams
from sportsreference.nhl.teams import Teams as NHLteams
import requests
import sqlite3
import re
import os


def update_home_away(location, result, home_rec, away_rec):
    if location == 'Home':
        if result == 'Win':
            home_rec[0] += 1
        elif result == 'Loss':
            home_rec[1] += 1
        else:
            home_rec[2] += 1
    elif location == 'Away':
        if result == 'Win':
            away_rec[0] += 1
        elif result == 'Loss':
            away_rec[1] += 1
        else:
            away_rec[2] += 1

def city_mascot(team):
    crap = str(re.match(r'((San Jose)|(New Jersey)|(Golden State)|(Green Bay)|(San Antonio)|(Oklahoma City)|(New Orleans)|(Tampa Bay)|(New York)|(Kansas City)|(Los Angeles)|(St. Louis)|(New England)|(San Francisco)|(San Diego)|\w+)', team))
    name_start = crap.find("'")
    crap = crap[name_start+1:]
    name_end = crap.find("'")
    city = crap[:name_end]

    length_name = len(city) + 1
    mascot = team[length_name:]

    list = [city, mascot]
    return list

def get_MLB_data(year, cur, conn):
    ''' returns a tuple of team name, home record, away record for MLB teams in the
    passed year '''
    cur.execute('''CREATE TABLE IF NOT EXISTS mlb_{} (city TEXT, mascot TEXT PRIMARY KEY, home_wins INTEGER, home_losses INTEGER, away_wins INTEGER, away_losses INTEGER)'''.format(year))
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()

    teams = mlbteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
    # get home stats
        hr = team.home_record
        hdash = hr.find("-")
        home_wins = hr[:hdash]
        home_losses = hr[hdash+1:]
    # get away stats
        ar = team.away_record
        adash = ar.find("-")
        away_wins = ar[:adash]
        away_losses = ar[adash+1:]
    # organize in a dict
        cur.execute("INSERT OR IGNORE INTO mlb_{} (city, mascot, home_wins, home_losses, away_wins, away_losses) VALUES (?,?,?,?,?,?)".format(year),(city, mascot, home_wins, home_losses, away_wins, away_losses))

    conn.commit()

def get_NFL_data(year, cur, conn):
    ''' returns a tuple of team name, home record, away record for MLB teams in the
    passed year '''
    cur.execute('''CREATE TABLE IF NOT EXISTS nfl_{} (city TEXT, mascot TEXT PRIMARY KEY, home_wins INTEGER, home_losses INTEGER, home_ties INTEGER, away_wins INTEGER, away_losses INTEGER, away_ties INTEGER)'''.format(year))
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()

    teams = nflteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]

    # look at all registered teams in the NFL
        schedule = team.schedule
        home_record = [0,0,0]
        away_record = [0,0,0]
    # look at results for all games in that team's schedule
        for game in schedule:
            if game.type == 'Reg':
                update_home_away(game.location, game.result, home_record, away_record)
    # organize in a dict    
        cur.execute("INSERT OR IGNORE INTO nfl_{} (city, mascot, home_wins, home_losses, home_ties, away_wins, away_losses, away_ties) VALUES (?,?,?,?,?,?,?,?)".format(year),(city, mascot, home_record[0], home_record[1], home_record[2], away_record[0], away_record[1], away_record[2]))
    
    conn.commit()

def get_NBA_data(year, cur, conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS nba_{} (city TEXT, mascot TEXT PRIMARY KEY, home_wins INTEGER, home_losses INTEGER, away_wins INTEGER, away_losses INTEGER)'''.format(year))
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()

    teams = NBAteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
    # look at all registered teams in NBA
        schedule = team.schedule
        home_record = [0,0,0]
        away_record = [0,0,0]
    # look at at results for all games in that team's schedule
        for game in schedule:
            if game.playoffs == False:
                update_home_away(game.location, game.result, home_record, away_record)
    # organize in a dict
        cur.execute("INSERT OR IGNORE INTO nba_{} (city, mascot, home_wins, home_losses, away_wins, away_losses) VALUES (?,?,?,?,?,?)".format(year),(city, mascot, home_record[0], home_record[1], away_record[0], away_record[1]))

    conn.commit()

def get_NHL_data(year, cur, conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS nhl_{} (city TEXT, mascot TEXT PRIMARY KEY, home_wins INTEGER, home_losses INTEGER, home_ties INTEGER, away_wins INTEGER, away_losses INTEGER, away_ties INTEGER)'''.format(year))
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()

    teams = NHLteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
    # look at all registered teams in NBA
        schedule = team.schedule
        home_record = [0,0,0]
        away_record = [0,0,0]
    # look at at results for all games in that team's schedule
        for game in schedule:
            if game.game <= 82:
                update_home_away(game.location, game.result, home_record, away_record)
    # organize in a dict
        cur.execute("INSERT OR IGNORE INTO nhl_{} (city, mascot, home_wins, home_losses, home_ties, away_wins, away_losses, away_ties) VALUES (?,?,?,?,?,?,?,?)".format(year),(city, mascot, home_record[0], home_record[1], home_record[2], away_record[0], away_record[1], away_record[2]))

    conn.commit()


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_stats_for_year(year):
    get_MLB_data(year, cur, conn)
    get_NBA_data(year, cur, conn)
    get_NFL_data(year, cur, conn)
    get_NHL_data(year, cur, conn)    

if __name__ == '__main__':
    setUpDatabase('sports_records')
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'sports_records.db')
    cur = conn.cursor()
    
    # Functions are programmed to make ONE API request at a time!  So in order to collect all of the data,
    # we must run functions multiple times (with different years).
    # run the for loop to make 20 api requests
    get_NHL_data(2012, cur, conn)
