import io
import json
import numpy as np
from tabula import read_pdf
from tabulate import tabulate
# from camelot import read_pdf
import pandas as pd
import scrapy
from urllib import request

class JudicialCoahuilaSpider(scrapy.Spider):
    name = 'JUDICIAL_COAHUILA_Spider'
    # allowed_domains = ['www.pjecz.gob.mx']
    start_urls = ['https://plataforma-web-api.justiciadigital.gob.mx/distritos']

    def parse(self, response, **kwargs):
        listAcuerdos = json.loads(response.text)
        for lst in listAcuerdos:
            url = f'https://plataforma-web-api.justiciadigital.gob.mx/autoridades?distrito_id={lst["id"]}'
            yield scrapy.Request(url=url, callback=self.parse_distrito)

    def parse_distrito(self, response):
        listJuzgado = json.loads(response.text)
        for lsj in listJuzgado:
            for year in ['2015','2016','2017','2018','2019','2020','2021','2022']:
                url = f'https://plataforma-web-api.justiciadigital.gob.mx/listas_de_acuerdos?autoridad_id={lsj["id"]}&ano={year}'
                yield scrapy.Request(url=url, callback=self.parse_juzgado, meta={'materia':lsj['materia'], 'juzgado':lsj['autoridad']})

    def parse_juzgado(self,response):
        listArchivo = json.loads(response.text)
        for lsj in listArchivo:
            fecha = lsj['fecha']
            try:
                response = request.urlretrieve(lsj['url'], lsj['archivo'])
                # wget.download(lsj['url'], lsj['archivo'])
                downloaded = True
            except:
                downloaded = False
            if downloaded == False:
                continue
            readPDF = read_pdf(lsj['archivo'] , pages='all', multiple_tables=True, pandas_options={'headers':None})
            for table in readPDF:
                for col in range(len(table.columns)):
                    column = table[col].replace(np.nan, '\n')
                    Columntxt = ' '.join(list(column))
                    # uptill here we get text from whole column seprated by \n 




