import json
from math import log2
from champ_id_remap import champ_id_remap

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
