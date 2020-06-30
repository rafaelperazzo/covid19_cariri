# -*- coding: utf-8 -*-
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
'''
from flask import Flask
from flask import render_template
from flask import request,url_for,send_file,send_from_directory,redirect,flash,Markup,Response,session
from datetime import datetime
#import MySQLdb
#from werkzeug.utils import secure_filename
import logging
import sys
import numpy as np
import csv
import pandas as pd
#from flask_mail import Mail
#from flask_mail import Message
import random
import json
#import glob
import warnings
warnings.filterwarnings('ignore')
#from sqlalchemy import *
#import pymysql
#from flask_httpauth import HTTPBasicAuth
import hashlib
import time
#import tracemalloc
import semantic_version
#from flask_wkhtmltopdf import Wkhtmltopdf
import os
import requests
import sqlite3
from bs4 import BeautifulSoup


WORKING_DIR='/dados/flask/covid/'
COVID_DIR = '/dados/flask/cimai/covid/'

logging.basicConfig(filename=WORKING_DIR + 'app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
logging.debug("INICIANDO LOG")

app = Flask(__name__)
#auth = HTTPBasicAuth()

versao = semantic_version.Version('1.2.0')

def getSenha(arquivo):
    f = open(arquivo,'r')
    senha = f.read()
    f.close()
    return(str(senha))

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
    porCidade = agrupados['confirmado','suspeitos','obitos','recuperados'].sum().tail(len(cariri))
    porCidade = pd.merge(porCidade,gps,on='cidade')
    agrupadosEvolucao = df_cariri.groupby(['data'])
    evolucaoTotal = agrupadosEvolucao['confirmado','suspeitos','obitos'].sum()
    cidades_confirmadas = porCidade[porCidade['confirmado']>0]

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
    #casos_cariri = casos_cariri[['codigoPaciente','bairroPaciente','municipioPaciente','sexoPaciente','idadePaciente','resultadoFinalExame','dataObito','obitoConfirmado']]
    casos_cariri = casos_cariri[['codigoPaciente','bairroPaciente','municipioPaciente','sexoPaciente','idadePaciente','resultadoFinalExame','dataObito','obitoConfirmado']]
    cariri = ['ABAIARA', 'ALTANEIRA', 'ANTONINA DO NORTE', 'ARARIPE', 'ASSARE','AURORA','BARBALHA','BARRO', 'BREJO SANTO', 'CAMPOS SALES', 'CARIRIACU', 'CRATO', 'FARIAS BRITO', 'GRANJEIRO', 'JARDIM', 'JATI', 'JUAZEIRO DO NORTE', 'LAVRAS DA MANGABEIRA', 'MAURITI', 'MILAGRES', 'MISSAO VELHA', 'NOVA OLINDA', 'PENAFORTE', 'PORTEIRAS', 'POTENGI', 'SALITRE', 'SANTANA DO CARIRI', 'TARRAFAS', 'VARZEA ALEGRE']
    casos_cariri = casos_cariri[casos_cariri['municipioPaciente'].isin(cariri)]
    casos_cariri['resultadoFinalExame'].replace([0],['Em Análise'],inplace=True)
    casos_cariri['sexoPaciente'].replace(['Feminino'],['FEMININO'],inplace=True)
    casos_cariri['sexoPaciente'].replace(['Masculino'],['MASCULINO'],inplace=True)
    casos_cariri['sexoPaciente'].replace(['0'],['FEMININO'],inplace=True)
    casos_cariri['bairroPaciente'].replace([0],['NAO INFORMADO'],inplace=True)
    casos_cariri['bairroPaciente'].replace(['VILA FATIMA'],['FATIMA'],inplace=True)
    casos_cariri.drop_duplicates(subset='codigoPaciente',inplace=True,keep='last')
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

    bairros = []
    for i in range(0,len(tabelaPositivoPorBairro.index),1):
        linha = list(tabelaPositivoPorBairro.index[i])
        confirmados_bairro = 1
        try:
            confirmados_bairro = tabelaPositivoPorBairro.loc[linha[0],linha[1]].tolist()[0]
        except KeyError:
            confirmados_bairro = 1

        if linha[1]=='NAO INFORMADO' or linha[1]=='ZONA RURAL':
            linha[1] = 'CENTRO'

        estado = 'CEARA'
        #senha = getSenha(WORKING_DIR + 'passwd.nominatim').rstrip()
        if linha[0]=='ARARIPE':
            consulta = linha[0] + ' ' + estado
        else:
            consulta = linha[0] + ' ' + estado + ' ' + linha[1]
        #requisicao = json.loads(requests.get("https://apps.yoko.pet/osm/search?q='" + consulta + "'&format=json", auth=('nominatim', senha)).text)
        requisicao = json.loads(requests.get("https://apps.yoko.pet/osm/search?q='" + consulta + "'&format=json").text)
        try:
            latitude = requisicao[0]['lat']
            longitude = requisicao[0]['lon']
            gps = str(latitude) + ',' + str(longitude)
        except IndexError:
            requisicao = json.loads(requests.get("https://apps.yoko.pet/osm/search?q='" + linha[0] + ' ' + estado + "'&format=json", auth=('nominatim', 'autoridade')).text)
            latitude = requisicao[0]['lat']
            longitude = requisicao[0]['lon']
            gps = str(latitude) + ',' + str(longitude)
        linha.append(gps)
        linha.append(latitude)
        linha.append(longitude)
        linha.append(confirmados_bairro)
        bairros.append(linha)

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
    #casos_cariri.drop_duplicates(subset='codigoPaciente',inplace=True,keep='last')
    porSexo = casos_cariri[casos_cariri['resultadoFinalExame']=='Positivo'].groupby(['sexoPaciente'])
    listaSexos = porSexo['codigoPaciente'].count().tolist()
    listaSexosTotais = porSexo['codigoPaciente'].count().index.tolist()

    porSexoObitos = casos_cariri[casos_cariri['obitoConfirmado']==1.0].groupby(['sexoPaciente'])
    listaSexosTotaisObitos = porSexoObitos['codigoPaciente'].count().tolist()
    
    #Total de exames realizados
    tipoResultado = ['Negativo','Positivo','Em Análise']
    totalExames = casos_cariri[casos_cariri['resultadoFinalExame'].isin(tipoResultado)].shape[0]
    totalNegativos = casos_cariri[casos_cariri['resultadoFinalExame']=='Negativo'].shape[0]

    #Por Idade
    #idades = [0,2,5,10,16,20,40,60,80,100]
    idades = [0,5,20,40,60,120]
    casos_positivos = casos_cariri[casos_cariri['resultadoFinalExame']=='Positivo']
    gruposPositivosIdades = casos_positivos.groupby((pd.cut(casos_positivos['idadePaciente'],idades,right=False)))
    porIdadePositivo = gruposPositivosIdades['codigoPaciente'].count().to_frame()
    porIdadePositivo.index.name = 'Faixa Etária'
    porIdadePositivo.columns = ['Quantidade']

    obitos_confirmados = casos_cariri[casos_cariri['obitoConfirmado']==1.0]
    gruposObitosIdades = obitos_confirmados.groupby((pd.cut(obitos_confirmados['idadePaciente'],idades,right=False)))
    porIdadeObitos = gruposObitosIdades['codigoPaciente'].count().to_frame()
    porIdadeObitos.index.name = 'Faixa Etária'
    porIdadeObitos.columns = ['Quantidade']

    casos_analise = casos_cariri[casos_cariri['resultadoFinalExame']=='Em Análise']
    gruposAnaliseIdades = casos_analise.groupby((pd.cut(casos_analise['idadePaciente'],idades)))
    porIdadeAnalise = gruposAnaliseIdades['codigoPaciente'].count().to_frame()
    porIdadeAnalise.index.name = 'Faixa Etária'
    porIdadeAnalise.columns = ['Quantidade']

    faixas = porIdadePositivo.index.tolist()
    for i in range(0,len(faixas),1):
        faixas[i] = str(faixas[i]).replace('(','[')
    intervaloIdades = faixas
    dadosPositivoIdade = porIdadePositivo['Quantidade'].tolist()
    dadosAnaliseIdade = porIdadeAnalise['Quantidade'].tolist()

    agrupamentos =[tabelaPositivoPorSexo.to_html(),tabelaPositivoPorBairro.to_html(),listaSexos,listaSexosTotais,totalExames,totalNegativos,intervaloIdades,dadosPositivoIdade,dadosAnaliseIdade,porIdadeObitos,listaSexosTotaisObitos]

    return(dia,evolucao,porCidade,evolucaoTotal,evolucaoDataset,cidades_confirmadas,agrupamentos,bairros)

@app.route("/", methods=['GET', 'POST'])
def covid():
    return(render_template('index.html'))
    dados,evolucao,porCidade,evolucaoTotal,evolucaoDataSet,cidades_confirmadas,agrupamentos,bairros = dadosCovid()
    total_populacao = porCidade['populacao'].astype(int).sum()
    col_populacao = porCidade['populacao'].astype(int)
    col_confirmados = porCidade['confirmado'].astype(int)
    porCidade = porCidade[['cidade','confirmado','suspeitos','obitos']]
    porCidade['incidencia'] = ((col_confirmados/col_populacao)*100000).round(2)
    cidades_confirmadas['incidencia'] = ((cidades_confirmadas['confirmado'].astype(int)/cidades_confirmadas['populacao'].astype(int))*100000).round(2)
    mapa_cidade = cidades_confirmadas['cidade'].tolist()
    mapa_confirmados = cidades_confirmadas['confirmado'].tolist()
    mapa_gps = cidades_confirmadas['gps'].tolist()
    mapa_incidencia = (cidades_confirmadas['incidencia'].astype(float)*50).tolist()
    arquivo = open(COVID_DIR + 'time.txt','r')
    conteudo = str(arquivo.read())
    arquivo.close()
    total_confirmados = porCidade['confirmado'].astype(int).sum()
    porCemMil = (total_confirmados/total_populacao)*100000
    porCemMil = '{:.2f}'.format(porCemMil)
    cores = getCores(len(agrupamentos[6]))
    # *******
    if request.method == "GET":
        if 'q' in request.args:
            q = int(request.args.get('q'))
            if (q==1):
                return(render_template('mapa.cidades.html',mapa_cidade=mapa_cidade,mapa_confirmados=mapa_confirmados,mapa_gps=mapa_gps,mapa_incidencia=mapa_incidencia))            
            elif (q==2):
                return(render_template('mapa.bairros.html',bairros=bairros))            
            elif (q==3):
                return(render_template('por.sexo.html',agrupamentos=agrupamentos))
            elif (q==4):
                return(render_template('por.idade.html',agrupamentos=agrupamentos,cores=cores))
            elif (q==5):
                return(render_template('por.evolucao.html',acumulados=evolucaoDataSet))
            else:
                return("Nao implementado...")            
    #*****
    return(render_template('covid.html',bairros=bairros,porCemMil=porCemMil,cores=cores,dados=dados,evolucao=evolucao.to_html(),porCidade=porCidade.to_html(index=False,index_names=False),atualizacao=conteudo,acumulados=evolucaoDataSet,cidades_confirmadas=cidades_confirmadas[['cidade','confirmado','suspeitos','obitos','incidencia']].to_html(index=False),total_confirmadas=cidades_confirmadas.shape[0],mapa_cidade=mapa_cidade,mapa_confirmados=mapa_confirmados,mapa_gps=mapa_gps,mapa_incidencia=mapa_incidencia,agrupamentos=agrupamentos))

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


def salvarDadosGrafico(arquivo,tabela,labels,dados,dados2=[]):
    conn = sqlite3.connect(arquivo)
    c = conn.cursor()
    if (len(dados2)==0):
        df = pd.DataFrame({"label": labels, "quantidade":dados})
        df.to_sql(tabela,conn,if_exists='replace',index=False)
    else:
        df = pd.DataFrame({"label": labels, "quantidade":dados,"quantidade2": dados2})
        df.to_sql(tabela,conn,if_exists='replace',index=False)
    conn.close()

def salvarDadosMapa(arquivo,tabela,cidade,confirmados,latitude,longitude,porCemMil,recuperados,emRecuperacao,obitos):
    #TODO: Adaptar para cidades e bairros
    conn = sqlite3.connect(arquivo)
    c = conn.cursor()
    df = pd.DataFrame({"cidade": cidade, "confirmados":confirmados,"latitude": latitude,"longitude":longitude,"incidencia": porCemMil,"recuperados": recuperados,"emRecuperacao": emRecuperacao,"obitos": obitos})
    df.to_sql(tabela,conn,if_exists='replace',index=False)
    conn.close()

def salvarDadosMapaBairros(arquivo,tabela,cidade,bairros,latitude,longitude,confirmados):
    #TODO: Adaptar para cidades e bairros
    conn = sqlite3.connect(arquivo)
    c = conn.cursor()
    df = pd.DataFrame({"cidade": cidade, "bairro":bairros,"latitude": latitude,"longitude":longitude,"confirmados": confirmados})
    df.to_sql(tabela,conn,if_exists='replace',index=False)
    conn.close()

def salvarDadosInternacoes(arquivo,tabela):
    conn = sqlite3.connect(arquivo)
    c = conn.cursor()
    df_internacoes = pd.read_csv(COVID_DIR + 'TODOS.CEARA.HOJE.LEITOS.CSV',delimiter=",",encoding='latin1',decimal='.')
    dados_internacoes = [df_internacoes['uti_ativos'].sum(),df_internacoes['uti_ocupacao'].sum(),df_internacoes['enfermaria_ativos'].sum(),df_internacoes['enfermaria_ocupacao'].sum()]
    dados_percentuais = [df_internacoes['uti_ocupacao'].sum()/df_internacoes['uti_ativos'].sum(),df_internacoes['enfermaria_ocupacao'].sum()/df_internacoes['enfermaria_ativos'].sum()]
    dados_percentuais = [round(num, 2) for num in dados_percentuais]
    dados_percentuais = [int(num*100) for num in dados_percentuais]
    df_ocupacao = pd.DataFrame([dados_percentuais],columns=['uti','enfermaria'],index=['percentuais'])
    df_ocupacao.to_sql("dadosInternacoes",conn,if_exists='replace',index=False)
    df_internacoes.to_sql("internacoes",conn,if_exists='replace',index=False)
    conn.close()

def salvarDadosObitos(arquivo,tabela):
    conn = sqlite3.connect(arquivo)
    c = conn.cursor()

    HTML_DIR = "/dados/www/html/covid_csv/spyder/"
    soup = BeautifulSoup(open(HTML_DIR + "sec-ce-comorbidades-hoje.html","rb"),'lxml')

    obitos_comorbidade = soup.find_all('text',attrs={'class':'value-text'})[5].get_text()
    obitos_comorbidade = obitos_comorbidade.lstrip()
    obitos_comorbidade = obitos_comorbidade.rstrip()

    obitos_por_dia = soup.find_all('text',attrs={'class':'value-text'})[3].get_text()
    obitos_por_dia = obitos_por_dia.lstrip()
    obitos_por_dia = obitos_por_dia.rstrip()

    mediana_idade = soup.find_all('text',attrs={'class':'value-text'})[7].get_text()
    mediana_idade = mediana_idade.lstrip()
    mediana_idade = mediana_idade.rstrip()

    dados = [obitos_comorbidade,obitos_por_dia,mediana_idade]
    df = pd.DataFrame([dados],columns=['comorbidades','porDia','mediana_idade'])
    df.to_sql(tabela,conn,if_exists='replace',index=False)

@app.route("/atualizarDados")
def atualizarDados():
    dados,evolucao,porCidade,evolucaoTotal,evolucaoDataSet,cidades_confirmadas,agrupamentos,bairros = dadosCovid()
    ARQUIVO = COVID_DIR + 'dados.cariri.hoje.sqlite3'
    salvarDadosGrafico(ARQUIVO,"confirmadosPorIdade",agrupamentos[6],agrupamentos[7])
    salvarDadosGrafico(ARQUIVO,"confirmadosPorSexo",agrupamentos[3],agrupamentos[2])    
    salvarDadosGrafico(ARQUIVO,"obitosPorIdade",agrupamentos[6],agrupamentos[9]['Quantidade'].tolist()) 
    salvarDadosGrafico(ARQUIVO,"obitosPorSexo",agrupamentos[3],agrupamentos[10])
    salvarDadosGrafico(ARQUIVO,"evolucao",evolucaoDataSet[0],evolucaoDataSet[1],evolucaoDataSet[3])
    porCemMil = ((cidades_confirmadas['confirmado']/cidades_confirmadas['populacao'])*100000).round(2)
    conf = np.array(cidades_confirmadas['confirmado'].tolist())
    ob = np.array(cidades_confirmadas['obitos'].tolist())
    rec = np.array(cidades_confirmadas['recuperados'].tolist())
    emRecuperacao = (conf-ob-rec).tolist()
    salvarDadosMapa(ARQUIVO,"cidadesConfirmadas",cidades_confirmadas['cidade'].tolist(),cidades_confirmadas['confirmado'].tolist(),cidades_confirmadas['latitude'].tolist(),cidades_confirmadas['longitude'].tolist(),porCemMil.tolist(),rec.tolist(),emRecuperacao,ob.tolist())
    df_bairros = pd.DataFrame.from_records(bairros)
    df_bairros.columns = ['cidade','bairro','gps','latitude','longitude','confirmados']
    salvarDadosMapaBairros(ARQUIVO,"bairros",df_bairros['cidade'].tolist(),df_bairros['bairro'].tolist(),df_bairros['latitude'].tolist(),df_bairros['longitude'].tolist(),df_bairros['confirmados'].tolist())
    salvarDadosInternacoes(ARQUIVO,"internacoes")
    salvarDadosObitos(ARQUIVO,"obitosResumo")
    return("SUCESSO\n")

@app.route("/teste")
def teste():
    return("OK")

if __name__ == "__main__":
    app.run()
