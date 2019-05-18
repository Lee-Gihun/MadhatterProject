import json
from make_idf_table import make_idf_table
from champ_id_remap import champ_id_remap
import sys

class UserVectorGenerator():
    def __init__(self, batch_file, mode):
        """
        mode: Determine which method to generate user vectors
            1: Naive method. Just get literal value from data
            2: TF-IDF method. Calcuate TF-IDF value for each vector value
        """
        self.remapped_champ_id = champ_id_remap()
        self.champ_num = len(self.remapped_champ_id)
        self.mode = mode

        with open(batch_file, 'r') as fp:
            self.batch_data = json.load(fp)

    def _get_max_play_count(self, user_name):
        """
        Get count of maximally played champion for user_name
        """
        max_play_count = 0

        for champ_history in self.batch_data[user_name]['champion_history']:
            champ_play_count = champ_history['play_count']
            if max_play_count < champ_play_count:
                max_play_count = champ_play_count

        return max_play_count

    def _get_play_count_vector(self, user_name):
        play_count_vector = [0 for _ in range(self.champ_num)]

        if self.mode == 1: # Naive mode
            for champ_history in self.batch_data[user_name]['champion_history']:
                original_champ_id = champ_history['champion_key']
                champ_idx = self.remapped_champ_id[original_champ_id]

                play_count_vector[champ_idx] = champ_history['play_count']
        elif self.mode == 2: # TF-IDF mode
            max_play_count = self._get_max_play_count(user_name)

            for champ_history in self.batch_data[user_name]['champion_history']:
                original_champ_id = champ_history['champion_key']
                champ_idx = self.remapped_champ_id[original_champ_id]
                play_count_tf_idf = (champ_history['play_count'] / max_play_count) * idf_table[champ_idx]

                play_count_vector[champ_idx] = play_count_tf_idf

        return play_count_vector

    def _get_max_mastery_score(self, user_name):
        """
        Get maximum mastery score of user_name
        """
        max_mastery_score = 0

        for champ_history in self.batch_data[user_name]['champion_history']:
            mastery_score = champ_history['championPoints']
            if max_mastery_score < mastery_score:
                max_mastery_score = mastery_score

        return max_mastery_score

    def _get_mastery_score_vector(self, user_name):
        mastery_score_vector = [0 for _ in range(self.champ_num)]
        
        if self.mode == 1: # Naive mode
            for champ_history in self.batch_data[user_name]['champion_history']:
                original_champ_id = champ_history['champion_key']
                champ_idx = self.remapped_champ_id[original_champ_id]

                mastery_score_vector[champ_idx] = champ_history['championPoints']
        elif self.mode == 2: # TF-IDF mode
            max_mastery_score = self._get_max_mastery_score(user_name)

            for champ_history in self.batch_data[user_name]['champion_history']:
                original_champ_id = champ_history['champion_key']
                champ_idx = self.remapped_champ_id[original_champ_id]
                mastery_tf_idf = (champ_history['championPoints'] / max_mastery_score) * idf_table[champ_idx]

                mastery_score_vector[champ_idx] = mastery_tf_idf

        return mastery_score_vector

    def make_user_vectors(self):
        user_vectors = {}

        for user_name in self.batch_data:
            play_count_vector = self._get_play_count_vector(user_name)
            mastery_score_vector = self._get_mastery_score_vector(user_name)
            user_vectors[user_name] = play_count_vector + mastery_score_vector

        return user_vectors

if __name__ == '__main__':
    user_vectors = {}
    mode = int(sys.argv[1])

    if mode == 2: # TF-IDF mode
        idf_table = make_idf_table()

    # batch for userlist 2
    for i in range(12):
        batch_file = './data_batch/batch2_' + str(i) + '.json'
        user_vector_generator = UserVectorGenerator(batch_file, mode)
        user_vectors.update(user_vector_generator.make_user_vectors())

    # batch for userlist 3
    for i in range(4):
        batch_file = './data_batch/batch3_' + str(i) + '.json'
        user_vector_generator = UserVectorGenerator(batch_file, mode)
        user_vectors.update(user_vector_generator.make_user_vectors())

    # batch for userlist 4
    for i in range(3):
        batch_file = './data_batch/batch4_' + str(i) + '.json'
        user_vector_generator = UserVectorGenerator(batch_file, mode)
        user_vectors.update(user_vector_generator.make_user_vectors())

    if mode == 1:
        user_vectors_file = './datasets/user_vectors_naive.json'
    elif mode == 2:
        user_vectors_file = './datasets/user_vectors_tf_idf.json'

    with open(user_vectors_file, 'w') as fp:
        json.dump(user_vectors, fp)
