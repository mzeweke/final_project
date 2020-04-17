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


def get_MLB_data(year):
    ''' returns a tuple of team name, home record, away record for MLB teams in the
    passed year '''
    teams = mlbteams(year)
    team_records = []
    for team in teams:
        name = team.name
    # get home stats
        hr = team.home_record
        hdash = hr.find("-")
        home_wins = hr[:hdash]
        home_losses = hr[hdash+1:]
        home_rec = [int(home_wins), int(home_losses)]
    # get away stats
        ar = team.away_record
        adash = ar.find("-")
        away_wins = ar[:adash]
        away_losses = ar[adash+1:]
        away_rec = [int(away_wins), int(away_losses)]
    # organize in a dict
        dict = {}
        dict["name"] = team.name
        dict["home"] = home_rec
        dict["away"] = away_rec
        team_records.append(dict)
    return team_records


def get_NFL_data(year):
    ''' returns a tuple of team name, home record, away record for MLB teams in the
    passed year '''
    teams = nflteams(year)
    team_records = []
    for team in teams:
    # look at all registered teams in the NFL
        schedule = team.schedule
        home_record = [0,0,0]
        away_record = [0,0,0]
    # look at results for all games in that team's schedule
        for game in schedule:
            if game.type == 'Reg':
                update_home_away(game.location, game.result, home_record, away_record)
    # organize in a dict    
        dict = {}
        dict["name"] = team.name
        dict["home"] = home_record
        dict["away"] = away_record
        team_records.append(dict)
    return team_records


def get_NBA_data(year, cur, conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS NBA (name TEXT PRIMARY KEY, home_wins INTEGER, home_losses INTEGER, away_wins INTEGER, away_losses INTEGER)''')
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()

    teams = NBAteams(year)
    team_records = []
    for team in teams:
    # look at all registered teams in NBA
        schedule = team.schedule
        home_record = [0,0,0]
        away_record = [0,0,0]
    # look at at results for all games in that team's schedule
        for game in schedule:
            if game.playoffs == False:
                update_home_away(game.location, game.result, home_record, away_record)
    # organize in a dict
        cur.execute("INSERT OR IGNORE INTO NBA (name, home_wins, home_losses, away_wins, away_losses) VALUES (?,?,?,?,?)",(team.name, home_record[0], home_record[1], away_record[0], away_record[1]))

    conn.commit()
    return team_records


def get_NHL_data(year):
    teams = NHLteams(year)
    team_records = []
    for team in teams:
    # look at all registered teams in NBA
        schedule = team.schedule
        home_record = [0,0,0]
        away_record = [0,0,0]
    # look at at results for all games in that team's schedule
        for game in schedule:
            if game.game <= 82:
                update_home_away(game.location, game.result, home_record, away_record)
    # organize in a dict
        dict = {}
        dict["name"] = team.name
        dict["home"] = home_record
        dict["away"] = away_record
        team_records.append(dict)
    return team_records


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


if __name__ == '__main__':
    setUpDatabase('sports_records')
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'sports_records.db')
    cur = conn.cursor()
    print(get_NHL_data(2019))
