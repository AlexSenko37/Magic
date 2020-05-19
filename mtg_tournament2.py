import scrapy
import ast

class TournamentSpider(scrapy.Spider):
	name = "mtg_tournament2"

	# start_urls = [
	# 	#'https://www.mtggoldfish.com/tournament/modern-super-qualifier-12124658#paper',
	# 	'https://www.mtggoldfish.com/tournament/30856',
	# ]

	def start_requests(self):

		# import json of tournament urls
		with open('mtg_tournament_urls.json', 'r') as f:
			lines = f.readlines()
		tournament_url_dict = ast.literal_eval(lines[1])
		tournament_urls = tournament_url_dict['tournament_urls']
        # urls = [
        #     'http://quotes.toscrape.com/page/1/',
        #     'http://quotes.toscrape.com/page/2/',
        # ]
		for url in tournament_urls:
			one_url = 'https://mtggoldfish.com' + url
			yield scrapy.Request(url=one_url, callback=self.parse)

	def parse(self, response):
		deck_urls = response.xpath("//table/tr/td/a[starts-with(@href, '/deck/')]/@href").extract()

		yield {
			'deck_urls': deck_urls,
		}

