from riotwatcher import RiotWatcher, ApiError
from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup

import operator
import json

from time import time

class DataCollector():
    def __init__(self,  api_key=None, batch_size=10000, path='./', my_region='kr'):
        self.path = path
        self.watcher = RiotWatcher(api_key)
        self.my_region = my_region
        self.target_user = []
        self.data = {}
        self.batch_size = batch_size
        self.batch_index = 0
        self.userlist_index = 0
        
        self.name_to_key = {}
        self.name_to_id = {}
        self.id_to_key = {}
        self.key_to_id = {}
        
         
        with open('./metadata/name_to_key.json', 'r') as fp:
            self.name_to_key = json.load(fp)
        
        with open('./metadata/name_to_id.json', 'r') as fp:
            self.name_to_id = json.load(fp)

        with open('./metadata/id_to_key.json', 'r') as fp:
            self.id_to_key = json.load(fp)
        
        with open('./metadata/key_to_id.json', 'r') as fp:
            self.key_to_id = json.load(fp)

            
    def user_selector(self, path, idx):
        """
        retrieve a list of target user data
        """
        # get collected user_name lists
        with open(path+'/userlist{}.json'.format(idx), 'r') as fp:
            user_list = json.load(fp)['user_name']
            
        self.userlist_index = idx

        return user_list


    def user_data_setter(self, userName):
        """
        complete data row for a userName
        """
        user_history = self.user_history_collector(userName)
        mastery = self.mastery_scanner(userName)
        
        user_data_row =  self.history_mastery_joiner(user_history, mastery)
        
        return user_data_row
    
    
    def user_history_collector(self, userName):

        """
        Create a datarow for given userName
        return : user_historyDTO
        """

        # url encoding (for Korean words)
        userName = parse.quote(userName)

        # open url and create bs4 Object
        html = urlopen("https://www.op.gg/summoner/userName="+userName)
        bsObject = BeautifulSoup(html, "html.parser")

        # decode userName from url encoding
        userName = parse.unquote(userName)

        # ranking and tier
        ranking = float(bsObject.find('div', 'LadderRank').text.strip().split()[-3][1:-1])
        tier_rank = bsObject.find('div', 'TierRank').text

        # win/loss and play count
        wins = int(bsObject.find('span', 'wins').text[:-1])
        losses = int(bsObject.find('span', 'losses').text[:-1])
        total_play = wins + losses    
        win_rate = round(wins/total_play, 3)

        # set champion history as list
        champ_list = bsObject.find_all("div", {'class' : 'ChampionBox Ranked'})    
        champion_history = self.champ_history_setter(champ_list)

        # this is user_history DTO
        user_historyDTO = {
            'user_name' : userName,
            'ranking' : ranking,
            'tier_rank' : tier_rank,
            'total_play' : total_play,
            'win_rate' : win_rate,
            'champion_history' : champion_history,
        }

        return user_historyDTO
                
        
    def text_processor(self, play_count, win_rate):
        play_count = int(play_count.split()[0])
        win_rate = int(win_rate[:-1])

        return play_count, win_rate


    def champ_history_setter(self, champ_list):

        """
        reads data of top7 played champions.
        sets data as a list of champion_DTO.
        """

        champion_history = []

        for champion in champ_list:
            champion_name = champion.find('div', 'ChampionName')['title']
            play_count = champion.find('div', 'Title').text.strip()
            win_rate = champion.find('div', {'title' : 'Win Ratio'}).text.strip()

            play_count, win_rate = self.text_processor(play_count, win_rate)

            championDTO = {
                'champion_key' : self.name_to_key[champion_name], 
                'champion_id' : self.name_to_id[champion_name],
                'play_count' : play_count,
                'win_rate' : round(win_rate*0.01, 3)}

            champion_history.append(championDTO)

        return champion_history

    
    def champ_mastery_setter(self, champion_masteryDTO):
        """
        get masteryDTO and return top10 mastery above thershold
        return : {championID : championPoints}
        """        
        
        top10_masteryDTO = {}
        
        # sort by champion mastery point
        sorted_mastery = sorted(champion_masteryDTO.items(), key=operator.itemgetter(1), reverse=True)
        
        # if in top10 and point is higher than 10,000
        for i, elem in enumerate(sorted_mastery):
            if (i < 10) and (elem[1] > 10000):
                top10_masteryDTO[int(elem[0])] = int(elem[1])
                
        return top10_masteryDTO
                
    
    def mastery_scanner(self, userName):
        """
        get champion_mastery data and truncate
        return : {championID : championPoints}
        """
        champion_masteryDTO = {}
        
        summoner_id = self.watcher.summoner.by_name(self.my_region, userName)['id']
        champion_mastery = self.watcher.champion_mastery.by_summoner(self.my_region, summoner_id)
        
        for champion in champion_mastery:
            key = champion['championId']
            item = champion['championPoints']
            champion_masteryDTO[key] = item
    
        return champion_masteryDTO

 
    def history_mastery_joiner(self, user_historyDTO, champion_masteryDTO):
        """
        joins user_history dict and champion_mastery dict together
        return: collected_dataDTO
        """
        
        collected_dataDTO = user_historyDTO
        
        # join user_historyDTO with champion_masteryDTO
        for i, champion in enumerate(user_historyDTO['champion_history']):
            champion_id = champion['champion_id']
            champion_key = self.id_to_key[champion_id]
            
            collected_dataDTO['champion_history'][i]['championPoints'] = champion_masteryDTO[champion_key]
        
        # add top10 champion mastery to collected_dataDTO
        top10_masteryDTO = self.champ_mastery_setter(champion_masteryDTO)
        collected_dataDTO['top10_champion_mastery'] = top10_masteryDTO
        
        return collected_dataDTO
    
    
    def save_data(self, target_users):
        """
        allocate self.batch_size users data in a single .json file.
        if file exists, then raise file index.

        target_users: list of user name
        """
        
        start = time()
        for i, user in enumerate(target_users):
            if not self.is_valid_user(user):
                continue
            
            user_data = self.user_data_setter(user)
            
            if self.is_valid_data(user_data):
                self.data[user] = user_data 
            else:
                print('Not valid user data, user: {}'.format(user))
                continue
            
            if len(self.data.keys()) % 10 == 0:
                print('{} users data collected'.format(len(self.data.keys())))
                print('elapsed time for 10 users: {}'.format(time() - start))
                start = time()

            if len(self.data.keys()) > 0 and (len(self.data.keys()) % self.batch_size == 0):
                with open('./data_batch/batch{}_{}.json'.format(self.userlist_index, self.batch_index), 'w') as fp:
                    json.dump(self.data, fp)
                
                print('----------------------------')
                print('Batch {} saved'.format(self.batch_index))
                print('----------------------------')
                print()
                self.batch_index += 1
                self.clean()
        
        else:
            # if data exists yet, save as last batch
            if len(self.data.keys()) > 0:
                with open('./data_batch/batch{}.json'.format(self.batch_index) , 'w') as fp:
                    json.dump(self.data, fp)
                    print("last batch saved")
                    print()
                self.clean()
            print("finished! {} batches saved in total".format(self.batch_index+1))

            
    def is_valid_user(self, userName):
        """
        check wheter the user is valid or not
        """
        validity = False
        
        # error handling for 404 error
        try:
            # if user has valid tier and rank
            user_id = self.watcher.summoner.by_name(self.my_region, userName)['id']
            if self.watcher.league.by_summoner('kr', user_id):
                validity = True
                
        except:
            pass
        
        return validity
            
    def is_valid_data(self, collected_dataDTO):
        """
        check whether the data is valid or not
        """
        validity = False
        
        # if the user played enough
        if collected_dataDTO['total_play'] >= 25:
            validity = True
        
        # if the user's win rate is in reasonable range
        #if 0.47 <= collected_dataDTO['win_rate'] <= 0.6:
            #validity = True
            
        return validity
            
            
    def clean(self):
        """
        reset data
        """
        self.data = {}
        #print("DataCollector batch cleaning")
        #print()
        
