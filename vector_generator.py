import json
from utils import make_idf_table
from utils import champ_id_remap
from utils import global_win_rate
from math import sqrt

PLAY_COUNT = 1
MASTERY_SCORE = 2

class UserVectorGenerator():
    def __init__(self, batch_file, mode):
        """
        mode: Determine which method to generate user vectors
            1: Naive method. Just get literal value from data
            2: TF-IDF method. Calcuate TF-IDF value for each vector value
            3: TF-IDF with global win rate mode
        """
        self.remapped_champ_id = champ_id_remap()
        self.champ_num = len(self.remapped_champ_id)
        self.global_win_rate = global_win_rate()
        self.mode = mode

        if mode == 2 or mode == 3: # TF-IDF mode or TF-IDF with global win rate mode
            self.idf_table = make_idf_table()

        with open(batch_file, 'r') as fp:
            self.batch_data = json.load(fp)

    def _get_user_vector_measure(self, user_name, champ_history, champ_idx, mode, measure):
        """
        user_name: User name
            Needed for max_play_count
        champ_history: Each champion history for user_name
            Needed for getting base value such as play count, win_rate, championPoints
        champ_idx: Remapped champion index
            Needed for accessing idf_table
        mode: Method for generating user vector measure
        measure: Determine which measure to get compute the value of user vector
            PLAY_COUNT: play count
            MASTERY_SCORE: mastery score
        """
        if measure == PLAY_COUNT: # play count
            if mode == 1: # Naive mode
                return champ_history['play_count']

            elif mode == 2: # TF-IDF mode
                max_play_count = self._get_max_play_count(user_name)
                return (champ_history['play_count'] / max_play_count) * self.idf_table[champ_idx]

            elif mode == 3: # TF-IDF with global win rate
                max_play_count = self._get_max_play_count(user_name)
                this_champ_global_win_rate = self.global_win_rate[champ_idx]
                this_user_champ_win_rate = champ_history['win_rate']

                weighted_rate = this_user_champ_win_rate / this_champ_global_win_rate
                play_count_tf_idf = (champ_history['play_count'] / max_play_count) * self.idf_table[champ_idx]

                return weighted_rate * play_count_tf_idf

        elif measure == MASTERY_SCORE: # mastery score
            if mode == 1: # Naive mode
                return champ_history['championPoints']

            elif mode == 2: # TF-IDF mode
                max_mastery_score = self._get_max_mastery_score(user_name)
                return (champ_history['championPoints'] / max_mastery_score) * self.idf_table[champ_idx]

            elif mode == 3: # TF-IDF with global win rate
                max_mastery_score = self._get_max_mastery_score(user_name)
                this_champ_global_win_rate = self.global_win_rate[champ_idx]
                this_user_champ_win_rate = champ_history['win_rate']

                weighted_rate = this_user_champ_win_rate / this_champ_global_win_rate
                mastery_tf_idf = (champ_history['championPoints'] / max_mastery_score) * self.idf_table[champ_idx]

                return weighted_rate * mastery_tf_idf

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
        #play_count_vector = [0 for _ in range(self.champ_num)]

        #for champ_history in self.batch_data[user_name]['champion_history']:
        #    play_count_vector[champ_idx] = \
        #            self._get_user_vector_measure(user_name, champ_history, \
        #            champ_idx, self.mode, PLAY_COUNT)
        play_count_vector = dict()

        user_win_rate = self.batch_data[user_name]['win_rate'];

        for champ_history in self.batch_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            exclude_champ_idx = self.remapped_champ_id[original_champ_id]

            exclude_champ_play_count = champ_history['play_count']
            exclude_champ_win_rate = champ_history['win_rate']
            play_count_vector[exclude_champ_idx] = (exclude_champ_play_count, \
                    exclude_champ_win_rate, user_win_rate, [0 for _ in range(self.champ_num)])

        for exclude_champ_idx in play_count_vector:
            for champ_history in self.batch_data[user_name]['champion_history']:
                if exclude_champ_idx == self.remapped_champ_id[champ_history['champion_key']]:
                    continue

                original_champ_id = champ_history['champion_key']
                champ_idx = self.remapped_champ_id[original_champ_id]

                play_count_vector[exclude_champ_idx][3][champ_idx] = \
                        self._get_user_vector_measure(user_name, champ_history, \
                        champ_idx, self.mode, PLAY_COUNT)

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
        
        for champ_history in self.batch_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = self.remapped_champ_id[original_champ_id]

            mastery_score_vector[champ_idx] = \
                    self._get_user_vector_measure(user_name, champ_history, \
                    champ_idx, self.mode, MASTERY_SCORE)

        return mastery_score_vector

    def make_user_vectors(self):
        user_vectors = {}

        for user_name in self.batch_data:
            play_count_vector = self._get_play_count_vector(user_name)
            #mastery_score_vector = self._get_mastery_score_vector(user_name)
            user_vectors[user_name] = play_count_vector #+ mastery_score_vector

        return user_vectors

class ItemVectorGenerator():
    def __init__(self, batch_file):
        self.remapped_champ_id = champ_id_remap()
        self.champ_num = len(self.remapped_champ_id)
        self.idf_table = make_idf_table()

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
            play_count_tf_idf = (champ_history['play_count'] / max_play_count) * self.idf_table[champ_idx]

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
            tf_idf_matrix[user_name] = self._get_play_count_tf_idf_vector(user_name)

        champ_corr_matrix = self._get_champ_corr_matrix(tf_idf_matrix)

        return champ_corr_matrix

def generate_user_vector(mode):
    user_vectors = {}


    batch_file = './data_batch/userbatch.json'
    user_vector_generator = UserVectorGenerator(batch_file, mode)
    user_vectors = user_vector_generator.make_user_vectors()

    if mode == 1:
        user_vectors_file = './datasets/user_vectors_naive.json'
    elif mode == 2:
        user_vectors_file = './datasets/user_vectors_tf_idf.json'
    elif mode == 3:
        user_vectors_file = './datasets/user_vectors_tf_idf_excluding.json'

    with open(user_vectors_file, 'w') as fp:
        json.dump(user_vectors, fp)

def generate_item_vector():
    item_vectors = {}

    batch_file = './data_batch/userbatch.json'
    item_vector_generator = ItemVectorGenerator(batch_file)
    item_vectors = item_vector_generator.make_item_vectors()

    item_vectors_file = './datasets/item_vectors_tf_idf.json'
    with open(item_vectors_file, 'w') as fp:
        json.dump(item_vectors, fp)
