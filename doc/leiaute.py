from enum import Enum
import itertools
import sys
import re
from modelos import Completo
from modelos import Resumo
from modelos import Geral
import cinto_utilidades as cinto


NS = {'base': 'http://www.w3.org/2001/XMLSchema'}
ANNOTATION = 'base:annotation'


class CategoriaItem(Enum):
    """Representa a categoria de um ItemLeiaute.
    """
    ATRIBUTO = 'A'
    GRUPO = 'G'
    ELEMENTO = 'E'
    CHOICE = 'CG'

    def agrupadora(self):
        """Indica se a categoria é agrupadora.

        Returns:
            bool: True se a categoria for agrupadora; False em caso contrário.
        """
        return self == CategoriaItem.GRUPO or self == CategoriaItem.CHOICE


class Leiaute:
    """Representa o leiaute de um evento do eSocial.
    """

    def __init__(self, xml, tipos_globais):
        """Inicia uma nova instância da classe Leiaute.

        Args:
            xml (Element): XSD que descreve o leiaute.

            tipos_globais (dict): Conjunto de tipos reutilizáveis.

        Raises:
            Exception: O primeiro elemento documentation não inicia com S-XXXX.
        """
        self.tipos_locais = {}

        for complex_type in xml.findall('base:complexType', NS):
            self.tipos_locais[complex_type.attrib['name']] = complex_type

        esocial = xml.find('base:element', NS)

        doc = esocial.find(ANNOTATION, NS).getchildren()[0]

        if not doc.text.startswith('S-'):
            raise Exception(
                'O primeiro elemento documentation não inicia com S-XXXX')

        self.codigo, self.descricao = doc.text.split(' - ', 1)
        self.primeira_ocorrencia_tipo = {}
        self.ultimo_numero = itertools.count(1)

        self.raiz = ItemLeiaute(esocial, tipos_globais, self)

        self.nome = self.raiz.filhos[0].nome

    def imprimir_estrutura(
            self, item_atual=None, ultimo_filho=True, prefixo=''):
        """Imprime a estrutura do Leiaute.

        Args:
            item_atual (ItemLeiaute, optional): Item do leiaute que será
                imprimido. Defaults to None.

            ultimo_filho (bool, optional): Valor que indica se o item atual é o
                último filho de seu pai. Defaults to True.

            prefixo (str, optional): Prefixo que representa a estrutura que
                contém o item atual . Defaults to ''.
        """
        if item_atual is None:
            item_atual = self.raiz

        if item_atual == self.raiz:
            print(' - '.join((self.codigo, self.descricao)))
            print(item_atual.nome)
        else:
            conector = '├── ' if not ultimo_filho else '└── '
            print(''.join((prefixo, conector, item_atual.nome)))

        if item_atual.filhos:
            if item_atual.nivel == 1:
                prefixo = ''
            else:
                prefixo += '    ' if ultimo_filho else '|   '

            for filho in item_atual.filhos[:-1]:
                self.imprimir_estrutura(filho, False, prefixo)

            self.imprimir_estrutura(item_atual.filhos[-1], True, prefixo)

    def gerar_texto(self):
        """Gera a representação do Leiaute em texto simples.

        Returns:
            str: Representação do Leiaute em texto simples.
        """

        txt = f'{self.codigo} - {self.nome}\n{self.descricao}\n\n'

        txt += self.raiz.gerar_texto_resumo()

        txt += self.raiz.gerar_texto_completo()

        return txt

    def gerar_html(self):
        """Gera a representação do Leiaute em HTML.

        Returns:
            str: Representação do Leiaute em HTML.
        """
        html = (
            Resumo.CABECALHO.format(
                self.nome, self.codigo, self.descricao)
            + self.raiz.gerar_html_resumo()
            + Geral.RODAPE_TABELA)

        self.ultimo_numero = itertools.count(1)

        html += (
            Completo.CABECALHO.format(self.codigo, self.descricao)
            + self.raiz.gerar_html_completo()
            + Geral.RODAPE_TABELA)

        return html


