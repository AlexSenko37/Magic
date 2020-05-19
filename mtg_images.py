import scrapy

class ImagesSpider(scrapy.Spider):
	name = "mtg_images"

	start_urls = [
		'https://img.scryfall.com/cards/png/front/7/4/741c479b-5e92-4837-9673-9bc72aa11d26.png?1562637557',
	]

	def parse(self, response):

		start_urls = [
			'https://img.scryfall.com/cards/png/front/7/4/741c479b-5e92-4837-9673-9bc72aa11d26.png?1562637557',
		]
		
		for img_url in start_urls:
			yield ImageItem(image_urls=[img_url])
