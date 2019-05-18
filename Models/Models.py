import torch
import torch.nn as nn
import torch.nn.functional as F



class AutoEncoder(nn.Module):
    """
    A simple AutoEncoder. Manually add activation at the last part of decoder if needed.
    """
    
    def __init__(self, input_len, hidden_unit, activation=False):
        super(AutoEncoder, self).__init__()
        self.intermediate = int((input_len+hidden_unit)/2)
        self.encoder = nn.Sequential(
            nn.Linear(input_len, self.intermediate),
            nn.LeakyReLU(inplace=True),
            nn.Linear(self.intermediate, hidden_unit))

        self.decoder = nn.Sequential(
            nn.Linear(hidden_unit, self.intermediate),
            nn.LeakyReLU(inplace=True),
            nn.Linear(self.intermediate, input_len))
        if activation:
            self.decoder.add_module('act', activation)
    
    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x
    
    
class Predictor(nn.Module):
    """
    A prediction model for winning rate. Given user and item vector, predicts winning rate with a scalar value.
    """
    
    def __init__(self, user_len, item_len, hidden_unit):
        super(Predictor, self).__init__()
        self.layer1 = nn.Linear(user_len+item_len, hidden_unit)
        self.relu = nn.ReLU(inplace=True)
        self.layer2 = nn.Linear(hidden_unit, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, user, item):
        x = torch.cat((user, item), dim=1)
        x = self.layer1(x)
        x = self.relu(x)
        x = self.layer2(x)
        x = self.sigmoid(x)
        return x
    