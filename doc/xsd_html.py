import os
import re
import sys
from time import perf_counter
from xml.etree.ElementTree import parse
sys.dont_write_bytecode = True
from leiaute import Leiaute
from modelos import Regra
from modelos import Geral
from modelos import Tabela
import cinto_utilidades as cinto

# TODO estrutura _saida _assets

if 'doc' in os.getcwd():
    os.chdir('../')

caminho_xsd = os.path.join(os.getcwd(), '{}')
caminho_doc = os.path.join(os.getcwd(), 'doc', '{}')

inicio = cinto.obter_arquivo(caminho_doc.format('inicio.html')).read()
fim = cinto.obter_arquivo(caminho_doc.format('fim.html')).read()

# REGRAS
regras = {}

arquivo = cinto.obter_arquivo(caminho_xsd.format('regras.txt'))
id = None

for linha in arquivo.readlines():
    if id is None:
        id = linha.rstrip()
        regras[id] = []
    else:
        if linha.strip() == '':
            id = None
        else:
            texto = linha.rstrip()

            for regra in set(re.findall(r'(REGRA_\w+)', texto)):
                texto = texto.replace(
                    regra, Geral.LINK.format(regra, regra))

            regras[id].append(texto)
arquivo.close()

inicio_tempo = perf_counter()

conteudo = inicio.replace('SUBTITULO', 'Regras de Validação').replace(
    'TITULO', 'Regras')

conteudo += Regra.CABECALHO

for regra in regras:
    texto = '<br />\n'.join(regras[regra])
    conteudo += Regra.LINHA.format(
        id=regra, nome=regra, texto=texto)

conteudo += Geral.RODAPE_TABELA
conteudo += fim

with cinto.obter_arquivo(caminho_doc.format('regras.html'), 'w') as f:
    f.write(conteudo)

# LEIAUTES
leiautes = []
identificadores = [item for item in os.listdir() if item.startswith('evt')]

tipos_globais = {tipo.get('name'): tipo
                 for tipo in parse(caminho_xsd.format('tipos.xsd')).getroot()}

for identificador in identificadores:
    raiz = parse(caminho_xsd.format(identificador)).getroot()
    leiautes.append(Leiaute(raiz, tipos_globais))

leiautes.sort(key=lambda item: item.codigo)

conteudo = inicio.replace('SUBTITULO', 'Leiautes').replace(
    'TITULO', 'Leiautes')

html = ''
for regra in regras:
    texto = '<br />\n'.join(regras[regra])
    html += Regra.LINHA_MODAL.format(nome=regra, texto=texto)

html += ''.join([item.gerar_html() for item in leiautes])

conteudo += html
conteudo += fim

with cinto.obter_arquivo(caminho_doc.format('index.html'), 'w') as f:
    f.write(conteudo)

# TABELAS
tabelas = []
conteudo_tabela = ''
conteudo_indice = ''

caminho_tabelas = os.path.join(os.getcwd(), 'tabelas', '{}')

