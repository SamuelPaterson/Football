"""
Scrape understat, convert to SQLite DB then save.
Drops useless information from DB such as understat's IDs.

Understat URLs are formatted as following:
    for players:    understat.com/player/"UNIQUE NUMBER CODE"
    for teams:      understat.com/team/"TEAM_NAME"/"SEASON STARTING YEAR"
    for games:      understat.com/match/"UNIQUE NUMBER CODE"
    for leagues:    understat.com/league/"LEAGUE NAME"/"SEASON START YEAR (if blanck current)"

Currently, getting useless database under player remove after testing and delete from files.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import sqlite3
import os

def get_database():
    base_url = "https://understat.com/"
    extension = "league"
    code = "Serie_A"
    year = "2021"
    if extension == "league":
        understat_url = base_url + extension + "/" + code + "/" + year
    else:
        understat_url = base_url + extension + "/" + code
    res = requests.get(understat_url)
    soup = BeautifulSoup(res.content, "lxml")
    scripts = soup.find_all("script")
    string_list = []
    for script in scripts:
        string = str(script)  # Convert into string
        if ("('" and "')") in string:
            ind_start = string.index("('") + 2
            ind_end = string.index("')")
            json_data = string[ind_start:ind_end]  # Index to only have json
            json_data = json_data.encode('utf8').decode('unicode_escape')
            string_list.append(json_data)  # List of json data in string format

    if extension == "player":
        get_player(string_list, soup)
    if extension == "team":
        get_team()
    if extension == "match":
        get_match()
    if extension == "league":
        get_league(string_list, soup, code, year)



'''
If getting stats for a player. 5 Databases
0 = All seasons all stats in 1 row.
1 = Stats per min in 1 row
2 = All Shot data
3 = All game data
4 = Ad data for website (ignore)
'''
def get_player(string_list, soup):
    dir_name = os.path.dirname(__file__)
    title = str(soup.find("title"))[7:-53]
    player_name = title[0:title.index("|") - 1].replace(" ", "")
    team_name = title[title.index("|") + 2:len(title)].replace(" ", "")
    index = 0
    for string in string_list:
        if len(string) > 0:
            data = json.loads(string)  # Convert from string into json
            df = pd.json_normalize(data)
            df = df.applymap(str)
            path = os.path.join(dir_name, "Databases", "Players", team_name, player_name)
            if not os.path.exists(path):
                os.makedirs(path)
            if index == 0:
                db_name = player_name + '_All_Seasons_(ignore for now)'
            elif index == 1:
                db_name = player_name + '_Stats_Per_Min'
            elif index == 2:
                db_name = player_name + '_All_Shots_Data'
                df = df.drop(columns=['id', 'player_id', 'season', 'match_id'])
            elif index == 3:
                db_name = player_name + '_All_Game_Data'
            elif index == 4:
                break
            path = os.path.join(path, db_name + '.db')
            print(path)
            conn = sqlite3.connect(path)
            df.to_sql(db_name, conn, if_exists='replace')
            index = index + 1
    conn.close()

def get_team():
    print("Team search not implemented yet")

def get_match():
    print("Match search not implemented yet")

'''
Get_league returns 4 DB
0 = Game results, including xg. for the season
1 = all teams there id and history (all in one row)
2 = ALL PLAYER DATA. Inc name id, season goals, xg ect.
3 = Ad data
'''
def get_league(string_list, soup, code, year):
    dir_name = os.path.dirname(__file__)
    index = 0
    for string in string_list:
        if len(string) > 0:
            data = json.loads(string)  # Convert from string into json
            df = pd.json_normalize(data)
            df = df.applymap(str)
            path = os.path.join(dir_name, "Databases", "Leagues", code, year)
            if not os.path.exists(path):
                os.makedirs(path)
            if index == 0:
                db_name = "Game_Results"
            if index == 1:
                db_name = "Teams_History"
            if index == 2:
                db_name = "All_Player_Data"
                path = os.path.join(dir_name, "Databases", year)
                if not os.path.exists(path):
                    os.makedirs(path)
                path = os.path.join(path, "All_Player_Data.db")
                print(path)
                conn = sqlite3.connect(path)
                df.insert(14, 'League', code)
                df.to_sql(db_name, conn, if_exists='append')
                break
            path = os.path.join(path, db_name + '.db')
            print(path)
            conn = sqlite3.connect(path)
            df.to_sql(db_name, conn, if_exists='replace')
            index = index+1
    conn.close()


if __name__ == "__main__":
    get_database()
