from urllib.request import urlopen
from urllib import parse
from bs4 import BeautifulSoup
from Models.DataCollector import DataCollector
import torch.nn.functional as F
import json
import operator

with open('./metadata/name_to_key.json', 'r') as fp:
    name_to_key = json.load(fp)

    
class UserInspector(DataCollector):
    def __init__(self):
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

    def user_history_collector(self, userName):
        # url encoding (for Korean words)
        userName = parse.quote(userName)

        # open url and create bs4 Object
        html = urlopen("https://www.op.gg/summoner/userName="+userName)
        bsObject = BeautifulSoup(html, "html.parser")

        # decode userName from url encoding
        userName = parse.unquote(userName)

        # win/loss and play count
        wins = int(bsObject.find('span', 'wins').text[:-1])
        losses = int(bsObject.find('span', 'losses').text[:-1])
        total_play = wins + losses    
        win_rate = round(wins/total_play, 3)

        champ_list = bsObject.find_all("div", {'class' : 'ChampionBox Ranked'})
        champion_history = self.champ_history_setter(champ_list)            

        # this is (adapted) user_history DTO
        user_historyDTO = {
            'user_name' : userName,
            'total_play' : total_play,
            'win_rate' : win_rate,
            'champion_history' : champion_history,
        }
        return user_historyDTO
    
    def user_allchamp_collector(self, userName):
        # url encoding (for Korean words)
        userName = parse.quote(userName)

        # open url and create bs4 Object
        html = urlopen("https://www.op.gg/summoner/champions/userName="+userName)
        bsObject = BeautifulSoup(html, "html.parser")

        # decode userName from url encoding
        userName = parse.unquote(userName)

        champ_list = bsObject.find_all("tr", {'class' : 'Row'})

        champion_history_dict = dict()

        for champion in champ_list:
            champion_name = champion.find('td', 'ChampionName Cell')

            win, lose = 0, 0        
            if champion_name is not None:
                champion_name = champion_name.find('a').text
                champion_win = champion.find('div', 'Text Left')
                champion_lose = champion.find('div', 'Text Right')
                if champion_win is not None:
                    win = int(champion_win.text[:-1])
                if champion_lose is not None:
                    lose = int(champion_lose.text[:-1])

                playcount = win + lose
                winrate = round(win/playcount, 3)
                champion_id = self.name_to_id[champion_name]
                if playcount >= 5:
                    champion_history_dict[champion_id] = [playcount, winrate]

        return champion_history_dict
    