from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup
from Models.DataCollector import DataCollector
from Models.UserInspector import UserInspector
from champion_graph import ChampionGraph
import torch.nn.functional as F
import json
import operator

import torch
from Models.Models import AutoEncoder, Predictor
from utils import champ_id_remap, global_win_rate, get_original_champ_id

with open('./metadata/name_to_key.json', 'r') as fp:
    name_to_key = json.load(fp)
    
    
class ChampionRecommender():
    def __init__(self):
        self.user_inspector = UserInspector()

        self.user_encoder = AutoEncoder(143, 12)
        self.user_encoder.load_state_dict(torch.load('./trained_model/user_encoder_augmented.pth'))

        self.item_encoder = AutoEncoder(143, 8)
        self.item_encoder.load_state_dict(torch.load('./trained_model/item_encoder2.pth'))

        self.predictor = Predictor(user_len=12, item_len=8, hidden_unit=10).eval()
        self.predictor.load_state_dict(torch.load('./trained_model/predictor_last_m.pth'))
        
        self.remapped_champ_id = champ_id_remap()
        self.global_win_rate = global_win_rate() 
        
        with open('./datasets/item_vectors_tf_idf.json', 'r') as fp:
            self.item_vectors = json.load(fp)        
        
        with open('./metadata/user_idf_table.json', 'r') as fp:
            self.idf_table = json.load(fp)

    def recommender(self, userName):
        #try:
        user_data = self.user_inspector.user_history_collector(userName)
        win_rate_dict, played_champion_key = self.winrate_predictior(user_data)
        champ_sim_dict = self.champion_mapper(userName)
        
        recommendation = dict()
        
        for key in champ_sim_dict.keys():
            recommendation[key] = 0.001*win_rate_dict[key] + champ_sim_dict[key]
            

        return recommendation, played_champion_key
        #except:
        #    print("not a valid user. please check.")
        
    def champion_mapper(self, userName):
        champion_graph = ChampionGraph(userName)
        champion_distance = champion_graph.get_champion_distance()
        champ_sim_dict = dict()
        sorted_result = sorted(champion_distance.items(), key=operator.itemgetter(1), reverse=False)
        for item in sorted_result:
            champ_sim_dict[item[0]] = round(1/item[1], 4)
        return champ_sim_dict
    

    def winrate_predictior(self, user_data):
        user_winrate = self._tensor_item(user_data['win_rate'])
        user_vec = self._user_vector_generator(user_data)
        played_champions = [i for i, e in enumerate(user_vec) if e != 0]
        
        played_champion_key = [get_original_champ_id(self.remapped_champ_id, int(i)) for i in played_champions]
        
        user_vec = torch.Tensor(user_vec)
        user_vec = self.user_encoder.encoder(user_vec)
        
        win_rate_dict = dict()
        
        for key, item in self.item_vectors.items():
            if int(key) not in played_champions:
                global_win = self._tensor_item(self.global_win_rate[int(key)])
                item_vec = torch.Tensor([item])
                item_vec = self.item_encoder.encoder(item_vec)
                #item_vec = torch.Tensor([0,0,0,0,0,0,0,0])
                #user_vec = torch.Tensor([0,0,0,0,0,0,0,0,0,0,0,0])
                item_vec = item_vec.squeeze()
                
                user_vec = F.normalize(user_vec, dim=0)
                item_vec = F.normalize(item_vec, dim=0)
                
                prediction = self.predictor(user_vec, item_vec, user_winrate, global_win)
                win_rate_dict[key] = prediction.item() - global_win.item()
        
        win_rate_dict = self._dict_origin_mapper(win_rate_dict)
        sorted_result = sorted(win_rate_dict.items(), key=operator.itemgetter(1), reverse=True)
        win_rate_dict = dict()
        
        for item in sorted_result:
            win_rate_dict[item[0]] = item[1]
            
        return win_rate_dict, played_champion_key
    
    
    def system_tester(self, userName):
        allchamp = self.user_inspector.user_allchamp_collector(userName)
        recommendation, played_keys = self.recommender(userName)
        
        type1_1 = []
        type1_2 = []
        all_win = []
        
        for i, (key, item) in enumerate(recommendation.items()):
            if key in allchamp.keys():
                type1_1.append(i)
                type1_2.append(allchamp[key][1])
                all_win.append(allchamp[key][1])
        
        reco = []
        type2 = []
        for i in range(5):
            key = list(recommendation.keys())[i]
            if key in allchamp.keys():
                reco.append(allchamp[key][1])
                
        if len(reco) != 0 and len(all_win) != 0:
            type2.append(sum(reco)/len(reco) - sum(all_win)/len(all_win))
        
        return [type1_1, type1_2], type2
        
    
    def _dict_origin_mapper(self, recommend_dict):
        original_recommend_dict = dict()
        for remapped_id, score in recommend_dict.items():
            original_id = get_original_champ_id(self.remapped_champ_id, int(remapped_id))
            original_name = self.user_inspector.key_to_id[str(original_id)]
            original_recommend_dict[original_name] = recommend_dict[remapped_id]
        return original_recommend_dict

            
    def _user_vector_generator(self, user_data):
        user_win_rate = user_data['win_rate']
        play_count_vector = [0 for x in range(143)]

        for champ_history in user_data['champion_history']:
            original_champ_id = champ_history['champion_key']
            champ_idx = self.remapped_champ_id[original_champ_id]

            max_play_count = self._get_max_play_count(user_data)
            measured_score = (champ_history['play_count'] / max_play_count) * self.idf_table[str(champ_idx)]
            play_count_vector[champ_idx] = measured_score
        
        return play_count_vector

    
    def _get_max_play_count(self, user_data):
        """
        Get count of maximally played champion for user_name
        """
        max_play_count = 0

        for champ_history in user_data['champion_history']:
            champ_play_count = champ_history['play_count']
            if max_play_count < champ_play_count:
                max_play_count = champ_play_count

        return max_play_count

    
    def _tensor_item(self, item):
        return torch.Tensor([item])