class ItemLeiaute:
    """Representa um item do leiaute.
    """

    def __init__(self, xml, tipos_globais, leiaute, nivel=1, pai=None):
        """Inicia uma nova instância da classe ItemLeiaute.

        Args:
            xml (Element): XSD que descreve o item.

            tipos_globais (dict): Conjunto de tipos reutilizáveis.

            leiaute (Leiaute): Leiaute que contém o item.

            nivel (int, optional): Indicador do nível hierárquico que o item
                ocupa. Defaults to 1.

            pai (ItemLeiaute, optional): Pai do item. Defaults to None.
        """
        self.analisar_definicao_item(xml, tipos_globais, leiaute, nivel, pai)

    def analisar_definicao_item(
            self, xml, tipos_globais, leiaute, nivel=1, pai=None):
        """Analisa a definição do item para identificar suas propriedades.

        Args:
            xml (Element): XSD que descreve o item.

            tipos_globais (dict): Conjunto de tipos reutilizáveis.

            leiaute (Leiaute): Leiaute que contém o item.

            nivel (int, optional): Indicador do nível hierárquico que o item
                ocupa. Defaults to 1.

            pai (ItemLeiaute, optional): Pai do item. Defaults to None.

        Raises:
            Exception: Definição de tipo não encontrada.
        """
        tag = xml.tag[34:]

        if tag == 'element' or tag == 'attribute':
            self.leiaute = leiaute
            self.nivel = nivel
            self.pai = pai
            self.numeracao = next(leiaute.ultimo_numero)
            self.nome = xml.attrib['name']
            self.referencia = None
            self.categoria = CategoriaItem.GRUPO
            self.filhos = []

            if nivel == 1:
                self.caminho = '_'.join((self.leiaute.codigo[2:], self.nome))
                self.descricao = [self.nome]
            elif nivel == 2:
                self.caminho = self.leiaute.codigo[2:]
            else:
                self.caminho = '_'.join([self.pai.caminho, self.nome])

            definicao_tipo = None

            if 'type' in xml.attrib:
                self.tipo = xml.attrib['type']

                if self.tipo.startswith(('T_', 'TS_')):
                    if self.tipo in leiaute.tipos_locais:
                        definicao_tipo = leiaute.tipos_locais[self.tipo]
                    elif self.tipo in tipos_globais:
                        definicao_tipo = tipos_globais[self.tipo]
                    else:
                        raise Exception('Definição de tipo não encontrada: {}'
                                        .format(self.tipo))

                if self.tipo.startswith('T_'):
                    if self.tipo not in leiaute.primeira_ocorrencia_tipo:
                        leiaute.primeira_ocorrencia_tipo[self.tipo] = self
                    else:
                        self.referencia = \
                            leiaute.primeira_ocorrencia_tipo[self.tipo]

                    self.analisar_definicao_item(
                        definicao_tipo, tipos_globais, leiaute, nivel, self)

                elif self.tipo.startswith(('xs:', 'TS_')):
                    self.categoria = CategoriaItem.ELEMENTO

                    if tag == 'attribute':
                        self.categoria = CategoriaItem.ATRIBUTO

                if definicao_tipo is not None:
                    self.analisar_annotation(definicao_tipo)
            else:
                definicao_tipo = xml.find('base:simpleType', NS)

                if definicao_tipo is not None:
                    self.categoria = CategoriaItem.ELEMENTO

                self.tipo = None

            self.analisar_restrictions(
                xml.attrib, definicao_tipo, tipos_globais)

            for filho in xml:
                tag_filho = filho.tag[34:]

                if tag_filho == 'simpleType':
                    self.categoria = CategoriaItem.ELEMENTO

                    if tag == 'attribute':
                        self.categoria = CategoriaItem.ATRIBUTO

                    self.analisar_annotation(filho)
                elif tag_filho == 'annotation':
                    self.analisar_annotation(xml)
                elif tag_filho == 'complexType':
                    self.analisar_definicao_item(
                        filho, tipos_globais, leiaute, nivel, self)

        elif tag == 'complexType':
            atributo = xml.find('base:attribute', NS)

            if atributo is not None:
                self.filhos.append(ItemLeiaute(
                    atributo, tipos_globais, leiaute, nivel + 1, self))

            for filho in xml:
                tag_filho = filho.tag[34:]

                if tag_filho == 'annotation':
                    self.analisar_annotation(xml)
                elif tag_filho == 'sequence':
                    self.analisar_definicao_item(
                        filho, tipos_globais, leiaute, nivel, self)

        elif tag == 'sequence' or tag == 'choice':
            if tag == 'choice':
                self.categoria = CategoriaItem.CHOICE

            for filho in xml:
                tag_filho = filho.tag[34:]

                if 'ref' in filho.attrib:
                    continue
                elif tag_filho == 'choice':
                    self.analisar_definicao_item(
                        filho, tipos_globais, leiaute, nivel, self)
                elif tag_filho == 'element':
                    self.filhos.append(ItemLeiaute(
                        filho, tipos_globais, leiaute, nivel + 1, self))

    def analisar_annotation(self, xml):
        """Analisa o elemento annotation para identificar a documentação e as
            restrições de preenchimento do item.

        Args:
            xml (Element): XSD que descreve o item.
        """
        annotation = xml.find(ANNOTATION, NS)
        if annotation is not None:

            if (not hasattr(self, 'descricao')
                    or self.descricao[0] != self.nome):
                self.descricao = [annotation[0].text]

            self.validacao = []
            self.origem = []
            self.evento_origem = []
            self.descricao_completa = []
            self.chaves = []
            self.regras = []
            self.condicoes = {'O': None}

            documentacao = {
                'validacao': self.validacao,
                'origem': self.origem,
                'evento_origem': self.evento_origem,
                'descricao': self.descricao,
                'descricao_completa': self.descricao_completa,
            }

            destino_documentacao = 'descricao'

            for documentation in annotation[1:]:
                texto = documentation.text

                if texto.startswith('Validação: '):
                    self.validacao.append(texto[11:])
                    destino_documentacao = 'validacao'

                elif texto.startswith('Origem: '):
                    self.origem.append(texto[8:])
                    destino_documentacao = 'origem'

                elif texto.startswith('Evento de origem: '):
                    self.evento_origem.append(texto[18:])
                    destino_documentacao = 'evento_origem'

                elif texto.startswith('CHAVE_GRUPO: '):
                    self.chaves = [chave[1:-1]
                                   for chave in texto[13:].split(', ')]

                elif texto.startswith('REGRA:'):
                    self.regras.append(texto[6:])

                elif texto.startswith('CONDICAO_GRUPO: '):
                    if ';' in texto:
                        condicoes = {}

                        for condicao in texto[16:].split('; '):
                            tipo, texto = condicao.split(' ', 1)
                            condicoes[tipo] = texto

                        self.condicoes = condicoes
                    else:
                        self.condicoes = {texto[16:]: None}

                elif texto.startswith('DESCRICAO_COMPLETA:'):
                    self.descricao_completa.append(texto[19:])
                    destino_documentacao = 'descricao_completa'

                else:
                    documentacao[destino_documentacao].append(texto)

    def analisar_restrictions(self, atributos, definicao_tipo, tipos_globais):
        """Analisa os atributos de um elemento para identificar a documentação
            e as restrições de preenchimento do item.

        Args:
            atributos (dict): Conjunto de atributos de um elemento.

            definicao_tipo (Element): Elemento que contém a definição do tipo.

            tipos_globais (dict): Conjunto de tipos reutilizáveis.
        """
        minimo = '1'
        maximo = '1'

        if self.pai is not None and self.pai.categoria == CategoriaItem.CHOICE:
            minimo = '0'
        else:
            if 'minOccurs' in atributos:
                minimo = atributos['minOccurs']

            if 'maxOccurs' in atributos:
                if atributos['maxOccurs'] == 'unbounded':
                    maximo = 'N'
                else:
                    maximo = atributos['maxOccurs']

        self.ocorrencia = (minimo, maximo)
        self.valores_validos = {}

        if not self.categoria.agrupadora():
            self.tamanho_fixo = None
            self.tamanho_lista = None
            self.tamanho_faixa = None

            if definicao_tipo is not None:
                restriction = definicao_tipo.find('base:restriction', NS)

                if restriction is not None:
                    restriction = cinto.obter_restriction_final(
                        restriction, tipos_globais)

                    base = restriction.get('base')

                    menor_tamanho = sys.maxsize
                    maior_tamanho = 0

                    for enum in restriction.findall('base:enumeration', NS):
                        annotation = enum.find(ANNOTATION, NS)
                        if annotation:
                            descricoes = annotation.getchildren()

                            if len(descricoes) == 1:
                                valor = cinto.codificar_sobrescrito(
                                    cinto.resolver_referencias(
                                        descricoes[0].text, self))

                            else:
                                self.valores_validos[descricoes[0].text] = ''

                                valor = cinto.codificar_sobrescrito(
                                    cinto.resolver_referencias(
                                        descricoes[1].text, self))
                        else:
                            valor = None

                        menor_tamanho = min(
                            menor_tamanho, len(enum.attrib['value']))

                        maior_tamanho = max(
                            maior_tamanho, len(enum.attrib['value']))

                        self.valores_validos[enum.attrib['value']] = valor

                    if self.valores_validos:
                        if menor_tamanho == maior_tamanho:
                            self.tamanho_fixo = menor_tamanho
                        else:
                            self.tamanho_faixa = (menor_tamanho, maior_tamanho)

                    tamanho_fixo = restriction.find('base:length', NS)
                    if tamanho_fixo is not None:
                        self.tamanho_fixo = int(tamanho_fixo.attrib['value'])

                    tamanho_minimo = restriction.find('base:minLength', NS)
                    tamanho_maximo = restriction.find('base:maxLength', NS)
                    if tamanho_minimo is not None:
                        self.tamanho_faixa = (
                            tamanho_minimo.attrib['value'],
                            tamanho_maximo.attrib['value'])

                    padrao = restriction.find('base:pattern', NS)
                    if padrao is not None and self.tamanho_fixo is None:
                        regex = padrao.attrib['value']

                        self.tamanho_lista = [int(item) for item in re.findall(
                            r'\\d{(\d+)}', regex)]

                        if len(self.tamanho_lista) == 1:
                            if r'\d' in regex:
                                posicao = regex.index(r'\d')
                            else:
                                posicao = 0

                            self.tamanho_fixo = posicao + self.tamanho_lista[0]
                            self.tamanho_lista = None

                        if not self.tamanho_lista:
                            match = re.match(r'(\\d|\\w){(\d+),(\d+)}', regex)
                            if match:
                                self.tamanho_faixa = (
                                    match.group(2), match.group(3))

                        if definicao_tipo.get('name') == 'TS_perApur':
                            self.tamanho_lista = [4, 7]
                            self.tamanho_fixo = None
                            self.tamanho_faixa = None

                    digitos_totais = restriction.find('base:totalDigits', NS)
                    if digitos_totais is not None:
                        self.tamanho_faixa = (1, digitos_totais.get('value'))

                    fracao = restriction.find('base:fractionDigits', NS)
                    if fracao is not None:
                        self.decimais = fracao.get('value')
                    else:
                        self.decimais = '-'

            elif 'type' in atributos:
                base = atributos['type']

            if base == 'xs:date':
                self.rotulo_tipo = 'D'
                self.tamanho_fixo = 10
                self.decimais = '-'
            elif base == 'xs:string' or base == 'xs:ID':
                self.rotulo_tipo = 'C'
            else:
                self.rotulo_tipo = 'N'
        else:
            self.rotulo_tipo = '-'
            self.decimais = '-'

    def gerar_html_completo(self, modelo_linha=Completo.LINHA,
                            modelo_referencia=Completo.REFERENCIA):
        """Gera a representação do item em HTML para a visão completa.

        Args:
            modelo_linha (str): Modelo de linha comum.

            modelo_referencia (str): Modelo de linha de referência.

        Returns:
            str: Representação do item em HTML.
        """
        marcador_grupo = ''
        nome = self.nome
        id = nome

        if self.categoria.agrupadora():
            marcador_grupo = ' class="grupo"'
            if self.categoria == CategoriaItem.CHOICE:
                marcador_grupo = ' class="grupo-choice"'

            if self.referencia is not None and self.referencia != self:
                id = '_'.join((self.pai.nome, id))

            nome = Geral.LINK.format('r_{}'.format(self.caminho), self.nome)

        html = modelo_linha.format(
            indice=next(self.leiaute.ultimo_numero),
            caminho=self.caminho,
            marcador_grupo=marcador_grupo,
            nome=nome,
            pai=self.gerar_link_pai(),
            tipo_elemento=self.categoria.value,
            tipo=self.rotulo_tipo,
            ocorrencia=self.gerar_descricao_ocorrencia(),
            tamanho=self.gerar_descricao_tamanho(),
            decimais=self.decimais,
            descricao=self.gerar_descricao(),
        )

        if self.referencia is not None and self.referencia != self:
            html += modelo_referencia.format(
                nome=self.referencia.nome,
                id=self.referencia.caminho,
                nome_pai=self.referencia.pai.nome,
                id_pai=self.referencia.pai.caminho
            )
            return html

        for filho in self.filhos:
            html += filho.gerar_html_completo(modelo_linha, modelo_referencia)

        return html

    def gerar_html_resumo(self, modelo_linha=Resumo.LINHA,
                          modelo_referencia=Resumo.REFERENCIA):
        """Gera a representação do item em HTML para a visão resumida.

        Args:
            modelo_linha (str): Modelo de linha comum.

            modelo_referencia (str): Modelo de linha de referência.

        Returns:
            str: Representação do item em HTML.
        """
        identificador = self.nome

        if self.referencia is not None:
            identificador = '_'.join((self.pai.nome, identificador))

        html = modelo_linha.format(
            link_completo=self.caminho,
            identificador_evento=self.leiaute.nome,
            id_nome=identificador,
            nome=self.nome,
            pai=self.gerar_link_pai(),
            nivel=self.nivel,
            descricao=cinto.resolver_referencias(
                self.descricao[0].rstrip('.'), None),
            ocorrencia=self.gerar_descricao_ocorrencia(),
            chave=self.gerar_descricao_chaves(),
            condicao=self.gerar_descricao_condicoes(),
        )

        for filho in self.filhos:
            if filho.categoria.agrupadora():
                if self.referencia is None:
                    html += filho.gerar_html_resumo(
                        modelo_linha, modelo_referencia)
                else:
                    html += modelo_referencia.format(
                        nome=self.referencia.nome,
                        nome_pai=self.referencia.pai.nome,
                        id_pai=self.referencia.pai.caminho,
                        id=self.referencia.caminho
                    )

                    break

        return html

    def gerar_descricao(self):
        """Gera a descrição do item.

        Returns:
            str: Descrição do item.
        """
        if self.descricao_completa:
            descricoes = self.descricao_completa
        else:
            descricoes = self.descricao

        rotulo = '<br />\n<strong>{}</strong>'

        descricao = '<br />\n'.join([cinto.resolver_referencias(
            descricao, self) for descricao in descricoes])

        if self.valores_validos:
            descricao += rotulo.format('Valores válidos:')
            linha_cabecalho = ''

            for chave in self.valores_validos:
                if self.valores_validos[chave] == '':
                    descricao += '{}<br />\n{}'.format(linha_cabecalho, chave)
                elif self.valores_validos[chave] is not None:
                    descricao += ' - '.join((
                        rotulo.format(chave), self.valores_validos[chave]))

                    if linha_cabecalho == '':
                        linha_cabecalho = '<br />\n'
                else:
                    descricao += ' {},'.format(chave)

            descricao = descricao.rstrip(',')

        if self.origem:
            descricao += rotulo.format('Origem:') + ' '
            descricao += '<br />\n'.join([cinto.resolver_referencias(
                origem, self) for origem in self.origem])

        if self.evento_origem:
            descricao += rotulo.format('Evento de origem:') + ' '
            descricao += '<br />\n'.join([cinto.resolver_referencias(
                origem, self) for origem in self.evento_origem])

        if self.validacao:
            descricao += rotulo.format('Validação:') + ' '
            descricao += '<br />\n'.join([cinto.resolver_referencias(
                validacao, self) for validacao in self.validacao])

        if self.regras:
            descricao += (
                rotulo.format('Regra{} de validação:'.format(
                    's' if len(self.regras) > 1 else '')))

            for regra in self.regras:
                descricao += '<br />\n' + \
                    Geral.LINK.format(regra, regra)

        return descricao

    def gerar_descricao_condicoes(self):
        """Gera a descrição das condições de uso do item.

        Returns:
            str: Descrição das condições de uso do item.
        """
        return ';<br />\n'.join([
            condicao if self.condicoes[condicao] is None else ' '.join(
                (
                    condicao,
                    cinto.resolver_referencias(self.condicoes[condicao], self)
                )) for condicao in self.condicoes
        ])

    def gerar_descricao_chaves(self):
        """Gera a descrição das chaves do item.

        Returns:
            str: Descrição das chaves do item.
        """
        if self.chaves:
            if self.referencia is None:
                caminho = self.caminho
            else:
                caminho = self.referencia.caminho

            return ', '.join([
                Geral.LINK.format('{}_{}'.format(caminho, chave), chave)
                for chave in self.chaves])
        else:
            return '-'

    def gerar_descricao_ocorrencia(self):
        """Gera a descrição da ocorrência do item.

        Returns:
            str: Descrição da ocorrência do item.
        """
        if self.ocorrencia[0] == self.ocorrencia[1]:
            return self.ocorrencia[0]
        else:
            return '{}-{}'.format(*self.ocorrencia)

    def gerar_descricao_tamanho(self):
        """Gera a descrição do tamanho do item.

        Returns:
            str: Descrição do tamanho do item.

        Raises:
            Exception: Tamanho não definido.
        """
        if self.categoria.agrupadora():
            return '-'

        if self.tamanho_fixo:
            return self.tamanho_fixo if self.rotulo_tipo != 'D' else '-'
        elif self.tamanho_faixa:
            return '{}-{}'.format(*self.tamanho_faixa)
        elif self.tamanho_lista:
            self.tamanho_lista.sort()
            return '{} ou {}'.format(
                ', '.join([str(item) for item in self.tamanho_lista[:-1]]),
                self.tamanho_lista[-1])
        else:
            raise Exception(
                'O tamanho do item {} não foi identificado.'.format(self.nome))

    def gerar_link_pai(self):
        """Gera um link para o pai do item, caso exista.

        Returns:
            str: Link para o pai do item.
        """
        if self.pai is None:
            return ''
        else:
            return Geral.LINK.format(
                'r_{}'.format(self.pai.caminho),
                self.pai.nome)

    def gerar_texto_resumo(self, modelo_linha=Resumo.LINHA_TEXTO):
        """Gera a representação do item em texto simples para a visão resumida.

        Args:
            modelo_linha (str): Modelo de linha comum.

        Returns:
            str: Representação do item em texto simples.
        """
        texto = modelo_linha.format(
            nivel=self.nivel,
            nome=self.nome,
            pai='-' if self.pai is None else self.pai.nome,
            descricao=self.descricao[0],
            ocorrencia=self.gerar_descricao_ocorrencia(),
            chave=self.gerar_descricao_chaves_texto(),
            condicao=self.gerar_descricao_condicoes_texto(),
        )

        for filho in self.filhos:
            if filho.categoria.agrupadora():
                texto += filho.gerar_texto_resumo()

        return texto

    def gerar_texto_completo(self, modelo_linha=Completo.LINHA_TEXTO):
        """Gera a representação do item em texto simples para a visão completa.

        Args:
            modelo_linha (str): Modelo de linha comum.

        Returns:
            str: Representação do item em texto simples.
        """
        html = modelo_linha.format(
            nome=self.nome,
            pai=self.pai.nome if self.pai is not None else '-',
            tipo_elemento=self.categoria.value,
            tipo=self.rotulo_tipo,
            ocorrencia=self.gerar_descricao_ocorrencia(),
            tamanho=self.gerar_descricao_tamanho(),
            decimais=self.decimais,
            descricao=self.gerar_descricao_texto(),
        )

        if '\n\n' in self.gerar_descricao_texto():
            print('aqui')

        for filho in self.filhos:
            html += filho.gerar_texto_completo(modelo_linha)

        return html

    def gerar_descricao_texto(self):
        """Gera a descrição do item.

        Returns:
            str: Descrição do item.
        """

        if self.descricao_completa:
            descricoes = self.descricao_completa
        else:
            descricoes = self.descricao

        descricao = '\n'.join(descricoes)

        if self.valores_validos:
            descricao += '\nValores válidos:\n'

            for chave in self.valores_validos:
                if self.valores_validos[chave] == '':
                    descricao += '{}\n'.format(chave)
                elif self.valores_validos[chave] is not None:
                    descricao += f'{chave} - {self.valores_validos[chave]}\n'
                else:
                    descricao += ' {},'.format(chave)

            descricao = descricao.rstrip(',').rstrip('\n')

        if self.origem:
            descricao += '\nOrigem: '
            descricao += '\n'.join([origem for origem in self.origem])

        if self.evento_origem:
            descricao += '\nEvento de origem: '
            descricao += '\n'.join([origem for origem in self.evento_origem])

        if self.validacao:
            descricao += '\nValidação: '
            descricao += '\n'.join([validacao for validacao in self.validacao])

        if self.regras:
            descricao += '\nRegras de validação:\n'

            descricao += '\n'.join([regra for regra in self.regras])

        return descricao

    def gerar_descricao_chaves_texto(self):
        """Gera a descrição das chaves do item.

        Returns:
            str: Descrição das chaves do item.
        """
        return ', '.join(self.chaves) if self.chaves else '-'

    def gerar_descricao_condicoes_texto(self):
        """Gera a descrição das condições de uso do item.

        Returns:
            str: Descrição das condições de uso do item.
        """
        return '\n'.join([
            condicao if self.condicoes[condicao] is None else ' '.join(
                (
                    condicao,
                    self.condicoes[condicao],
                )) for condicao in self.condicoes
        ])
