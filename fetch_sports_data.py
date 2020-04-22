from sportsreference.mlb.teams import Teams as MLBteams
from sportsreference.nfl.teams import Teams as NFLteams
from sportsreference.nba.teams import Teams as NBAteams
from sportsreference.nhl.teams import Teams as NHLteams
import requests
import sqlite3
import time
import csv
import re
import os


def update_home_away(location, result, home_rec, away_rec):
    """Takes a game location and result, along with the team’s home and away records as input.
    Updates the home and away records with the result of the passed game played at the passed
    location.  Does not return."""

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
    """Takes a team name as input.  Separates the city name from the mascot name (mostly so that
    my tables can be joined with Ben's). Returns a list of the city name and the mascot, in that 
    Order."""

    crap = str(re.match(r'((San Jose)|(New Jersey)|(Golden State)|(Green Bay)|(San Antonio)|(Oklahoma City)|(New Orleans)|(Tampa Bay)|(New York)|(Kansas City)|(Los Angeles)|(St. Louis)|(New England)|(San Francisco)|(San Diego)|\w+)', team))
    name_start = crap.find("'")
    crap = crap[name_start+1:]
    name_end = crap.find("'")
    city = crap[:name_end]

    length_name = len(city) + 1
    mascot = team[length_name:]

    list = [city, mascot]
    return list


def fetch_MLB_data(year):
    '''Takes a year as input.  Fetches data from sportsreference.mlb.teams for the passed year. 
    Returns a list of id, year, league, home wins, home losses, home ties, away wins, away losses,
    away ties, city, and mascot for each baseball team that is ready to be stored in database.'''

    teams = MLBteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
        str_year = str(year)
        short_year = str_year[2:]
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
        tup = [team.name +" '" + str(short_year), year, "MLB", home_wins, home_losses, 0, away_wins, away_losses, 0, city, mascot]
        team_records.append(tup)
        print("   Loading data for " + team.name + " " + str(year) + "...")
    return team_records


def fetch_NFL_data(year):
    '''Takes a year as input.  Fetches data from sportsreference.nfl.teams for the passed year. 
    Returns a list of id, year, league, home wins, home losses, home ties, away wins, away losses, 
    away ties, city, and mascot for each football team that is ready to be stored in database.'''

    teams = NFLteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
        str_year = str(year)
        short_year = str_year[2:]

        schedule = team.schedule    # look at all registered teams in the NFL
        home_record = [0,0,0]
        away_record = [0,0,0]
    
        for game in schedule:       # look at results for all games in that team's schedule
            if game.type == 'Reg':
                update_home_away(game.location, game.result, home_record, away_record)
       
        tup = [team.name +" '" + str(short_year), year, "NFL", home_record[0], home_record[1], home_record[2], away_record[0], away_record[1], away_record[2], city, mascot]
        team_records.append(tup)    # store in list
        print("   Loading data for " + team.name + " " + str(year) + "...")
    return team_records


def fetch_NBA_data(year):
    '''Takes a year as input.  Fetches data from sportsreference.nba.teams for the passed year. 
    Returns a list of id, year, league, home wins, home losses, home ties, away wins, away losses, 
    away ties, city, and mascot for each basketball team that is ready to be stored in database.'''

    teams = NBAteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
        str_year = str(year)
        short_year = str_year[2:]

        schedule = team.schedule      # look at all registered teams in NBA
        home_record = [0,0,0]
        away_record = [0,0,0]
    
        for game in schedule:         # look at all registered teams in NBA
            if game.playoffs == False:
                update_home_away(game.location, game.result, home_record, away_record)

        tup = [team.name +" '" + str(year), year, "NBA", home_record[0], home_record[1], home_record[2], away_record[0], away_record[1], away_record[2], city, mascot]
        team_records.append(tup)      # store in list
        print("   Loading data for " + team.name + " " + str(year) + "...")
    return team_records


