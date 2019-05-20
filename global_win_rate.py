import json
import math
from champ_id_remap import champ_id_remap

# index for tuple in global_win_stat list
WIN = 0
PLAY = 1

def global_win_rate():
    remapped_champ_id = champ_id_remap()
    global_win_stat = [[0, 0] for _ in range(len(remapped_champ_id))]

    with open('./data_batch/userbatch.json', 'r') as fp:
        user_data = json.load(fp)

    for user_name in user_data:
        for champ_history in user_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = remapped_champ_id[original_champ_id]

            this_champ_play = champ_history['play_count']
            this_champ_win = math.ceil(this_champ_play * champ_history['win_rate'])

            global_win_stat[champ_idx][WIN] += this_champ_win
            global_win_stat[champ_idx][PLAY] += this_champ_play

    global_win_rate = [(round(global_win_stat[i][WIN] / global_win_stat[i][PLAY], 2)) for i in range(len(global_win_stat))]

    return global_win_rate

if __name__ == '__main__':
    global_win_rate()
