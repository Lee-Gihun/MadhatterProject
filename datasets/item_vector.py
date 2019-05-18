import json
from make_idf_table import make_idf_table
from champ_id_remap import champ_id_remap
from math import sqrt
import sys

class ItemVectorGenerator():
    def __init__(self, batch_file):
        self.remapped_champ_id = champ_id_remap()
        self.champ_num = len(self.remapped_champ_id)

        with open(batch_file, 'r') as fp:
            self.batch_data = json.load(fp)

    def _get_max_play_count(self, user_name):
        """
        Get count of maximally played champion for user_name
        """
        _max_play_count = 0

        for champ_history in self.batch_data[user_name]['champion_history']:
            champ_play_count = champ_history['play_count']
            if _max_play_count < champ_play_count:
                _max_play_count = champ_play_count

        return _max_play_count

    def _get_play_count_tf_idf_vector(self, user_name):
        play_count_tf_idf_vector = [0 for _ in range(self.champ_num)]
        max_play_count = self._get_max_play_count(user_name)

        for champ_history in self.batch_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = self.remapped_champ_id[original_champ_id]
            play_count_tf_idf = (champ_history['play_count'] / max_play_count) * idf_table[champ_idx]

            play_count_tf_idf_vector[champ_idx] = play_count_tf_idf

        return play_count_tf_idf_vector

    def _get_champ_vector(self, tf_idf_matrix, champ_idx):
        _champ_vector = []

        for user_name in tf_idf_matrix:
            _champ_vector.append(tf_idf_matrix[user_name][champ_idx])

        return _champ_vector

    def _get_intersect_user_pos(self, champ_a_vector, champ_b_vector):
        _intersect_user_pos = []

        for i in range(len(champ_a_vector)):
            if (champ_a_vector[i] != 0) and (champ_b_vector[i] != 0):
                _intersect_user_pos.append(i)

        return _intersect_user_pos

    def _compute_similarity(self, champ_a_vector, champ_b_vector):
        assert(len(champ_a_vector) == len(champ_b_vector))
        champ_a_b_inner_prod = 0
        champ_a_norm = 0
        champ_b_norm = 0

        # Get user position where both of champ a and b are played
        intersect_user_pos = self._get_intersect_user_pos(champ_a_vector, champ_b_vector)

        # Use cosine similarity
        if len(intersect_user_pos) > 0:
            for i in range(len(intersect_user_pos)):
                champ_a_b_inner_prod += champ_a_vector[i] * champ_b_vector[i]
                champ_a_norm += champ_a_vector[i] ** 2
                champ_b_norm += champ_b_vector[i] ** 2

            if champ_a_norm != 0 and champ_b_norm != 0:
                _sim_a_b = champ_a_b_inner_prod / (sqrt(champ_a_norm) * sqrt(champ_b_norm))
            else:
                _sim_a_b = 0.0
        else:
            _sim_a_b = 0.0

        return _sim_a_b
                
    def _get_champ_corr_matrix(self, tf_idf_matrix):
        _champ_corr_matrix = {}

        # Initialize _champ_corr_matrix
        for champ_idx in range(self.champ_num):
            _champ_corr_matrix[champ_idx] = [0.0 for _ in range(self.champ_num)]

        for champ_a_idx in range(self.champ_num):
            champ_a_vector = self._get_champ_vector(tf_idf_matrix, champ_a_idx)

            for champ_b_idx in range(self.champ_num):
                if champ_b_idx < champ_a_idx:
                    sim_a_b = _champ_corr_matrix[champ_b_idx][champ_a_idx]
                elif champ_b_idx == champ_a_idx:
                    sim_a_b = 1.0
                else:
                    champ_b_vector = self._get_champ_vector(tf_idf_matrix, champ_b_idx)
                    sim_a_b = self._compute_similarity(champ_a_vector, champ_b_vector)

                _champ_corr_matrix[champ_a_idx][champ_b_idx] = sim_a_b

        return _champ_corr_matrix

    def make_item_vectors(self):
        tf_idf_matrix = {} # tf_idf vector for each user
        champ_corr_matrix = {} # champ_num by champ_num matrix

        for user_name in self.batch_data:
            play_count_tf_idf_vector = self._get_play_count_tf_idf_vector(user_name)
            tf_idf_matrix[user_name] = play_count_tf_idf_vector

        champ_corr_matrix = self._get_champ_corr_matrix(tf_idf_matrix)

        return champ_corr_matrix

if __name__ == '__main__':
    item_vectors = {}
    idf_table = make_idf_table()

    # batch for userlist 2
    for i in range(12):
        batch_file = '../data_batch/batch2_' + str(i) + '.json'
        item_vector_generator = ItemVectorGenerator(batch_file)
        item_vectors.update(item_vector_generator.make_item_vectors())

    # batch for userlist 3
    for i in range(4):
        batch_file = '../data_batch/batch3_' + str(i) + '.json'
        item_vector_generator = ItemVectorGenerator(batch_file)
        item_vectors.update(item_vector_generator.make_item_vectors())

    # batch for userlist 4
    for i in range(3):
        batch_file = '../data_batch/batch4_' + str(i) + '.json'
        item_vector_generator = ItemVectorGenerator(batch_file)
        item_vectors.update(item_vector_generator.make_item_vectors())

    item_vectors_file = './item_vectors_tf_idf.json'

    with open(item_vectors_file, 'w') as fp:
        json.dump(item_vectors, fp)
