import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CyprusItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CyprusSpider(scrapy.Spider):
	name = 'cyprus'
	start_urls = ['https://www.bankofcyprus.com/en-GB/News_Archive/']

	def parse(self, response):
		articles = response.xpath('//div[@class="item-details"]')
		for article in articles:
			date = article.xpath('.//p[@class="date"]/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response,date):
		title = ' '.join(response.xpath('//div[@class="wrapper intro"]/text()').getall())
		content = response.xpath('//div[@class="dynamic-content rte"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CyprusItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
