import json
import math
from math import log2


def champ_id_remap():
    original_champ_id = {}
    remapped_champ_id = {}

    with open('./metadata/id_to_key.json', 'r') as fp:
        original_champ_id = json.load(fp)

    for i, champ_name in enumerate(original_champ_id):
        remapped_champ_id[original_champ_id[champ_name]] = i
    
    return remapped_champ_id


def get_original_champ_id(remapped_champ_id, champ_idx):
    for original_id, remapped_id in remapped_champ_id.iteritems():
        if remapped_id == champ_idx:
            return original_id

        
        

def make_idf_table():
    remapped_champ_id = champ_id_remap()
    idf_table = [0 for _ in range(len(remapped_champ_id))]
    total_user_num = 0

    # batch for userlist 2
    for i in range(12):
        batch_file = './data_batch/batch2_' + str(i) + '.json'
        with open(batch_file, 'r') as fp:
            batch_data = json.load(fp)

        for user_name in batch_data:
            for champ_history in batch_data[user_name]['champion_history']:
                champ_idx = remapped_champ_id[champ_history['champion_key']]
                idf_table[champ_idx] += 1

            total_user_num += 1

    # batch for userlist 3
    for i in range(4):
        batch_file = './data_batch/batch3_' + str(i) + '.json'
        with open(batch_file, 'r') as fp:
            batch_data = json.load(fp)

        for user_name in batch_data:
            for champ_history in batch_data[user_name]['champion_history']:
                champ_idx = remapped_champ_id[champ_history['champion_key']]
                idf_table[champ_idx] += 1

            total_user_num += 1

    # batch for userlist 4
    for i in range(3):
        batch_file = './data_batch/batch4_' + str(i) + '.json'
        with open(batch_file, 'r') as fp:
            batch_data = json.load(fp)

        for user_name in batch_data:
            for champ_history in batch_data[user_name]['champion_history']:
                champ_idx = remapped_champ_id[champ_history['champion_key']]
                idf_table[champ_idx] += 1

            total_user_num += 1

    idf_table = [log2(total_user_num / i) for i in idf_table]

    return idf_table
        
        
        
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

