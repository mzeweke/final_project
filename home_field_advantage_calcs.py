import matplotlib.pyplot as plt
import numpy as np
import requests
import sqlite3
import time
import math
import csv
import re
import os

def get_leage_records_for_year(year, league, cur, conn):
    cur.execute('SELECT city, mascot, league, home_wins, home_losses, home_ties, away_wins, away_losses, away_ties FROM sports_records WHERE year = {}'.format(year))
    tuples = cur.fetchall()
    league_records = []
    for tuple in tuples:
        if tuple[2] == league:
            tup = [tuple[0], tuple[1], [tuple[3], tuple[4], tuple[5]], [tuple[6], tuple[7], tuple[8]]]
            league_records.append(tup)
    return league_records

def calculate_z_score(league_records, z_star):
    '''
    Calculates the z-score and whether we reject the null hypothesis at the alpha significance
    level... in English: calculates whether each team has a Home Field Advantage
    '''
    list = []
    for record in league_records:
        dict = {}
        dict["team_name"] = record[0] + " " + record[1]
        home_n = record[2][0] + record[2][1] + record[2][2]
        away_n = record[3][0] + record[3][1] + record[3][2]
        home_p = (record[2][0]/home_n)
        away_p = (record[3][0]/away_n)
        p_hat = (record[2][0]+record[3][0])/(home_n+away_n)
        if p_hat != 0:
            z = (home_p-away_p)/math.sqrt( (p_hat * (1-p_hat)) * ((1/home_n)+(1/away_n)) )
        else:
            z = 0
        dict['z'] = z
        dict['home_p'] = home_p
        dict['away_p'] = away_p
        if z > z_star:
            dict['HFA'] = True
        else:
            dict['HFA'] = False
        list.append(dict)
    return list

def conclusions(stats_output):
    count = 0
    for entry in stats_output:
        if entry['HFA'] == True:
            count = count + 1
    return count/len(stats_output)

def hypothesis_test(year, league, cur, conn, alpha):
    print("  " + league + "...")
    if alpha == 0.10:
        z_star = 1.28
    if alpha == 0.05:
        z_star = 1.28
    if alpha == 0.01:
        z_star = 2.33
    records = get_leage_records_for_year(year, league, cur, conn)
    stats_output = calculate_z_score(records, z_star)
    conclusion = conclusions(stats_output)*100
    print("    At an alpha = " + str(alpha) +  " significance level, the data suggests that " + str(conclusion) + "%")
    print("    of teams in the " + league +  " seemed to have a home-field advantage in " + str(year) + ".\n")
    return conclusion

def avg(list):
    sum = 0
    for i in list:
        sum = sum + i
    return sum/len(list)

def run_tests_on_all_data(years, leagues, cur, conn, alpha):
    MLB = [];    NFL = [];    NBA = [];    NHL = []
    for year in years:
        print("Calculating data from " + str(year) + "...")
        for league in leagues:
            conclusion = hypothesis_test(year, league, cur, conn, alpha)
            if league == "MLB":
                MLB.append(conclusion)
            if league == "NFL":
                NFL.append(conclusion)
            if league == "NBA":
                NBA.append(conclusion)
            if league == "NHL":
                NHL.append(conclusion)
    avgMLB = avg(MLB); avgNFL = avg(NFL); avgNBA = avg(NBA); avgNHL = avg(NHL)
    print("Calculating the average home-field advantages...")
    print("  MLB...   " + str(avgMLB) + "%")
    print("  NFL...   " + str(avgNFL) + "%")
    print("  NBA...   " + str(avgNBA) + "%")
    print("  NHL...   " + str(avgNHL) + "%\n")

def get_box_plot_data(year, leagues, cur, conn, z_star):
    data_list = []
    for league in leagues:
        league_records = get_leage_records_for_year(year, league, cur, conn)
        list = calculate_z_score(league_records, z_star)
        home_p_list = []
        away_p_list = []
        for data in list:
            home_p_list.append(data["home_p"])
            away_p_list.append(data["away_p"])
        data = [home_p_list, away_p_list]
        data_list.append(data)
    return data_list

def get_line_plot_data(year, leagues, cur, conn, z_star):
    data_list = []
    for league in leagues:
        league_records = get_leage_records_for_year(year, league, cur, conn)
        list = calculate_z_score(league_records, z_star)
        teams = []
        home_p_list = []
        fifty = []
        i = 1
        num = []
        for rec in list:
            name = rec["team_name"]
            abbrev = ""
            for char in name:
                if char.isupper():
                    abbrev = abbrev + char
            if abbrev == "P":
                abbrev = abbrev + str(76)
            teams.append(abbrev)
            home_p_list.append(rec["home_p"])
            fifty.append(.5)
            num.append(i); i = i + 1
        data = [teams, home_p_list, fifty, num]
        print(data[0])
        data_list.append(data)
    return data_list

def line_plot(data_list, year):
    fig = plt.figure()
    leagues = ["MLB", "NFL", "NBA", "NHL"]
    fig_num = 1
    for data in data_list:
        strnum = "22" + str(fig_num)
        ax = fig.add_subplot(int(strnum))
        ax.plot(data[0], data[1], marker ="o", linestyle="none")
        ax.plot(data[0], data[2])
        ax.set_title("Home Game Wins\n" + leagues[fig_num-1] + " " + str(year))
        ax.set_ylabel("Home Wins (%)")
        ax.set_xlabel(leagues[fig_num-1] + " teams")
        ax.set_xticklabels(data[0], rotation="vertical")
        fig_num = fig_num + 1
    fig.tight_layout()
    plt.show()

def box_plot(data_list, year):
    fig = plt.figure()
    leagues = ["MLB", "NFL", "NBA", "NHL"]
    fig_num = 1
    for data in data_list:
        strnum = "22" + str(fig_num)
        ax = fig.add_subplot(int(strnum))
        ax.set_title("Difference in Performance Home vs. Away\n" + leagues[fig_num-1] + " " + str(year))
        ax.set_ylabel("Percentage of Games Won (%)")
        ax.set_xticklabels(["Home", "Away"])
        bp = ax.boxplot(data, patch_artist=True)
        fig_num = fig_num + 1
        i = 0
        for box in bp['boxes']:
            box.set(color='black', linewidth=2)
            if i == 0:
                box.set(facecolor = "lightgreen")
                i = i + 1
            else:
                box.set(facecolor = "pink")
        for whisker in bp['whiskers']:
            whisker.set(color='black', linewidth=2)
        for cap in bp['caps']:
            cap.set(color='black', linewidth=2)
        for median in bp['medians']:
            median.set(color='black', linewidth=2)
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+'sports_records.db')
    cur = conn.cursor()
    years = [2017, 2018, 2019]; leagues = ["MLB", "NFL", "NBA", "NHL"]

    run_tests_on_all_data(years, leagues, cur, conn, 0.10)

    #box_data2019 = get_box_plot_data(2019, leagues, cur, conn, 1.28)
    #box_plot(box_data2019, 2019)

    #line_data2019 = get_line_plot_data(2019, leagues, cur, conn, 1.28)
    #line_plot(line_data2019, 2019)