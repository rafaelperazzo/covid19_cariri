# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InternacoesItem(scrapy.Item):
    # define the fields for your item here like:
    unidade = scrapy.Field()
    uti_ativos = scrapy.Field()
    uti_ocupacao = scrapy.Field()
    uti_percentual = scrapy.Field()
    enfermaria_ativos = scrapy.Field()
    enfermaria_ocupacao = scrapy.Field()
    enfermaria_percentual = scrapy.Field()