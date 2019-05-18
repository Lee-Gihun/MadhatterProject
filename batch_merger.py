import json
import sys

if __name__ == '__main__':
    user_batch = {}
    # batch for userlist 2
    for i in range(12):
        batch_file = './data_batch/batch2_' + str(i) + '.json'
        with open(batch_file, 'r') as fp:
            per_user_batch = json.load(fp)

        user_batch.update(per_user_batch)

    # batch for userlist 3
    for i in range(4):
        batch_file = './data_batch/batch3_' + str(i) + '.json'
        with open(batch_file, 'r') as fp:
            per_user_batch = json.load(fp)

        user_batch.update(per_user_batch)

    # batch for userlist 4
    for i in range(3):
        batch_file = './data_batch/batch4_' + str(i) + '.json'
        with open(batch_file, 'r') as fp:
            per_user_batch = json.load(fp)

        user_batch.update(per_user_batch)

    with open('./data_batch/userbatch.json', 'w') as fp:
        json.dump(user_batch, fp)
