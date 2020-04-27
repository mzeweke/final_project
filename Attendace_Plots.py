import matplotlib.pyplot as plt
import sqlite3
import requests
import os
import pprint

def reconds_and_attendace(league, cur, conn):
    ''' 
    Joins the data from the two tables to prepare to be plotted. 
    Takes a league as an imput, and outputs a list of JOINed data
    '''

    path = os.path.dirname(os.path.abspath(__file__))
    db_conn = sqlite3.connect(path+'/'+"sports_records.db")
    db_cur = db_conn.cursor()
    category_id_dict = {}
    db_cur.execute("SELECT * FROM sports_winloss")
    for row in db_cur:
        category_id_dict[row[1]] = row[0]
    if league == 'NFL' or league == 'MLB' or league == 'NHL':
        db_cur.execute('''SELECT DISTINCT sports_attend.name, sports_winloss.mascot, 
                                        sports_attend.year, sports_attend.average, sports_attend.league,
                                        sports_winloss.home_wins, sports_winloss.away_wins, 
                                        sports_winloss.home_losses, sports_winloss.away_losses 
                        FROM sports_attend 
                        JOIN sports_winloss 
                        ON sports_attend.name = sports_winloss.city  
                        AND sports_attend.year = sports_winloss.year 
                        WHERE sports_winloss.league= ?
                        AND sports_attend.league = ?''', (league, league, ))
    else:
        db_cur.execute('''SELECT DISTINCT sports_attend.name, sports_winloss.mascot, 
                                      sports_attend.year, sports_attend.average, sports_attend.league,
                                      sports_winloss.home_wins, sports_winloss.away_wins, 
                                      sports_winloss.home_losses, sports_winloss.away_losses 
                      FROM sports_attend 
                      JOIN sports_winloss 
                      ON sports_attend.name = sports_winloss.mascot  
                      AND sports_attend.year = sports_winloss.year 
                      WHERE sports_winloss.league= "NBA"
                      AND sports_attend.league = "NBA"''')
    r_lsit = db_cur.fetchall()
    db_cur.close()
    return r_lsit
   

db_conn = sqlite3.connect("sports_records.db")
db_cur = db_conn.cursor()

def get_what_we_want(data):
    '''
    Formats the data collected from reconds_and_attendace_nfl() so that we can later plot. 
    Input is the data. Outputs a dictionary of data
    '''

    dic = {}
    for i in data:
        if i[0] == "New York" or i[0] == 'Los Angeles':
            pass
        if i[1] not in dic:
            dic[i[1]] = []
        dic[i[1]].append((i[3], i[5]+i[6]))
    return dic

def plotting(league):
    '''
    Takes in a league that you wish to see data plotted, and calls other functions to create the plot.
    '''

    dic = get_what_we_want(reconds_and_attendace(league, db_cur, db_conn))
    for team in dic.keys():
        x = []
        y = []
        for i in dic[team]:
            x.append(i[0])
            y.append(i[1])
        plt.scatter(x, y, label=team)
        # Add labels and title
    plt.title("Wins V. Game Attendace {}".format(league))
    plt.xlabel("Attendance")
    plt.ylabel("Games Won")
        
    plt.legend()
    plt.show()

### Uncomment bellow and input a league
#plotting("NBA")
