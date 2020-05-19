#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 20:35:49 2020

@author: alex
"""

import ast
import json
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats
import pandas as pd



def read_json():
    
    with open('mtg_all.json', 'r') as f:
        lines = f.readlines()

    deck_list = []
    for line in lines[1:-1]:
        deck_dict = ast.literal_eval(line[:-2])
        deck_list += [deck_dict]
    return deck_list

deck_list = read_json()

# just get the 'humans' archetype
def get_archetype(archetype):
    archetype_decks = []
    for deck in deck_list:
        if deck['archetype'] == archetype:
            archetype_decks += [deck]
    return archetype_decks

archetype_decks = get_archetype('Bant Snowblade')

# build two new features: cardnum + name + main_or_side, and win rate
def add_features(archetype_decks):
    for deck in archetype_decks:
        deck['win%'] = int(deck['wins']) / (int(deck['wins']) + int(deck['losses']))
        names = deck['names']
        nums = deck['nums']
        main_or_side = deck['main_or_side']
        num_name_side = []
        for i,_ in enumerate(names):
            combined = str(nums[i]) + ' ' + names[i] + ' ' + main_or_side[i]
            num_name_side += [combined]
        deck['num_name_side'] = num_name_side
    return archetype_decks

archetype_decks = add_features(archetype_decks)
    
def winPer_by_card(archetype_decks):
    win_list = {}
    for deck in archetype_decks:
        cards = deck['num_name_side']
        for card in cards:
            if card in win_list:
                win_list[card]['wins'] += int(deck['wins'])
                win_list[card]['losses'] += int(deck['losses'])
            else:
                win_list[card] = {}
                win_list[card]['wins'] = int(deck['wins'])
                win_list[card]['losses'] = int(deck['losses'])
    card_records = {}
    for card in win_list:
        winPer = win_list[card]['wins'] / (win_list[card]['wins'] + win_list[card]['losses'])
        card_records[card] = winPer
    return card_records
                
card_record = winPer_by_card(archetype_decks)

# generate ordered reference list:
# this list now has the cards in alphabetical order
ordered_card_list = list(card_record)
ordered_card_list.sort()

# add total appearances of each card
num_unique = len(ordered_card_list)
frequency = np.zeros(num_unique)
for deck in archetype_decks:
    for card_x in deck['num_name_side']:
        frequency[ordered_card_list.index(card_x)] += 1

# build ordered win% vector
win_vect = []
for card in ordered_card_list:
    win_vect += [card_record[card]]
win_vect.reverse()
win_vect = np.array(win_vect)

# build a vector representation of the deck contents
def add_vect(archetype_decks, ordered_card_list):
    for deck in archetype_decks:
        deck_vect = np.zeros(len(ordered_card_list))
        for card in deck['num_name_side']:
            deck_vect[ordered_card_list.index(card)] += 1
        deck['deck_vect'] = deck_vect
    return archetype_decks

archetype_decks = add_vect(archetype_decks, ordered_card_list)

# build matrix where rows are vector representation of decks
def linFeatures(archetype_decks):
    trainX = []
    trainY = []
    for deck in archetype_decks:
        x1 = list(deck['deck_vect'])
        #print(x1)
        #print(trainX)
        y1 = deck['win%']
        trainX = trainX + [x1]
        trainY = trainY + [y1]
    return trainX, trainY

trainX, trainY = linFeatures(archetype_decks)

# do linear regression with scikit-learn
reg = LinearRegression().fit(trainX, trainY)

# make dict of cards and weights
lin_scores = dict(zip(ordered_card_list, reg.coef_ / 10 ** 10))

freq = stats.zscore(frequency)
weight = stats.zscore(reg.coef_ / 10 ** 10)
freq_plus_weight = freq + weight
freq_plus_weight_dict = dict(zip(ordered_card_list, freq_plus_weight))

#with open('humans_frequency_plus_weight.json', 'w') as fp:
#    json.dump(freq_plus_weight_dict, fp)

# export as csv
Mexport = [list(freq_plus_weight_dict.keys()), list(freq_plus_weight_dict.values())]
df_export = pd.DataFrame(list(map(list, zip(*Mexport))))
Mex2 = np.empty((len(ordered_card_list),4), dtype='object')
for index, row in df_export.iterrows():
    c_name = row[0]
    c_num = c_name[0]
    c_ms = c_name[-1]
    c_name = c_name[2:-1]
    Mex2[index][0] = c_num
    Mex2[index][1] = c_name
    Mex2[index][2] = c_ms
    Mex2[index][3] = row[1]
df_Mex2 = pd.DataFrame(Mex2)
df_Mex2 = df_Mex2.sort_values(by=[2,3], ascending = [True, False])
df_Mex2.to_csv('card_rank_export.csv', index=False)

## build dictionary with names and scores
#score_dict2 = dict(zip(ordered_card_list, scores))