def fetch_NHL_data(year):
    '''Takes a year as input.  Fetches data from sportsreference.nhl.teams for the passed year. 
    Returns a list of id, year, league, home wins, home losses, home ties, away wins, away losses, 
    away ties, city, and mascot for each hockey team that is ready to be stored in database.'''

    teams = NHLteams(year)
    team_records = []
    for team in teams:
        list = city_mascot(team.name)
        city = list[0]
        mascot = list[1]
        str_year = str(year)
        short_year = str_year[2:]

        schedule = team.schedule    # look at all registered teams in NBA
        home_record = [0,0,0]
        away_record = [0,0,0]
    
        for game in schedule:       # look at at results for all games in that team's schedule
            if game.game <= 82:
                update_home_away(game.location, game.result, home_record, away_record)

        tup = [team.name +" '" + str(year), year, "NHL", home_record[0], home_record[1], home_record[2], away_record[0], away_record[1], away_record[2], city, mascot]
        team_records.append(tup)      # store in list
        print("   Loading data for " + team.name + " " + str(year) + "...")
    return team_records


def get_data_year(year):
    '''Takes a year as input. Runs all of the fetch_data functions for that year and saves the
    data into one huge masterlist.  Returns this masterlist.'''

    master_list = []
    print("Loading MLB data... this may take a while.")
    master_list = master_list + fetch_MLB_data(year)
    #print("\nPausing for 30 seconds so we don't make too many api requests...\n")
    #time.sleep(30)

    print("Loading NFL data... this may take a while.")
    master_list = master_list + fetch_NFL_data(year)
    #print("\nPausing for 30 seconds so we don't make too many api requests...\n")
    #time.sleep(30)

    print("Loading NBA data... this may take a while.")
    master_list = master_list + fetch_NBA_data(year)
    #print("\nPausing for 30 seconds so we don't make too many api requests...\n")
    #time.sleep(30)

    print("Loading NHL data... this may take a while.")
    master_list = master_list + fetch_NHL_data(year)
    #print("\nPausing for 30 seconds so we don't make too many api requests...\n")
    #time.sleep(30)
    return master_list


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


def add_records_to_db(teams_masterlist, start):
    ''' Takes a list and a starting index as input.  Fetches the next 20 terms from the passed
    list, beginning at 'start' and loads them into the database. If there are less than 20
    terms left to load, loads the remaining terms into the database.  If there are no more
    terms to load, alerts the user.  Returns a new index that you should use next time. '''
    
    cur.execute('''CREATE TABLE IF NOT EXISTS sports_records (id TEXT PRIMARY KEY, year INTEGER, league TEXT, home_wins INTEGER, home_losses INTEGER, home_ties INTEGER, away_wins INTEGER, away_losses INTEGER, away_ties INTEGER, city TEXT, mascot TEXT)''')
    db_conn = sqlite3.connect("sports_records.db")
    db_cur = db_conn.cursor()
    for team in teams_masterlist:
        if start+20 <= len(teams_masterlist):
            for i in range(start, start+20):
                cur.execute("INSERT OR IGNORE INTO sports_records (id, year, league, home_wins, home_losses, home_ties, away_wins, away_losses, away_ties, city, mascot) VALUES (?,?,?,?,?,?,?,?,?,?,?)",team)
        elif start == len(teams_masterlist):
            print("No more data to load!")
            return -1
        else:
            for i in range(start, len(teams_masterlist)):
                cur.execute("INSERT OR IGNORE INTO sports_records (id, year, league, home_wins, home_losses, home_ties, away_wins, away_losses, away_ties, city, mascot) VALUES (?,?,?,?,?,?,?,?,?,?,?)",team)
    conn.commit()
    return i

    
if __name__ == '__main__':
    setUpDatabase('sports_records')
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'sports_records.db')
    cur = conn.cursor()
    
    #===============================================================================================#
    
    # First I loaded the lists of team information into CSV files, so I'm not making requests for the
    # same information over and over again.  I only did this ONCE.
    '''
    sports_17 = get_data_year(2017)
    load_to_file("sports_17.csv", sports_17)

    sports_18 = get_data_year(2018)
    load_to_file("sports_18.csv", sports_18)

    sports_19 = get_data_year(2019)
    load_to_file("sports_19.csv", sports_19)
    '''

    #===============================================================================================#
    
    # Now I will load all sports records data for the past 3 years 20 at a time into tables.
    
    sports_17 = read_file_into_list("sports_17.csv")
    sports_18 = read_file_into_list("sports_18.csv")
    sports_19 = read_file_into_list("sports_19.csv")

    sports_list = sports_17 + sports_18 + sports_19

    index = add_records_to_db(sports_list, 0)
    if index != -1:
        print("Run again to keep loading data! Use start = " + str(index+1) + " to load more data!")
    
    
    # Now everything is loaded in the database, so this file is complete (:

    #===============================================================================================#
