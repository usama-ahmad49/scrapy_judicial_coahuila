from tabula import read_pdf

import numpy as np

readPDF = read_pdf('2019-12-20-lista-de-acuerdos.pdf', pages='all', multiple_tables=True, pandas_options={'header':None})
for table in readPDF:
    for col in range(len(table.columns)):
        column = table[col].replace(np.nan, '\n')
        Columntxt = ' '.join(list(column))