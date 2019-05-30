from urllib.request import urlopen
from bs4 import BeautifulSoup
import json

user_batch = {}
user_list = []

for i in range(1, 4001):
    html = urlopen("https://www.op.gg/ranking/ladder/page=" + str(i))
    bsObject = BeautifulSoup(html, "html.parser")
    user_cell = bsObject.find_all('tr', 'ranking-table__row')
    for elem in user_cell:
        user_name = elem.find('span').text
        win_rate = int(elem.find('span', 'winratio__text').text[:-1])
        if 43 <= win_rate <= 65:
            user_list.append(user_name)

user_batch['user_name'] = user_list
user_batch['batch_size'] = len(user_list)
        
with open('./data_batch/userlist1.json', 'w') as fp:
    json.dump(user_batch, fp)