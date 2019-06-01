import json
import csv
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
    for original_id, remapped_id in remapped_champ_id.items():
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
        
def global_win_rate():
    # index for tuple in global_win_stat list
    WIN = 0
    PLAY = 1
    remapped_champ_id = champ_id_remap()
    global_win_stat = [[0, 0] for _ in range(len(remapped_champ_id))]

    with open('./data_batch/userbatch.json', 'r') as fp:
        user_data = json.load(fp)

    for user_name in user_data:
        for champ_history in user_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = remapped_champ_id[original_champ_id]

            this_champ_play = champ_history['play_count']
            this_champ_win = this_champ_play * champ_history['win_rate']

            global_win_stat[champ_idx][WIN] += this_champ_win
            global_win_stat[champ_idx][PLAY] += this_champ_play

    global_win_rate = [(round(global_win_stat[i][WIN] / global_win_stat[i][PLAY], 3)) for i in range(len(global_win_stat))]

    return global_win_rate

def champion_similarity_csv_to_json():
    similarity_matrix = dict()
    remapped_champ_id = champ_id_remap()

    with open('./metadata/id_to_key.json', 'r') as f:
        original_champ_id_dict = json.load(f)

    champ_node_file = open('./datasets/allchampions_nodes.csv', 'r')
    champ_node_reader = csv.reader(champ_node_file, delimiter=',')
    node_column = next(champ_node_reader)

    champ_edge_file = open('./datasets/allchampions_edges.csv', 'r')
    champ_edge_reader = csv.reader(champ_edge_file, delimiter=',')
    edge_column = next(champ_edge_reader)

    CHAMP_NAME = 1
    for champ_node_row in champ_node_reader:
        champ_name = champ_node_row[CHAMP_NAME]
        original_champ_id = original_champ_id_dict[champ_name]
        champ_idx = remapped_champ_id[original_champ_id]
        similarity_matrix[champ_idx] = [0 for _ in range(len(original_champ_id_dict))]

    SOURCE_CHAMP = 0
    TARGET_CHAMP = 1
    EDGE_WEIGHT = 2
    for champ_edge_row in champ_edge_reader:
        source_champ_idx = remapped_champ_id[original_champ_id_dict[champ_edge_row[SOURCE_CHAMP]]]
        target_champ_idx = remapped_champ_id[original_champ_id_dict[champ_edge_row[TARGET_CHAMP]]]
        weight = float(champ_edge_row[EDGE_WEIGHT])

        if similarity_matrix[source_champ_idx][target_champ_idx] == 0 and \
           similarity_matrix[target_champ_idx][source_champ_idx] == 0:
            similarity_matrix[source_champ_idx][target_champ_idx] = weight
            similarity_matrix[target_champ_idx][source_champ_idx] = weight

    with open('./datasets/item_vectors_weights.json', 'w') as f:
        json.dump(similarity_matrix, f)
