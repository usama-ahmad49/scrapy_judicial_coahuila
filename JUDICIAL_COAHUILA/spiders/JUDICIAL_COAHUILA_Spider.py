import json
import re
from urllib import request

import numpy as np
import scrapy
from tabula import read_pdf

def remove_accents(string):
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    # string = re.sub(u"[ýÿ]", 'y', string)
    # string = re.sub(u"[ñ]", 'n', string)

    string = re.sub(u"[ÀÁÂÃÄÅ]", 'A', string)
    string = re.sub(u"[ÈÉÊË]", 'E', string)
    string = re.sub(u"[ÌÍÎÏ]", 'I', string)
    string = re.sub(u"[ÒÓÔÕÖ]", 'O', string)
    string = re.sub(u"[ÙÚÛÜ]", 'U', string)
    # string = re.sub(u"[ÝŸ]", 'Y', string)
    # string = re.sub(u"[Ñ]", 'N', string)

    string = re.sub(u"[()~!@#$%^&*=-]",'',string)
    string = re.sub(u"[\t\n\r]", "", string)

    string = re.sub(u"[-]", "", string)
    return string
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
            for year in ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022']:
                url = f'https://plataforma-web-api.justiciadigital.gob.mx/listas_de_acuerdos?autoridad_id={lsj["id"]}&ano={year}'
                yield scrapy.Request(url=url, callback=self.parse_juzgado,
                                     meta={'materia': lsj['materia'], 'juzgado': lsj['autoridad']})

    def parse_juzgado(self, response):
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
            readPDF = read_pdf(lsj['archivo'], pages='all', multiple_tables=True, pandas_options={'headers': None})
            for table in readPDF:
                for col in range(len(table.columns)):
                    column = table[col].replace(np.nan, '\n')
                    Columntxt = ' '.join(list(column))
                    # uptill here we get text from whole column seprated by \n , from onw \n to next str is one row in column
