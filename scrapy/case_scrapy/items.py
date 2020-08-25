# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class case_Items(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    case_name = scrapy.Field()
    case_brief = scrapy.Field()
    case_status = scrapy.Field()
    date_of_last_review = scrapy.Field()
    plaintiffs = scrapy.Field()
    sector = scrapy.Field()
    industry = scrapy.Field()
    headquarters = scrapy.Field()
    ticker_symbol = scrapy.Field()
    company_market = scrapy.Field()
    market_status = scrapy.Field()
    court = scrapy.Field()
    docket = scrapy.Field()
    judge = scrapy.Field()
    date_filed = scrapy.Field()
    class_period_start = scrapy.Field()
    class_period_end = scrapy.Field()
    fic_summary_table = scrapy.Field()
    fic_doc_links = scrapy.Field()
    fic_links_list = scrapy.Field()
    
