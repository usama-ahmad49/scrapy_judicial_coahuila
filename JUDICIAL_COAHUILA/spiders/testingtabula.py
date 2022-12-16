import re

from tabula import read_pdf

import numpy as np

DemandoList = ['Ord.', 'Ejec.', 'Ejecc.', 'Juic.', 'Esp.', 'Aud.', 'Acdo.', 'Cuad.', 'Inc.', 'Cump.', 'Div.', 'Cont.', 'Controv.', 'Alim. ', 'Int.', 'Test.', 'Intest.', 'Reconoc.', 'Perd.', 'Exh.', 'Med.', 'INTERD.', 'Inmat.', 'Solic.', 'Nul.', 'Exhorto', 'Expedientillo', 'Juris.', 'Reg.', 'ACDOS.', 'INTESTAM.', 'Admis.', 'INCDTE.', 'Prov.', 'Via de ', 'Ejecutivo', 'Especial', 'Extinción', 'Providencias', 'Cuaderno', 'Incidente', 'Terceria', 'Controversia', 'Medios preparatorios', 'Oral', 'Jurisdicción', 'Sucesorio', 'Controversias', 'Pago', 'Actos prejudiciales', 'Diversos', 'Guarda', 'Exhorto', 'Via', 'Ejecutiva']
def remove_accents(string):
    # if type(string) is not unicode:
    #     string = unicode(string, encoding='utf-8')

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


readPDF = read_pdf('2021-12-17-LISTA-DE-ACUERDOS-NL0Q9gd5.pdf', pages='all' ,multiple_tables=True, pandas_options={'header':None})
# readPDF = read_pdf('2019-12-20-lista-de-acuerdos.pdf', pages='all' ,multiple_tables=True, pandas_options={'header':None})
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
            if flag==False:
                di[f'r{r}c{col}'] = ' '.join(list(column)).strip().split('\n')[r]
                listofdicts.append(di)


    for i, row in enumerate(listofdicts):
        item = dict()
        if '-TOCA' in row[f'r{i}c0']:
            EXPEDIENTE = ''.join(row[f'r{i}c0'].split('.')[:2])
            EXPEDIENTEORIGEN = ''.join(row[f'r{i}c0'].split('.')[2:3])
            ORGANOJURISDICCIONALORIGEN = ''.join(row[f'r{i}c0'].split('.')[3:])
        TIPO = row[f'r{i}c1']
        if ' VS ' in row[f'r{i}c2'] or 'VS.' in row[f'r{i}c2']or 'VS-' in row[f'r{i}c2']:
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






        # for row in Columntxt.split('\n'):
        #     if '-TOCA' in row:
        #         EXPEDIENTE = ''.join(row.split('.')[:2])
        #         EXPEDIENTEORIGEN = ''.join(row.split('.')[2:3])
        #         ORGANOJURISDICCIONALORIGEN = ''.join(row.split('.')[3:])
        #
        #         # DEMANDADO =