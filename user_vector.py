import json
import sys

class UserVectorGenerator():
    def __init__(self, batch_file):
        self.remapped_champ_id = self._champ_id_remap()
        self.champ_num = len(self.remapped_champ_id)

        with open(batch_file, 'r') as fp:
            self.batch_data = json.load(fp)

    def _champ_id_remap(self):
        original_champ_id = {}
        remapped_champ_id = {}

        with open('./id_to_key.json') as fp:
            original_champ_id = json.load(fp)

        for i, champ_name in enumerate(original_champ_id):
            remapped_champ_id[original_champ_id[champ_name]] = i
        
        return remapped_champ_id

    def _get_play_count_vector(self, user_name):
        play_count_vector = [0 for _ in range(self.champ_num)]

        for champ_history in self.batch_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = self.remapped_champ_id[original_champ_id]

            play_count_vector[champ_idx] = champ_history['play_count']

        return play_count_vector

    def _get_mastery_score_vector(self, user_name):
        mastery_score_vector = [0 for _ in range(self.champ_num)]
        
        for champ_history in self.batch_data[user_name]['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = self.remapped_champ_id[original_champ_id]

            mastery_score_vector[champ_idx] = champ_history['championPoints']

        return mastery_score_vector

    def make_user_vectors_json(self):
        user_vectors = {}

        for user_name in self.batch_data:
            play_count_vector = self._get_play_count_vector(user_name)
            mastery_score_vector = self._get_mastery_score_vector(user_name)
            user_vectors[user_name] = play_count_vector + mastery_score_vector

        with open('./data_batch/user_vectors.json', 'w') as fp:
            json.dump(user_vectors, fp)

user_vector_generator = UserVectorGenerator('./data_batch/batch2_0.json')
user_vector_generator.make_user_vectors_json()
