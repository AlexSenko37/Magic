# sum all wins and losses for each archetype
deck_stats = {}
# for each deck in deck_list
for deck in deck_list:
    # get the name of the deck
    deck_name = deck['deckname']
    # check if there is already a dictionary entry for that deck name
    if deck_name in deck_stats:
        # add wins and losses to running total
        if deck['pilot'] not in deck_stats[deck_name]['pilots']:
            deck_stats[deck_name]['pilots'].append(deck['pilot'])
        deck_stats[deck_name]['wins'] += int(deck['wins'])
        deck_stats[deck_name]['losses'] += int(deck['losses'])
    # if not, create one
    else:
        deck_stats[deck_name] = {'wins': int(deck['wins']), 
                  'losses': int(deck['losses']),
                  'pilots': [deck['pilot']]}

wins_ranked = []
# calculate win percentage and rank decks
for name in deck_stats:
    row = [name, int(deck_stats[name]['wins']), int(deck_stats[name]['losses'])]
    row.append(row[1] / (row[1] + row[2]))
    wins_ranked.append(row)
    row.append(len(deck_stats[name]['pilots']))
