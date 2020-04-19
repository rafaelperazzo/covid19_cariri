# -*- coding: utf-8 -*-
#GPS: https://raw.githubusercontent.com/kelvins/Municipios-Brasileiros/master/csv/municipios.csv
from flask import Flask
from flask import render_template
from flask import request,url_for,send_file,send_from_directory,redirect,flash,Markup,Response,session
from datetime import datetime
import MySQLdb
from werkzeug.utils import secure_filename
import logging
import sys
import numpy as np
import csv
import pandas as pd
from flask_mail import Mail
from flask_mail import Message
import random
import json
import glob
import warnings
warnings.filterwarnings('ignore')
import logging
from sqlalchemy import *
import pymysql
from flask_httpauth import HTTPBasicAuth
import hashlib
import time
import tracemalloc
import semantic_version
from flask_wkhtmltopdf import Wkhtmltopdf
import os

WORKING_DIR='/dados/flask/covid/'
COVID_DIR = '/dados/flask/cimai/covid/'

logging.basicConfig(filename=WORKING_DIR + 'app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.debug("INICIANDO LOG")

app = Flask(__name__)
auth = HTTPBasicAuth()

versao = semantic_version.Version('1.0.0')
def hash(str):
    result = hashlib.sha256(str.encode())
    return(result.hexdigest())

def getCores(quantidade=1):
    r = lambda: random.randint(0,255)
    cores = []
    for i in range(0,quantidade,1):
        cor = ('#%02X%02X%02X' % (r(),r(),r()))
        cores.append(cor)
    return(cores)

def dadosCovid():
    # ANTONINA DO NORTE, JATI E PENAFORTE - ausentes
    CSV_DIR = '/dados/flask/cimai/covid/'
    cariri = [' JUAZEIRO DO NORTE ', ' CRATO ', ' BARBALHA ', ' BREJO SANTO ']
    cariri = [' ABAIARA ', ' ALTANEIRA ', ' ANTONINA DO NORTE ', ' ARARIPE ', ' ASSARE ', ' AURORA ', ' BARBALHA ', ' BARRO ', ' BREJO SANTO ', ' CAMPOS SALES ', ' CARIRIACU ', ' CRATO ', ' FARIAS BRITO ', ' GRANJEIRO ', ' JARDIM ', ' JATI ', ' JUAZEIRO DO NORTE ', ' LAVRAS DA MANGABEIRA ', ' MAURITI ', ' MILAGRES ', ' MISSAO VELHA ', ' NOVA OLINDA ', ' PENAFORTE ', ' PORTEIRAS ', ' POTENGI ', ' SALITRE ', ' SANTANA DO CARIRI ', ' TARRAFAS ', ' VARZEA ALEGRE ']
    for i in range(0,len(cariri),1):
        cariri[i] = cariri[i].lstrip()
        cariri[i] = cariri[i].rstrip()

    gps = pd.read_csv(CSV_DIR + 'cidades.cariri.completo.csv',delimiter=",",encoding='utf8',decimal='.')
    df_ceara = pd.read_csv(CSV_DIR + 'TODOS.CEARA.HOJE.CSV',delimiter=",",encoding='utf8',decimal='.')
    df_cariri = df_ceara[df_ceara['cidade'].isin(cariri)].sort_values(by=['data','cidade'])
    agrupados = df_cariri.groupby(['data','cidade'])

    evolucao = agrupados['confirmado','suspeitos','obitos'].sum()
    dia = agrupados['confirmado','suspeitos','obitos'].sum().tail(len(cariri)).sum(axis=0).tolist()
    porCidade = agrupados['confirmado','suspeitos','obitos'].sum().tail(len(cariri))
    porCidade = pd.merge(porCidade,gps,on='cidade')
    agrupadosEvolucao = df_cariri.groupby(['data'])
    evolucaoTotal = agrupadosEvolucao['confirmado','suspeitos','obitos'].sum()
    cidades_confirmadas = porCidade[porCidade['confirmado']>0]
    '''
    atualizacao = evolucaoTotal.index[-1]
    date_o = datetime.strptime(atualizacao,'%Y-%m-%d')
    atualizacao = date_o.strftime("%d/%m/%Y")
    '''
    datas = evolucaoTotal.index.to_list()
    confirmados = evolucaoTotal['confirmado'].to_list()
    suspeitos = evolucaoTotal['suspeitos'].to_list()
    obitos = evolucaoTotal['obitos'].to_list()
    evolucaoDataset = [datas,confirmados,suspeitos,obitos]
    qtde_cidades_confirmadas = cidades_confirmadas.shape[0]

    #RESUMO POR RESULTADO DE EXAME, SEXO E IDADE
    CASOS_DIR = '/dados/flask/cimai/covid/'
    casos_cariri = pd.read_csv(CASOS_DIR + 'covid.ceara.csv',delimiter=",",encoding='latin1',decimal='.')
    casos_cariri.fillna(0,inplace=True)
    casos_cariri = casos_cariri[['codigoPaciente','bairroPaciente','municipioPaciente','sexoPaciente','idadePaciente','resultadoFinalExame']]
    cariri = ['ABAIARA', 'ALTANEIRA', 'ANTONINA DO NORTE', 'ARARIPE', 'ASSARE','AURORA','BARBALHA','BARRO', 'BREJO SANTO', 'CAMPOS SALES', 'CARIRIACU', 'CRATO', 'FARIAS BRITO', 'GRANJEIRO', 'JARDIM', 'JATI', 'JUAZEIRO DO NORTE', 'LAVRAS DA MANGABEIRA', 'MAURITI', 'MILAGRES', 'MISSAO VELHA', 'NOVA OLINDA', 'PENAFORTE', 'PORTEIRAS', 'POTENGI', 'SALITRE', 'SANTANA DO CARIRI', 'TARRAFAS', 'VARZEA ALEGRE']
    casos_cariri = casos_cariri[casos_cariri['municipioPaciente'].isin(cariri)]
    casos_cariri['resultadoFinalExame'].replace([0],['Em Análise'],inplace=True)
    casos_cariri['sexoPaciente'].replace(['Feminino'],['FEMININO'],inplace=True)
    casos_cariri['sexoPaciente'].replace(['Masculino'],['MASCULINO'],inplace=True)
    casos_cariri['sexoPaciente'].replace(['0'],['FEMININO'],inplace=True)
    casos_cariri['bairroPaciente'].replace([0],['NAO INFORMADO'],inplace=True)
    #POR SEXO E RESULTADO POSITIVO
    porSexo = casos_cariri[casos_cariri['resultadoFinalExame']=='Positivo'].groupby(['municipioPaciente','sexoPaciente'])
    tabelaPositivoPorSexo = porSexo['codigoPaciente'].count().to_frame()
    tabelaPositivoPorSexo.columns = ['Quantidade']
    tabelaPositivoPorSexo.index.names = ['Cidade','Sexo']
    #POR RESULTADO POSITIVO E BAIRRO
    porBairro = casos_cariri[casos_cariri['resultadoFinalExame']=='Positivo'].groupby(['municipioPaciente','bairroPaciente'])
    tabelaPositivoPorBairro = porBairro['codigoPaciente'].count().to_frame()
    tabelaPositivoPorBairro.columns = ['Quantidade']
    tabelaPositivoPorBairro.index.names = ['Cidade','Bairro']
    #POR SEXO E RESULTADO NEGATIVO
    porSexo = casos_cariri[casos_cariri['resultadoFinalExame']=='Negativo'].groupby(['municipioPaciente','sexoPaciente'])
    tabelaNegativoPorSexo = porSexo['codigoPaciente'].count().to_frame()
    tabelaNegativoPorSexo.columns = ['Quantidade']
    tabelaNegativoPorSexo.index.names = ['Cidade','Bairro']
    #POR SEXO E RESULTADO EM ANÁLISE
    porSexo = casos_cariri[casos_cariri['resultadoFinalExame']=='Em Análise'].groupby(['municipioPaciente','sexoPaciente'])
    tabelaAnalisePorSexo = porSexo['codigoPaciente'].count().to_frame()
    tabelaAnalisePorSexo.columns = ['Quantidade']
    tabelaAnalisePorSexo.index.names = ['Cidade','Bairro']
    #TOTAL DE CONFIRMADOS POR SEXO
    porSexo = casos_cariri[casos_cariri['resultadoFinalExame']=='Positivo'].groupby(['sexoPaciente'])
    listaSexos = porSexo['codigoPaciente'].count().tolist()
    listaSexosTotais = porSexo['codigoPaciente'].count().index.tolist()
    #Total de exames realizados
    tipoResultado = ['Negativo','Positivo','Em Análise']
    totalExames = casos_cariri[casos_cariri['resultadoFinalExame'].isin(tipoResultado)].shape[0]
    totalNegativos = casos_cariri[casos_cariri['resultadoFinalExame']=='Negativo'].shape[0]

    #Por Idade
    idades = [0,2,5,10,16,20,40,60,80,100]
    casos_positivos = casos_cariri[casos_cariri['resultadoFinalExame']=='Positivo']
    gruposPositivosIdades = casos_positivos.groupby((pd.cut(casos_positivos['idadePaciente'],idades)))
    porIdadePositivo = gruposPositivosIdades['codigoPaciente'].count().to_frame()
    porIdadePositivo.index.name = 'Faixa Etária'
    porIdadePositivo.columns = ['Quantidade']

    casos_analise = casos_cariri[casos_cariri['resultadoFinalExame']=='Em Análise']
    gruposAnaliseIdades = casos_analise.groupby((pd.cut(casos_analise['idadePaciente'],idades)))
    porIdadeAnalise = gruposAnaliseIdades['codigoPaciente'].count().to_frame()
    porIdadeAnalise.index.name = 'Faixa Etária'
    porIdadeAnalise.columns = ['Quantidade']

    faixas = porIdadePositivo.index.tolist()
    for i in range(0,len(faixas),1):
        faixas[i] = str(faixas[i]).replace('(','[')
        faixas[i] = faixas[i].replace(']','[')
    intervaloIdades = faixas
    dadosPositivoIdade = porIdadePositivo['Quantidade'].tolist()
    dadosAnaliseIdade = porIdadeAnalise['Quantidade'].tolist()

    agrupamentos =[tabelaPositivoPorSexo.to_html(),tabelaPositivoPorBairro.to_html(),listaSexos,listaSexosTotais,totalExames,totalNegativos,intervaloIdades,dadosPositivoIdade,dadosAnaliseIdade]

    return(dia,evolucao,porCidade,evolucaoTotal,evolucaoDataset,cidades_confirmadas,agrupamentos)

@app.route("/")
def covid():

    dados,evolucao,porCidade,evolucaoTotal,evolucaoDataSet,cidades_confirmadas,agrupamentos = dadosCovid()
    porCidade = porCidade[['cidade','confirmado','suspeitos','obitos']]
    mapa_cidade = cidades_confirmadas['cidade'].tolist()
    mapa_confirmados = cidades_confirmadas['confirmado'].tolist()
    mapa_gps = cidades_confirmadas['gps'].tolist()
    arquivo = open(COVID_DIR + 'time.txt','r')
    conteudo = str(arquivo.read())
    cores = getCores(len(agrupamentos[6]))
    return(render_template('covid.html',cores=cores,dados=dados,evolucao=evolucao.to_html(),porCidade=porCidade.to_html(index=False,index_names=False),atualizacao=conteudo,acumulados=evolucaoDataSet,cidades_confirmadas=cidades_confirmadas[['cidade','confirmado','suspeitos','obitos']].to_html(index=False),total_confirmadas=cidades_confirmadas.shape[0],mapa_cidade=mapa_cidade,mapa_confirmados=mapa_confirmados,mapa_gps=mapa_gps,agrupamentos=agrupamentos))

@app.route("/atualizaDatasets")
def atualizaDatasets():
    CSV_DIR = '/dados/flask/cimai/covid/'
    cariri = ['ABAIARA', 'ALTANEIRA', 'ANTONINA DO NORTE', 'ARARIPE', 'ASSARE', 'AURORA', 'BARBALHA', 'BARRO', 'BREJO SANTO', 'CAMPOS SALES', 'CARIRIACU', 'CRATO', 'FARIAS BRITO', 'GRANJEIRO', 'JARDIM', 'JATI', 'JUAZEIRO DO NORTE', 'LAVRAS DA MANGABEIRA', 'MAURITI', 'MILAGRES', 'MISSAO VELHA', 'NOVA OLINDA', 'PENAFORTE', 'PORTEIRAS', 'POTENGI', 'SALITRE', 'SANTANA DO CARIRI', 'TARRAFAS', 'VARZEA ALEGRE']
    df_ceara = pd.read_csv(CSV_DIR + 'TODOS.CEARA.HOJE.CSV',delimiter=",",encoding='utf8',decimal='.')
    df_cariri = df_ceara[df_ceara['cidade'].isin(cariri)].sort_values(by=['data','cidade'])
    df_ceara.to_csv('/dados/www/html/covid_csv/todos.ceara.hoje.csv',index=False)
    df_cariri.to_csv('/dados/www/html/covid_csv/todos.cariri.hoje.csv',index=False)
    df_ceara.to_csv('/dados/flask/cimai/covid/todos.ceara.hoje.csv',index=False)
    df_cariri.to_csv('/dados/flask/cimai/covid/todos.cariri.hoje.csv',index=False)
    return("SUCESSO")
if __name__ == "__main__":
    app.run()
