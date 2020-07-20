# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class case_Items(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    url = scrapy.Field()
    court = scrapy.Field()
    docket = scrapy.Field()
    judge = scrapy.Field()
    file_date = scrapy.Field()
    cp_start = scrapy.Field()
    cp_end = scrapy.Field()
    defendant_sector = scrapy.Field()
    defendant_industry = scrapy.Field()
    defendant_headquarters = scrapy.Field()
    defendant_ticker = scrapy.Field()
    defendant_market = scrapy.Field()
    defendant_market_status = scrapy.Field()
    