for tabela in sorted(os.listdir(caminho_tabelas.replace('{}', ''))):
    texto_tabela = []
    anexos_tabela = []

    with cinto.obter_arquivo(caminho_tabelas.format(tabela)) as arquivo_tabela:
        rowspan_linha = {}

        fim_da_tabela = False
        texto_largura_fixa = False

        for indice_linha, linha in enumerate(arquivo_tabela):
            if '__' in linha:
                linha = re.sub('__(.*?)__', '<i>\\1</i>', linha)
            if '##' in linha:
                linha = re.sub('##(.*?)##', '<b>\\1</b>', linha)

            itens_linha = []

            if linha.rstrip() == '===':
                fim_da_tabela = True
                continue
            elif fim_da_tabela:
                if (linha.startswith('>')):
                    if not texto_largura_fixa:
                        anexos_tabela.append(
                            '<pre>{}'.format(linha.rstrip()[1:]))
                        texto_largura_fixa = True
                    else:
                        anexos_tabela.append(linha.rstrip()[1:])
                else:
                    if texto_largura_fixa:
                        texto_largura_fixa = False
                        anexos_tabela.append('</pre>')
                    anexos_tabela.append(
                        '<p>{}</p>'.format(linha.rstrip()))
                continue
            elif indice_linha == 0:
                titulo = linha.rstrip()
                continue
            else:
                extensao_colspan = 0

                for indice_item, item in enumerate(linha.rstrip().split('|')):
                    if indice_linha == 1:
                        rowspan_linha[indice_item] = 0

                        if '>' in item:
                            itens_linha.append('')
                            extensao_colspan += 1
                        else:
                            itens_linha.append(
                                Tabela.CELULA_CABECALHO.format(item))
                    else:
                        if item.startswith('^'):
                            itens_linha.append('')
                            rowspan_linha[indice_item] += 1
                        elif item.startswith('>'):
                            itens_linha.append('')
                            extensao_colspan += 1

                            if rowspan_linha[indice_item] > 0:
                                indice = indice_linha \
                                    - rowspan_linha[indice_item] - 2

                                valor = texto_tabela[indice][indice_item]
                                valor = valor.replace(
                                    'rowspan=""', 'rowspan="{}"'.format(
                                        rowspan_linha[indice_item] + 1))

                                texto_tabela[indice][indice_item] = valor
                                rowspan_linha[indice_item] = 0

                        else:
                            if extensao_colspan != 0:
                                indice = indice_item - extensao_colspan - 1
                                valor = itens_linha[indice].replace(
                                    'colspan=""', 'colspan="{}"'.format(
                                        extensao_colspan + 1))

                                itens_linha[indice] = valor
                                extensao_colspan = 0

                            if rowspan_linha[indice_item] > 0:
                                indice = indice_linha \
                                    - rowspan_linha[indice_item] - 2

                                valor = texto_tabela[indice][indice_item]
                                valor = valor.replace(
                                    'rowspan=""', 'rowspan="{}"'.format(
                                        rowspan_linha[indice_item] + 1))

                                texto_tabela[indice][indice_item] = valor

                            rowspan_linha[indice_item] = 0

                            itens_linha.append(Tabela.CELULA.format(item))

                if extensao_colspan > 0:
                    item = itens_linha[indice_item - extensao_colspan]
                    item = item.replace('colspan=""', 'colspan="{}"'.format(
                        extensao_colspan + 1))
                    itens_linha[indice_item - extensao_colspan] = item

            texto_tabela.append(itens_linha)

        for i in range(indice_item):
            if rowspan_linha[i] > 0:
                texto = texto_tabela[indice_linha - rowspan_linha[i] - 1][i]
                texto = texto.replace('rowspan=""', 'rowspan="{}"'.format(
                    rowspan_linha[i] + 1))
                texto_tabela[indice_linha - rowspan_linha[i] - 1][i] = texto

        conteudo_tabela += Tabela.CABECALHO.format(
            tabela[:-4], indice_item + 1, tabela[:-4], titulo)

        for indice_linha, linha in enumerate(texto_tabela):
            if 'class="grupo"' in linha[0]:
                conteudo_tabela += '<tr class="grupo">\n'
            else:
                conteudo_tabela += '<tr>\n'

            for item in linha:
                if item != '':
                    conteudo_tabela += item.replace(
                        ' class="grupo"', '').replace(
                        ' rowspan=""', '').replace(' colspan=""', '')

            conteudo_tabela += '</tr>\n'

        conteudo_tabela += Geral.RODAPE_TABELA

        if len(anexos_tabela) > 0:
            conteudo_tabela += Tabela.ANEXO.format(
                ''.join([anexo + '\n' for anexo in anexos_tabela]))

    conteudo_indice += Tabela.LINHA_INDICE.format(
        numero=tabela[:-4], titulo=titulo)

    tabelas.append(tabela[:-4])


conteudo = inicio.replace('SUBTITULO', 'Tabelas').replace(
    'TITULO', 'Tabelas')
conteudo += '<ul>\n'
conteudo += conteudo_indice
conteudo += '</ul>\n'
conteudo += conteudo_tabela
conteudo += fim

with cinto.obter_arquivo(caminho_doc.format('tabelas.html'), 'w') as f:
    f.write(conteudo)

# VERIFICAÇÃO DE LINKS

links = []
[links.append(item)
    for item in re.findall(r'"\#(\S+)"', html) if item not in links]

ids = []
[ids.append(item)
    for item in re.findall(r'id="(\S+)"', html) if item not in ids]
ids = ids + tabelas

ausentes = [link for link in links if link not in ids]

if ausentes:
    print('Links quebrados:')
    [print(link) for link in ausentes]

print('Tempo de execução: ', perf_counter() - inicio_tempo)
