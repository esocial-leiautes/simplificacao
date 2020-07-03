import os
import re
import sys
from xml.etree.ElementTree import parse
sys.dont_write_bytecode = True
from leiaute import Leiaute
from modelos import Regra
from modelos import Geral
from modelos import Tabela
import cinto_utilidades as cinto

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
                    regra, Geral.LINK.format(regra.lower(), regra))

            regras[id].append(texto)
arquivo.close()

arquivo = cinto.obter_arquivo(caminho_doc.format('regras.html'), 'w')
arquivo.write(inicio.replace('SUBTITULO', 'Regras de Validação')
              .replace('TITULO', 'Regras'))
arquivo.write(Regra.CABECALHO)

for regra in regras:
    texto = '<br />\n'.join(regras[regra])
    arquivo.write(
        Regra.LINHA.format(id=regra.lower(), nome=regra, texto=texto))

arquivo.write(Geral.RODAPE_TABELA)
arquivo.write(fim)
arquivo.close()

# LEIAUTES
leiautes = []
identificadores = [item for item in os.listdir() if item.startswith('evt')]

tipos_globais = {tipo.get('name'): tipo
                 for tipo in parse(caminho_xsd.format('tipos.xsd')).getroot()}

for identificador in identificadores:
    raiz = parse(caminho_xsd.format(identificador)).getroot()
    leiautes.append(Leiaute(raiz, tipos_globais))

leiautes.sort(key=lambda item: item.codigo)

arquivo = cinto.obter_arquivo(caminho_doc.format('index.html'), 'w')
arquivo.write(inicio.replace('SUBTITULO', 'Leiautes')
              .replace('TITULO', 'Leiautes'))

for regra in regras:
    texto = '<br />\n'.join(regras[regra])
    arquivo.write(Regra.LINHA_MODAL.format(nome=regra, texto=texto))

html = ''.join([item.gerar_html() for item in leiautes])

arquivo.writelines(html)
arquivo.write(fim)
arquivo.close()

# TABELAS
tabelas = []

arquivo = cinto.obter_arquivo(caminho_doc.format('tabelas.html'), 'w')
arquivo.write(inicio.replace('SUBTITULO', 'Tabelas')
              .replace('TITULO', 'Tabelas'))

conteudo = ''
conteudo_indice = ''

caminho_tabelas = caminho_doc = os.path.join(os.getcwd(), 'tabelas', '{}')

for tabela in sorted(os.listdir(caminho_tabelas.replace('{}', ''))):
    texto_tabela = []
    anexos_tabela = []

    with cinto.obter_arquivo(caminho_tabelas.format(tabela)) as arquivo_tabela:
        rowspan_linha = {}

        fim_da_tabela = False
        texto_largura_fixa = False

        for indice_linha, linha in enumerate(arquivo_tabela):
            if '__' in linha:
                linha = re.sub('__(.*?)__', '<em>\\1</em>', linha)
            if '##' in linha:
                linha = re.sub('##(.*?)##', '<strong>\\1</strong>', linha)

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
                    anexos_tabela.append('<p>{}</p>'.format(linha.rstrip()))
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

        conteudo += Tabela.CABECALHO.format(
            tabela[:-4], indice_item + 1, tabela[:-4], titulo)

        for indice_linha, linha in enumerate(texto_tabela):
            if 'class="grupo"' in linha[0]:
                conteudo += '<tr class="grupo">\n'
            else:
                conteudo += '<tr>\n'

            for item in linha:
                if item != '':
                    conteudo += item.replace(
                        ' rowspan=""', '').replace(' colspan=""', '') + '\n'

            conteudo += '</tr>\n'

        conteudo += Geral.RODAPE_TABELA

        if len(anexos_tabela) > 0:
            conteudo += Tabela.ANEXO.format(
                ''.join([anexo + '\n' for anexo in anexos_tabela]))

        conteudo_indice += Tabela.LINHA_INDICE.format(
            numero=tabela[:-4], titulo=titulo)

    tabelas.append('Tabela {}'.format(tabela[:-4]))

arquivo.write('\n<ul>\n')
arquivo.write(conteudo_indice)
arquivo.write('</ul>\n')
arquivo.write(conteudo)
arquivo.write(fim)
arquivo.close()

# VERIFICAÇÃO DE LINKS

links = []
regex = (
    # href="#1000_Id"
    r'"\#(\d{4}_\S+)"'
    # href="#resumo_evtInfoEmpregador:esocial"
    r'|"\#(resumo_evt\S+)"'
    # href="#evtInfoEmpregador:esocial"
    r'|"\#(evt\S+)"'
    # href="regra_remun_ja_existe_desligamento"
    r'|"\#(regra\S+)"'
    # href="tabelas.html#Tabela 05"
    r'|\#(Tabela \d{2})')

for itens in re.findall(regex, html):
    [links.append(item) for item in itens if item != '' and item not in links]

ids = []
regex = (
    # id="1000_Id"
    r'id="(\d{4}_\S+)"'
    # id="evtInfoEmpregador"
    r'|id="(evt\S+)"'
    # id="resumo_evtInfoEmpregador:esocial"
    r'|id="(resumo_evt\S+)"')

for itens in re.findall(regex, html):
    [ids.append(item) for item in itens if item != '' and item not in ids]

ids = ids + [id.lower() for id in regras.keys()] + tabelas

ausentes = [link for link in links if link not in ids]

if ausentes:
    print('Links quebrados:')
    [print(link) for link in ausentes]
