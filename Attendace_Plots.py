import matplotlib.pyplot as plt
import sqlite3
import requests
import os
import pprint

def reconds_and_attendace_nfl(league, cur, conn):
    path = os.path.dirname(os.path.abspath(__file__))
    db_conn = sqlite3.connect(path+'/'+"sports_records.db")
    db_cur = db_conn.cursor()
    category_id_dict = {}
    db_cur.execute("SELECT * FROM sports_winloss")
    for row in db_cur:
        category_id_dict[row[1]] = row[0]

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
    r_lsit = db_cur.fetchall()
    db_cur.close()
    return r_lsit

db_conn = sqlite3.connect("sports_records.db")
db_cur = db_conn.cursor()

nfl = reconds_and_attendace_nfl("NFL", db_cur, db_conn)

def get_what_we_want(data):
    dic = {}
    for i in data:
        if i[0] == "New York" or i[0] == 'Los Angeles':
            pass
        if i[1] not in dic:
            dic[i[1]] = []
        dic[i[1]].append((i[3], i[5]+i[6]))
    return dic

def plotting_nfl(league):
    if league == 'NFL' or league == 'MLB' or league == 'NHL':
        dic = get_what_we_want(reconds_and_attendace_nfl(league, db_cur, db_conn))
    else:
        return print("Can't do that quite yet")
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
#plotting_nfl("NHL")
