# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import date
import csv
import json
import unicodedata
import re
import sys
import pandas as pd

OUTPUT_DIR = '/dados/flask/cimai/covid/'

def removeChar(s):

    r = s.replace('"','')
    r = r.replace(',','')
    r = r.replace('.','')
    r = r.lstrip()
    r = r.rstrip()
    return(int(r))

cidades_cariri = ['ABAIARA', 'ALTANEIRA', 'ANTONINA DO NORTE', 'ARARIPE', 'ASSARE','AURORA','BARBALHA','BARRO', 'BREJO SANTO', 'CAMPOS SALES', 'CARIRIACU', 'CRATO', 'FARIAS BRITO', 'GRANJEIRO', 'JARDIM', 'JATI', 'JUAZEIRO DO NORTE', 'LAVRAS DA MANGABEIRA', 'MAURITI', 'MILAGRES', 'MISSAO VELHA', 'NOVA OLINDA', 'PENAFORTE', 'PORTEIRAS', 'POTENGI', 'SALITRE', 'SANTANA DO CARIRI', 'TARRAFAS', 'VARZEA ALEGRE']

def prepararPalavra(palavra):

    nfkd = unicodedata.normalize('NFKD', palavra).encode('ASCII','ignore').decode('ASCII')
    return(nfkd.upper())


class InternacoesPipeline(object):
    
    def open_spider(self,spider):
        
        self.file = open(OUTPUT_DIR + 'TODOS.CEARA.HOJE.LEITOS.CSV', 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['data','unidade','uti_ativos','uti_ocupacao','uti_percentual','enfermaria_ativos','enfermaria_ocupacao','enfermaria_ocupacao'])

    def close_spider(self,spider):
        self.file.close()

    
    def process_item(self, item, spider):
        today = date.today()
        data_hoje = today.strftime("%Y-%m-%d")
        
        dic = dict(item)
        unidade = prepararPalavra(dic['unidade'])
        uti_ativos = removeChar(str(dic['uti_ativos']))
        uti_ocupacao = removeChar(str(dic['uti_ocupacao']))
        uti_percentual = str(dic['uti_percentual'])
        enfermaria_ativos = removeChar(str(dic['enfermaria_ativos']))
        enfermaria_ocupacao = removeChar(str(dic['enfermaria_ocupacao']))
        enfermaria_percentual = str(dic['enfermaria_percentual'])
        
        self.writer.writerow([data_hoje,unidade,uti_ativos,uti_ocupacao,uti_percentual,enfermaria_ativos,enfermaria_ocupacao,enfermaria_percentual])

        return item
