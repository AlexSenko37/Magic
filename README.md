# Magic: The Gathering Metagame Analysis

Magic: The Gathering is a board game with 20 million+ players worldwide in which players battle each other using decks of 60+ cards constructed from a pool of thousands of unique cards.

The decks used competitively in tournaments tend to revolve around dozens of deck archetypes. This notebooks studies clusters of similar decks to determine the true number of meaningful archetypes.

In this notebook:
- Representing decks with vectors indicating their compostiion
- Dimensionality reduction with UMAP so similar decks are clustered in a 2D space
- Interactive plotting of the UMAP embeddings using Bokeh

## Import Deck Database


```python
import ast, json

# import data from json database
def read_json():
    
    with open('mtg_all.json', 'r') as f:
        lines = f.readlines()

    deck_list = []
    for line in lines[1:-1]:
        deck_dict = ast.literal_eval(line[:-2])
        deck_list += [deck_dict]
    return deck_list

deck_list = read_json()
```

The deck list is a list of dictionaries, where each dictionary contains a description of a deck from a sanctioned MTG tournament, scraped from mtggoldfish.com (specifically Modern format decks played between March 13 and April 24 2020). For example:


```python
#%pprint # turn pretty printing off
deck_list[0]
```




    {'tournament': 'Modern League 2020-04-24', 'game_format': 'Modern', 'date_played': 'Apr 24, 2020', 'deck_url': '/deck/2958088', 'archetype': 'Ad Nauseam', 'deckname': 'Ad Nauseam', 'pilot': 'mashmalovsky', 'wins': '5', 'losses': '0', 'nums': [4, 4, 3, 4, 4, 4, 1, 4, 4, 4, 4, 4, 3, 4, 2, 1, 3, 2, 1, 1, 1, 1, 3, 2, 1, 1, 1, 4], 'names': ["Thassa's Oracle", 'Simian Spirit Guide', 'Pact of Negation', "Angel's Grace", 'Serum Visions', 'Spoils of the Vault', 'Lightning Storm', 'Ad Nauseam', 'Lotus Bloom', 'Pentad Prism', 'Phyrexian Unlife', 'City of Brass', 'Darkslick Shores', 'Gemstone Mine', 'Island', 'Plains', 'Seachrome Coast', 'Temple of Deceit', 'Temple of Enlightenment', 'Fatal Push', 'Path to Exile', 'Thoughtseize', 'Veil of Summer', 'Echoing Truth', 'Grand Abolisher', 'Pyroclasm', "Bontu's Last Reckoning", 'Leyline of Sanctity'], 'main_or_side': ['M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S']}



The actual contents of the deck (which cards are in it) are contained in the lists 'names' and 'nums', where 'names' contains the names of the cards in the deck and 'nums' contains the number of that card the deck contains.


```python
import pandas as pd

df_deck_example = pd.DataFrame({'names': deck_list[0]['names'], 'nums': deck_list[0]['nums']})
df_deck_example.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>names</th>
      <th>nums</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Thassa's Oracle</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Simian Spirit Guide</td>
      <td>4</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Pact of Negation</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Angel's Grace</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Serum Visions</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



## Make Vector Representation of Decks

In order to cluster decks, we need a vector representation of each deck. To do that, we'll get the set of all cards that appear in all decks, and arrange them alphabetically. Then each deck can be represented by populating a vector indicating how many of each possible card type that deck contains.


```python
from collections import defaultdict

# class to build vector representations of decks
class VectDeck:
    
    def __init__(self, deck_list):
        self.deck_list = deck_list
    
    # make ordered dictionary of all card names
    def make_card_dict(self):
        all_card_names = dict()
        self.all_archetypes = defaultdict(int)
        for deck in self.deck_list:
            self.all_archetypes[deck['archetype']] += 1
            card_names = deck['names']
            for name in card_names:
                all_card_names[name] = 0
        self.card_name_list = dict(sorted(all_card_names.items()))
        return self.card_name_list, self.all_archetypes
    
    # build vector representation for each deck
    def build_deck_vects(self):

        # for each deck
        for deck in self.deck_list:
            # create a new instance of card_name_list
            deck_card_names = dict(self.card_name_list)

            # get lists of cards names and nums
            names = deck['names']
            nums = deck['nums']

            # assign values to card name dict
            for i, name in enumerate(names):
                deck_card_names[name] = nums[i]

            # convert to a vector of card numbers
            # store as a new part of the deck dict
            deck['card_vector'] = list(deck_card_names.values())
        return self.deck_list
    
