# -*- coding: utf-8 -*-
import scrapy
from internacoes.items import InternacoesItem

class OcupacoesSpider(scrapy.Spider):
    name = 'Ocupacoes'
    allowed_domains = ['apps.yoko.pet']
    start_urls = ['https://apps.yoko.pet/covid_csv/spyder/sec-ce-internacoes-hoje.html']

    def parse(self, response):
        tabela = response.xpath('//*[@class="mat-table cdk-table mat-sort"]')[0]
        linhas = tabela.xpath('//tr')
        for i in range(1,len(linhas),1):
            try:
                unidade = linhas[i].xpath('td//text()').extract()[0]
                uti_ativos = linhas[i].xpath('td//text()').extract()[1]
                uti_ocupacao = linhas[i].xpath('td//text()').extract()[2]
                uti_percentual = linhas[i].xpath('td//text()').extract()[3]
                enfermaria_ativos = linhas[i].xpath('td//text()').extract()[4]
                enfermaria_ocupacao = linhas[i].xpath('td//text()').extract()[5]
                enfermaria_percentual = linhas[i].xpath('td//text()').extract()[6]
                entrada = InternacoesItem(unidade=unidade,uti_ativos=uti_ativos,uti_ocupacao=uti_ocupacao,uti_percentual=uti_percentual,enfermaria_ativos=enfermaria_ativos,enfermaria_ocupacao=enfermaria_ocupacao,enfermaria_percentual=enfermaria_percentual)
                yield entrada
            except IndexError:
                pass
