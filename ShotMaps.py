"""
Take shot data from SQLite database and plot as a shotmap.
If database doesn't exist creates one.

Currently doesn't look good for players who have taken many shots.
Takes no extra arguments, just plot all shots a player has ever taken in the top 5 european leagues.
"""
import os
import sqlite3
import pandas as pd
from ScrapeUnderstat import *
import matplotlib.pyplot as plt
from mplsoccer.pitch import VerticalPitch


def plot_shotmap():
    team = input("Team Name (No spaces):  ")
    player = input("Player Name (With spaces):  ")
    dir_name = os.path.dirname(__file__)
    path = os.path.join(dir_name, "Databases", "Players", team, player.replace(" ", ""))
    if not os.path.exists(path):
        os.makedirs(path)
        conn = sqlite3.connect(os.path.join(dir_name, "Databases", "2021", "All_Player_data.db"))
        sql_query = """SELECT id, player_name
        FROM All_Player_Data
        WHERE player_name = '""" + player + "'"

        data = pd.read_sql(sql_query, conn)
        conn.close()
        try:
            code = int(data.id)
        except:
            code = input("Player Code:  ")
        get_database("player", code)

    conn = sqlite3.connect(os.path.join(path, player.replace(" ", "") + "_All_Shots_Data.db"))
    sql_query = """SELECT date, minute, result, h_a, X, Y,
        CAST(xG AS REAL)*500 as scaled_xg,
        X*120 AS y,
        (1-Y)*80 AS x
        FROM """ + player.replace(" ", "") + "_All_Shots_Data"
    data = pd.read_sql(sql_query, conn)
    conn.close()

    data_goals = data.loc[data.result == 'Goal']
    data_nongoals = data.loc[data.result != 'Goal']
    goals = [data_goals.x.values.tolist(), data_goals.y.values.tolist(), data_goals.scaled_xg.values.tolist()]
    nongoals = [data_nongoals.x.values.tolist(), data_nongoals.y.values.tolist(), data_nongoals.scaled_xg.values.tolist()]

    fig, axs = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#03021a')
    pitch = VerticalPitch(pitch_color='#03021a', line_color='white', half=True, pad_bottom=-25)
    pitch.draw(ax=axs)

    plt.scatter(goals[0], goals[1], goals[2], alpha=0.75, label='Goals')
    plt.scatter(nongoals[0], nongoals[1], nongoals[2], alpha=0.75, label='Non-Goals')
    plt.suptitle(player, y=0.72, x=0.51, fontsize=22, color='w')
    plt.title('League Games', y=0.95, fontsize=14, color='w')
    plt.legend(loc="lower left", fontsize=15, markerscale=1)
    plt.show()

if __name__ == "__main__":
    plot_shotmap()