deck_vect_db = VectDeck(deck_list)
deck_vect_db.make_card_dict()
deck_vect_db.build_deck_vects();
```


```python
deck_vect_db.deck_list[0]
```




    {'tournament': 'Modern League 2020-04-24', 'game_format': 'Modern', 'date_played': 'Apr 24, 2020', 'deck_url': '/deck/2958088', 'archetype': 'Ad Nauseam', 'deckname': 'Ad Nauseam', 'pilot': 'mashmalovsky', 'wins': '5', 'losses': '0', 'nums': [4, 4, 3, 4, 4, 4, 1, 4, 4, 4, 4, 4, 3, 4, 2, 1, 3, 2, 1, 1, 1, 1, 3, 2, 1, 1, 1, 4], 'names': ["Thassa's Oracle", 'Simian Spirit Guide', 'Pact of Negation', "Angel's Grace", 'Serum Visions', 'Spoils of the Vault', 'Lightning Storm', 'Ad Nauseam', 'Lotus Bloom', 'Pentad Prism', 'Phyrexian Unlife', 'City of Brass', 'Darkslick Shores', 'Gemstone Mine', 'Island', 'Plains', 'Seachrome Coast', 'Temple of Deceit', 'Temple of Enlightenment', 'Fatal Push', 'Path to Exile', 'Thoughtseize', 'Veil of Summer', 'Echoing Truth', 'Grand Abolisher', 'Pyroclasm', "Bontu's Last Reckoning", 'Leyline of Sanctity'], 'main_or_side': ['M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'M', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'], 'card_vector': [0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}



We can see that a len 1341 (the number of unique cards in the database) vector called card_vector has been added to each dictionary describing a deck. Each of the entries in the vector maps to the name of a card.

## Reduce Deck Vector Dimensions Using UMAP and Plot Using Bokeh

We can map the 1341-dimensional space that describes the decks into a 2D space that can be plotted and show the relative similarity of different decks.


```python
import umap
import numpy as np
from bokeh.plotting import figure, show, output_notebook
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper, OpenURL, TapTool
from bokeh.palettes import Turbo256

# plot vector representation of decks
class UmapDeck:
    
    def __init__(self, deck_list):
        self.deck_list = deck_list
    
    def get_umap_embedding(self):
        # compile vector representations into one numpy array
        M = []
        for deck in deck_list:
            M += [deck['card_vector']]
        X = np.array(M)
        
        # run umap to create embedding
        reducer = umap.UMAP()
        self.embedding = reducer.fit_transform(X)
        return self.embedding

    # generate labels for embeddings created by umap
    def make_deck_labels(self):
        # generate list of archetypes labels for each deck
        deck_labels = []
        deck_urls = []
        for deck in deck_list:
            deck_labels += [deck['archetype']]
            deck_urls += [deck['deck_url']]

        self.deck_df = pd.DataFrame(self.embedding, columns=('x', 'y'))
        self.deck_df['archetype'] = deck_labels
        self.deck_df['deck_url'] = deck_urls
        return self.deck_df

    
    def interactive_umap(self):
        datasource = ColumnDataSource(self.deck_df)

        color_mapping = CategoricalColorMapper(factors=list(set(self.deck_df['archetype'])), palette=Turbo256)

        output_notebook()
        
        plot_figure = figure(
            title='UMAP projection of the Magic dataset',
            plot_width=600,
            plot_height=600,
            tools=('pan, wheel_zoom, reset','tap')
        )

        plot_figure.add_tools(HoverTool(tooltips=[
            ("archeytpe", "@archetype"),
        ]))

        plot_figure.circle(
            'x',
            'y',
            source=datasource,
            color=dict(field='archetype', transform=color_mapping),
            line_alpha=0.6,
            fill_alpha=0.6,
            size=4
        )

        url = "http://www.mtggoldfish.com/@deck_url/"
        taptool = plot_figure.select(type=TapTool)
        taptool.callback = OpenURL(url=url)

        show(plot_figure)

        return

deck_umap = UmapDeck(deck_list)
deck_umap.get_umap_embedding();
deck_umap.make_deck_labels();
deck_umap.interactive_umap()
```



<div class="bk-root">
    <a href="https://bokeh.org" target="_blank" class="bk-logo bk-logo-small bk-logo-notebook"></a>
    <span id="1442">Loading BokehJS ...</span>
</div>











<div class="bk-root" id="3bf3be01-c726-4c2a-bef5-59e90c1fdffc" data-root-id="1443"></div>






```python

```


```python

```


```python

```
