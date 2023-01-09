import json
import re
from urllib import request

import numpy as np
import scrapy
from tabula import read_pdf, read_pdf_with_template
from scrapy.crawler import CrawlerProcess

DemandoList = ['Ord.', 'Ejec.', 'Ejecc.', 'Juic.', 'Esp.', 'Aud.', 'Acdo.', 'Cuad.', 'Inc.', 'Cump.', 'Div.', 'Cont.', 'Controv.', 'Alim. ', 'Int.', 'Test.', 'Intest.', 'Reconoc.', 'Perd.', 'Exh.', 'Med.', 'INTERD.', 'Inmat.', 'Solic.', 'Nul.', 'Exhorto', 'Expedientillo', 'Juris.', 'Reg.', 'ACDOS.', 'INTESTAM.', 'Admis.', 'INCDTE.', 'Prov.', 'Via de ', 'Ejecutivo', 'Especial', 'Extinción', 'Providencias', 'Cuaderno', 'Incidente', 'Terceria', 'Controversia', 'Medios preparatorios', 'Oral', 'Jurisdicción', 'Sucesorio', 'Controversias', 'Pago', 'Actos prejudiciales', 'Diversos', 'Guarda', 'Exhorto', 'Via', 'Ejecutiva']
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
        for lst in listAcuerdos[:1]:
            url = f'https://plataforma-web-api.justiciadigital.gob.mx/autoridades?distrito_id={lst["id"]}'
            yield scrapy.Request(url=url, callback=self.parse_distrito)

    def parse_distrito(self, response):
        listJuzgado = json.loads(response.text)
        for lsj in listJuzgado:
            for year in ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022','2023'][-2:]:
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
            # readPDF = read_pdf(lsj['archivo'], pages='all', multiple_tables=True, pandas_options={'headers': None})
            # readPDF = read_pdf(lsj['archivo'], area=[150, 1, 770.5, 561], pages='all',multiple_tables=True, pandas_options={'header': None})
            readPDF = read_pdf_with_template(lsj['archivo'], template_path = 'tabula-2023-01-06-LISTA-DE-ACUERDOS-E0zV9vm0.json',pages='all', pandas_options={'header': None})

            for table in readPDF:
                table.drop(columns=table.columns[0], axis=1, inplace=True)
                table.fillna(method='ffill', inplace=True)
                lastCol = len(table.columns)
                table = table.groupby(1).agg(
                    {2: lambda s: " ".join(s), lastCol: lambda s: ''.join(set("".join(s)))}).reset_index()
                listofdicts = []
                for index, row in table.iterrows():
                    item = dict()
                    item['expediente'] = row[1].strip()
                    if 'LIC.' in row[2]:
                        TIPO = '.'.join(row[2].split('.')[:2])
                    elif '.-' in row[2]:
                        TIPO = row[2].split('.-')[0]
                    else:
                        TIPO = row[2].split('.')[0]
                    item['tipo'] = remove_accents(TIPO)
                    if 'VS' in row[2]:
                        ACTOR = row[2].split(TIPO).split('VS.')[0].replace('.', '').strip()
                        DEMANDADO = row[2].split(TIPO).split('VS.')[1].replace('.', '').strip()
                    else:
                        ACTOR = row[2].split('.'.join(row[2].split('.')[:2]))[-1].replace('.', '').strip()
                        DEMANDADO = ''
                    item['actor'] = remove_accents(ACTOR)
                    item['demandado'] = remove_accents(DEMANDADO)
            '''
            for table in readPDF:
                listofdicts = []
                for col in range(len(table.columns)):
                    flag = False
                    column = table[col].replace(np.nan, '\n')
                    ColumntxtList = ' '.join(list(column)).split('\n')

                    for r in range(len(' '.join(list(column)).strip().split('\n'))):
                        di = dict()
                        for v in listofdicts:
                            if f'r{r}' in ','.join(list(v.keys())):
                                v[f'r{r}c{col}'] = ' '.join(list(column)).strip().split('\n')[r]
                                flag = True
                        if flag == False:
                            di[f'r{r}c{col}'] = ' '.join(list(column)).strip().split('\n')[r]
                            listofdicts.append(di)

                for i, row in enumerate(listofdicts):
                    item = dict()
                    if '-TOCA' in row[f'r{i}c0']:
                        EXPEDIENTE = ''.join(row[f'r{i}c0'].split('.')[:2])
                        EXPEDIENTEORIGEN = ''.join(row[f'r{i}c0'].split('.')[2:3])
                        ORGANOJURISDICCIONALORIGEN = ''.join(row[f'r{i}c0'].split('.')[3:])
                    TIPO = row[f'r{i}c1']
                    if ' VS ' in row[f'r{i}c2'] or 'VS.' in row[f'r{i}c2'] or 'VS-' in row[f'r{i}c2']:
                        actor = row[f'r{i}c2'].split('VS')[0]
                        demandado = row[f'r{i}c2'].split('VS')[-1]
                        for search in DemandoList:
                            index = demandado.find(" %s " % search)
                            if index != -1:
                                first_part = demandado[:index]
                                break
                        try:
                            demandado = first_part
                        except:
                            pass
                        if '.-' in actor:
                            item['actor'] = remove_accents(actor.split('.-')[-1].strip()).upper()
                        elif '-' in actor:
                            item['actor'] = remove_accents(actor.split('-')[-1].strip()).upper()
                        elif '.' in actor:
                            item['actor'] = remove_accents(actor.split('.')[-1].strip()).upper()
                        elif 'PROMOVIDO POR' in actor:
                            item['actor'] = remove_accents(actor.split('PROMOVIDO POR')[-1].strip()).upper()
                        elif 'PROMOVIDO PRO' in actor:
                            item['actor'] = remove_accents(actor.split('PROMOVIDO PRO')[-1].strip()).upper()
                        elif ')' in actor:
                            item['actor'] = remove_accents(actor.split(')')[-1].strip()).upper()
                        else:
                            item['actor'] = remove_accents(actor.strip()).upper()
                        item['demandado'] = remove_accents(demandado.strip()).upper()
            '''


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(JudicialCoahuilaSpider)
process.start()
