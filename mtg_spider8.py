import scrapy
import ast

class QuotesSpider(scrapy.Spider):
	name = "mtg8"

	# start_urls = [
	# 	'https://www.mtggoldfish.com/deck/2911709',
	# ]

	def start_requests(self):

		# import json of tournament urls
		with open('mtg_decklist.json', 'r') as f:
			lines = f.readlines()

		deck_list = []
		for line in lines[1:-1]:
			deck_dict = ast.literal_eval(line[:-2])
			deck_list += deck_dict['deck_urls']
		# tournament_url_dict = ast.literal_eval(lines[1])
		# tournament_urls = tournament_url_dict['tournament_urls']
        # urls = [
        #     'http://quotes.toscrape.com/page/1/',
        #     'http://quotes.toscrape.com/page/2/',
        # ]
		for deck in deck_list:
			one_url = 'https://mtggoldfish.com' + deck
			yield scrapy.Request(url=one_url, callback=self.parse, meta= {'deck_url': deck})

	def parse(self, response):
		deckname = response.xpath("//h1[@class='deck-view-title']/text()").extract()[0]
		deckname = deckname.strip('\n')
		pilot = response.xpath("//span[@class='deck-view-author']/text()").extract()[0]
		pilot = pilot[3:]
		wins_loss = response.xpath("//div[@class='deck-view-description']/text()").extract()[1]
		wins = wins_loss[3]
		losses = wins_loss[5]
		game_format = response.xpath("//div[@class='deck-view-description']/text()").extract()[2]
		game_format = game_format.strip('\n')
		game_format = game_format[8:]
		date_played = response.xpath("//div[@class='deck-view-description']/text()").extract()[3]
		date_played = date_played.strip('\n')
		tournament = response.xpath("//div[@class='deck-view-description']/a/text()").extract()[0]
		archetype = response.xpath("//div[@class='deck-view-description']/a/text()").extract()[1]

		names = response.selector.xpath("//table[@class='deck-view-deck-table']/tr/td/a/text()").extract()
		nums = response.selector.xpath("//table[@class='deck-view-deck-table']//tr/td[@class='deck-col-qty']/text()").extract()
		nums = [num.strip('\n') for num in nums]

		nums_keep = []
		for num in nums:
		    num = int(num)
		    nums_keep.append(num)
		    if sum(nums_keep) >= 75:
		        break
		nums = nums_keep
		names = names[:len(nums)]

		main_or_side = []
		run_sum = 0
		for num in nums:
			if run_sum < 60:
				main_or_side += ['M']
			else:
				main_or_side += ['S']
			run_sum += num

		yield {
			'tournament': tournament,
			'game_format': game_format,
			'date_played': date_played,
			'deck_url': response.meta['deck_url'],
			'archetype': archetype,
			'deckname': deckname,
			'pilot': pilot,
			'wins': wins,
			'losses': losses,
			'nums': nums,
			'names': names,
			'main_or_side': main_or_side,
		}