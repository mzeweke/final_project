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
    '''Takes a year, a league (MLB, NFL, NBA, NHL), a cursor object and a connect object as input.
    Selects relevant data from the database, and from it, calculates percent home and away wins
    and total percent wins.  Stores this data in a list of dictionaries.  Returns this list.'''

    cur.execute('SELECT city, mascot, league, home_wins, home_losses, home_ties, away_wins, away_losses, away_ties FROM sports_records WHERE year = {}'.format(year))
    tuples = cur.fetchall()
    dict_list = []
    for tuple in tuples:
        if tuple[2] == league:
            league_records = {}
            tup = [tuple[0], tuple[1], [tuple[3], tuple[4], tuple[5]], [tuple[6], tuple[7], tuple[8]]]
            league_records["name"] = tup[0] + " " + tup[1]

            n_home = tup[2][0]+tup[2][1]+tup[2][2]
            league_records["n_home"] = n_home 

            n_away = tup[3][0]+tup[3][1]+tup[3][2]
            league_records["n_away"] = n_away

            p_home = tup[2][0]/n_home
            league_records["p_home"] = p_home

            p_away = tup[3][0]/n_away
            league_records["p_away"] = p_away

            p_hat = (tup[2][0]+tup[3][0])/(n_home+n_away)
            league_records["p_hat"] = p_hat
            dict_list.append(league_records)
    return dict_list

def calculate_z_score(record):
    '''Takes a dictionary 'record' as input.  Uses a formula to calculate the z-score for the data
    in the dictionary.  Adds the z-score to the dictionary.  Does not return.'''

    if record["p_hat"] != 0:
        z = (record["p_home"]-record["p_away"])/math.sqrt( (record["p_hat"] * (1-record["p_hat"])) * ((1/record["n_home"])+(1/record["n_away"])) )
    else:
        z = 0
    record["z"] = z

def run_hypothesis_test(record, alpha):
    '''Takes a dictionary 'record' and alpha value as input.  Calculates whether or not the data from
    the dictionary is statistically significant with regard to alpha, in other words, is there a home
    field advantage?  Adds a bool to the dictionary.  Does not return.'''

    if alpha == 0.10:
        z_star = 1.28
    if alpha == 0.05:
        z_star = 1.28
    if alpha == 0.01:
        z_star = 2.33
    z = record["z"]
    if z > z_star:   
        record['HFA'] = True
    else:
        record['HFA'] = False

def conclusions(stats_output):
    '''Takes a list of dictionaries as input.  Counts the number of statistically significant results
    in the dictionary.  Returns the proportion of statistically significant results.'''

    count = 0
    for entry in stats_output:
        if entry['HFA'] == True:
            count = count + 1
    return count/len(stats_output)

def abbreviate(name):
    '''Takes a name as input.  Calculates an abbreviation for the name.  Returns this abbreviation.'''
    abbrev = ""
    for char in name:
        if char.isupper():
            abbrev = abbrev + char
    if abbrev == "P":
        abbrev = abbrev + str(76)
    return abbrev

def run_tests_on_all_data(years, leagues, cur, conn, alpha, filename):
    '''Takes a list of years, a list of leagues, a cursor object, a connect object, an alpha value, and
    a filename as input.  Runs hypothesis tests on all of the data and outputs the results to filename.
    Does not return.'''

    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    file = open(path + filename, 'w')
    file.write("Two Proportion Hypothesis Test Results:\n\n")
    lines = []
    for year in years:
        for league in leagues:
            season_records = get_leage_records_for_year(year, league, cur, conn)
            for record in season_records:
                calculate_z_score(record)
                run_hypothesis_test(record, alpha)
            result = conclusions(season_records)*100
            file.write('  ' + league + ' ' +str(year) + "...\n")
            file.write("    At an alpha = " + str(alpha) +  " significance level, the data suggests that " + str(result) + "%\n")
            file.write("    of teams in the " + league +  " seemed to have a home-field advantage in " + str(year) + ".\n\n")
    file.close()


def get_box_plot_data(year, leagues, cur, conn):
    '''Takes a year, a league, a cursor object, and a connect object.  Loops through the data and returns
    a list of parallel lists of data to be used in the box_plot function.'''

    data_list = []
    for league in leagues:
        league_records = get_leage_records_for_year(year, league, cur, conn)
        for record in league_records:
            calculate_z_score(record)
        p_homes = []
        p_aways = []
        for data in league_records:
            p_homes.append(data["p_home"])
            p_aways.append(data["p_away"])
        data = [p_homes, p_aways]
        data_list.append(data)
    return data_list

def get_line_plot_data(year, leagues, cur, conn):
    '''Takes a year, a league, a cursor object, and a connect object.  Loops through the data and returns
    a list of parallel lists of data to be used in the line_plot function.'''

    data_list = []
    for league in leagues:
        league_records = get_leage_records_for_year(year, league, cur, conn)
        for record in league_records:
            calculate_z_score(record)
        teams = []
        p_homes = []
        p_aways = []
        fifty = []
        i = 1
        num = []
        for data in league_records:
            teams.append(abbreviate(data['name']))
            p_homes.append(data["p_home"])
            p_aways.append(data['p_away'])
            fifty.append(.5)
            num.append(i); i = i + 1
        data = [teams, p_homes, fifty, num, p_aways]
        data_list.append(data)
    return data_list

def line_plot(data_list, year):
    '''Takes a list of parallel lists and a year.  Generates a line plot of the data.  Does not
    return.'''

    fig = plt.figure()
    leagues = ["MLB", "NFL", "NBA", "NHL"]
    fig_num = 1
    for data in data_list:
        strnum = "22" + str(fig_num)
        ax = fig.add_subplot(int(strnum))
        ax.plot(data[0], data[1], color="#42B165", marker ="o", linestyle="none")
        ax.plot(data[0], data[4], color="#CF2460", marker ="o", linestyle="none")
        ax.plot(data[0], data[2], color = "black")
        ax.set_title("Home Game Wins\n" + leagues[fig_num-1] + " " + str(year))
        ax.set_ylabel("Home Wins (%)")
        ax.set_xlabel(leagues[fig_num-1] + " teams")
        ax.set_xticklabels(data[0], rotation="vertical")
        fig_num = fig_num + 1
    fig.tight_layout()
    plt.show()

def box_plot(data_list, year):
    '''Takes a list of parallel lists and a year.  Generates a box plot of the data.  Does not return.'''

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

    run_tests_on_all_data(years, leagues, cur, conn, 0.10, "stats_calcs.txt")

    box_data2019 = get_box_plot_data(2019, leagues, cur, conn)
    box_plot(box_data2019, 2019)

    line_data2019 = get_line_plot_data(2019, leagues, cur, conn)
    line_plot(line_data2019, 2019)