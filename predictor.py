import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import MultiStepLR
from torch.utils.data import DataLoader, Dataset, Subset
from utils import champ_id_remap, global_win_rate
import json
import math

from Models.Models import AutoEncoder, Predictor

global_win_rate = global_win_rate()


class WinRateDataset(Dataset):
    """
    data : user_vector, item_vector
    label : win_rate
    """
    def __init__(self, user_path, item_path, label_path, global_win_rate):
        self.user_encoder = AutoEncoder(143, 12)
        self.user_encoder.load_state_dict(torch.load('./trained_model/user_encoder_augmented.pth'))
        self.item_encoder = AutoEncoder(143, 10)
        self.item_encoder.load_state_dict(torch.load('./trained_model/item_encoder.pth'))
        self.champ_id_remap = champ_id_remap()
        
        # get user_vector
        with open(user_path, 'r') as up:
            self.user = json.load(up)
        
        # get item_vector
        with open(item_path, 'r') as ip:
            self.item = json.load(ip)
        
        # get label
        with open(label_path, 'r') as lp:
            self.label = json.load(lp)
            
        # build dataset
        self.data = []
        with torch.no_grad():
            for i, (user, user_set) in enumerate(self.user.items()):
                for excluded_champ, augdataDTO in user_set.items():                        
                    play_count = augdataDTO[0]

                    if play_count >= 10:
                        win_rate_label = augdataDTO[1]
                        user_winrate = augdataDTO[2]
                        user_vec = augdataDTO[3]
                        item_vec = self.item[str(excluded_champ)]
                        global_win = global_win_rate[int(excluded_champ)]


                        user_winrate = torch.Tensor([user_winrate])
                        user_vec = torch.Tensor(user_vec)
                        item_vec = torch.Tensor(item_vec)
                        global_win = torch.Tensor([global_win])


                        user_vec = self.user_encoder.encoder(user_vec)
                        item_vec = self.item_encoder.encoder(item_vec)

                        self.data.append(((user_vec, item_vec, user_winrate), global_win, win_rate_label))  
                                
                                
    def __getitem__(self, index):
        user_vec = self.data[index][0][0]
        item_vec = self.data[index][0][1]
        user_winrate = self.data[index][0][2]
        global_win = self.data[index][1]
        label = self.data[index][2]
        return (user_vec, item_vec, user_winrate), global_win, label
                                     
    def __len__(self):
        length = len(self.data)
        return length

    
    
    
user_path = './datasets/user_vectors_tf_idf_excluding.json'
item_path = './datasets/item_vectors_tf_idf.json'
label_path = './data_batch/userbatch.json'

dataset = WinRateDataset(user_path, item_path, label_path, global_win_rate)

total_data = len(dataset)

train_list = [x for x in range(len(dataset))]
valid_list = train_list[-2500:]

train_list = list(set(train_list)-set(valid_list))

train_set = Subset(dataset, train_list)
valid_set = Subset(dataset, valid_list)


num_epochs = 100
batch_size = 32
device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
learning_rate = 0.001

train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=15)
valid_loader = torch.utils.data.DataLoader(valid_set, batch_size=batch_size, num_workers=4)

model = Predictor(user_len=12, item_len=10, hidden_unit=22).to(device)
criterion = nn.SmoothL1Loss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-5)
scheduler = MultiStepLR(optimizer, [20, 40, 60, 80], gamma=0.5)

loss = []
best_model_wts = None
best_loss = 100

for epoch in range(num_epochs):
    train_loss = 0.0
    count = 0
    for (user_vec, item_vec, user_winrate), global_win, label in train_loader:
        scheduler.step()
        user_vec = user_vec.to(device)
        item_vec = item_vec.to(device)
        global_win = global_win.to(device)
        user_winrate = user_winrate.to(device)
        label = label.float().to(device)
        # ===================forward=====================
        output = model(user_vec, item_vec, user_winrate, global_win)
        loss = criterion(output, label)
        # ===================backward====================
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        count += label.size(0)
        #print(loss.item()/user_vec.size(0))
    # ===================log========================
    print('train epoch [{}/{}], loss:{:.8f}'
          .format(epoch + 1, num_epochs, train_loss/count))

    valid_loss = 0.0
    count = 0
    
    if (epoch+1) % 4 == 0 and epoch > 1:
        print('---------------------------')
        for (user_vec, item_vec, user_winrate), global_win, label in valid_loader:
            scheduler.step()
            user_vec = user_vec.to(device)
            item_vec = item_vec.to(device)
            global_win = global_win.to(device)
            user_winrate = user_winrate.to(device)
            label = label.float().to(device)
            # ===================forward=====================
            output = model(user_vec, item_vec, user_winrate, global_win)
            loss = criterion(output, label)
            # ===================backward====================
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            valid_loss += loss.item()
            count += label.size(0)
            if valid_loss < best_loss:
                print('best model so far!')
                best_loss = valid_loss
                best_model_wts = model.state_dict()
        # ===================log========================
        print('valid epoch, loss:{:.8f}'
              .format(valid_loss/count))
        print('----------------------------')
        
        
        
