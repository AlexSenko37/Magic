import scrapy

class TournamentSpider(scrapy.Spider):
	name = "mtg_tournament_search"

	start_urls = [
		#'https://www.mtggoldfish.com/tournament_searches/create?utf8=%E2%9C%93&tournament_search%5Bname%5D=&tournament_search%5Bformat%5D=modern&tournament_search%5Bdate_range%5D=03%2F10%2F2020+-+04%2F24%2F2020&commit=Search',
		'https://www.mtggoldfish.com/tournament_searches/create?utf8=%E2%9C%93&tournament_search%5Bname%5D=&tournament_search%5Bformat%5D=modern&tournament_search%5Bdate_range%5D=03%2F13%2F2020+-+04%2F26%2F2020&commit=Search',
	]

	def parse(self, response):
		#tournament_urls = response.xpath("//table/tr/td/a/@href").extract()

		# if pass_urls:
		# 	pass_urls = {
		# 		'tournament_urls': response.xpath("//table/tr/td/a/@href").getall(),
		# 	}
		try:
			#old_tournaments = response.meta['tournament_urls']
			#pass_urls = response.xpath("//table/tr/td/a/@href").getall().append(old_tournaments['tournament_urls'])
			pass_urls = {
				'tournament_urls': response.meta['tournament_urls'] + response.xpath("//table/tr/td/a/@href").getall()
			}
		except:
			pass_urls = {
				'tournament_urls': response.xpath("//table/tr/td/a/@href").getall(),
			}


		try:
			next_page_url = response.xpath("//a[@class='next_page']/@href").get()
		except:
			next_page_url = None
		#next_page_url = 'mtggoldfish.com' + next_page_url
		#print(next_page_url)
		if next_page_url is not None:
			yield response.follow(next_page_url, callback=self.parse, meta = pass_urls)
		else:
			yield pass_urls