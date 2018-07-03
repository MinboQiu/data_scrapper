# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LandChinaItem(scrapy.Item):
    name = scrapy.Field()
    regulationNo = scrapy.Field()
    landSource = scrapy.Field()
    tenureOfUse = scrapy.Field()
    industry = scrapy.Field()
    landLevel = scrapy.Field()
    price = scrapy.Field()
    owner = scrapy.Field()
    plotRatioUpperLimit = scrapy.Field()
    plotRatioDownLimit = scrapy.Field()
    dateOfDeliveryAgreed = scrapy.Field()
    dateOfConstructionAgreed = scrapy.Field()
    dateOfConstructionActual = scrapy.Field()
    dateOfCompletionAgreed = scrapy.Field()
    dateOfCompletionActual = scrapy.Field()
    approvedBy = scrapy.Field()
    dateOfSigning = scrapy.Field()
    district = scrapy.Field()
    location = scrapy.Field()
    area = scrapy.Field()
    usage = scrapy.Field()
    wayOfSupply = scrapy.Field()
    url = scrapy.Field()
    payments = scrapy.Field()


class Payment(scrapy.Item):
    date = scrapy.Field()
    amount = scrapy.Field()
    comment = scrapy.Field()
