import re
from modelos import Geral

RES = 'base:restriction'
NS = {'base': 'http://www.w3.org/2001/XMLSchema'}


def obter_arquivo(caminho, modo='r'):
    """Obtém o stream de um arquivo.

    Args:
        caminho (str): Caminho do arquivo.

    Returns:
        TextIOWrapper: Stream do arquivo.
    """
    return open(caminho, modo, encoding='utf8')


def obter_restriction_final(restriction, tipos_globais):
    """Obtém o elemento restriction final de uma cadeia de reuso.

    Args:
        restriction (Element): XSD que define o elemento inicial.

        tipos_globais (dict): Conjunto de tipos reutilizáveis.

    Returns:
        Element: Último elemento da cadeia.
    """
    base = restriction.get('base')
    if base and base.startswith('TS_'):
        proximo = tipos_globais[base].find(RES, NS)
        if proximo is not None:
            return obter_restriction_final(proximo, tipos_globais)
    else:
        return restriction


def resolver_referencias(texto, item):
    """Identifica referências em um texto e as substitui por links HTML.

    Args:
        texto (str): Texto com referências.

        item (ItemLeiaute): Item contextual da referência.

    Returns:
        str: Texto com links.
    """
    texto = texto.translate(str.maketrans({
        '"': '&quot;',
        '>': '&gt;',
        '<': '&lt;',
    }))

    for ocorrencia in re.findall(r'\{([^\{\}]+)\}\(([^()]+)\)', texto):
        nome = ocorrencia[0]
        endereco = ocorrencia[1]

        if endereco.startswith('../'):
            item_final = item
            saltos = endereco.count('../')

            if not item.categoria.agrupadora():
                item_final = item.pai

            for salto in range(saltos):
                item_final = item_final.pai

            endereco = endereco.replace(
                '../' * saltos, item_final.obter_caminho_encurtado() + '_')

        elif endereco.startswith('/'):
            endereco = endereco.replace('/', item.leiaute.codigo[2:] + '_')

        elif endereco.startswith('./'):
            endereco = '_'.join(
                (item.pai.obter_caminho_encurtado(), endereco[2:]))

        texto = texto.replace(
            '{{{}}}({})'.format(nome, ocorrencia[1]),
            Geral.LINK.format(endereco, nome))

    return re.sub(
        r'(Tabela \d{2})', '<a href="tabelas.html#\\1">\\1</a>', texto)
