import xml.etree.ElementTree as ET
import io
import re
import sys
import os

def remover_namespace(elemento, ns):
    return elemento.tag.replace('{' + ns['base'] + '}', '')


def tratar_tipo(raiz, nome, pai, ns, indice, resumo, tipos_usados, evento, indice_completo, caminho_completo, numero):
    for tipo in raiz.findall('base:complexType', ns):
        if tipo.get('name') == nome:
            return navegar(raiz, tipo, pai, ns, indice, resumo, tipos_usados, nome in tipos_usados, evento, False, indice_completo, caminho_completo, numero)

    return navegar(raiz, tipos_include[nome], pai, ns, indice, resumo, tipos_usados, nome in tipos_usados, evento, False, indice_completo, caminho_completo, numero)


def converter_tipo(tipo):
    if tipo == 'xs:string' or tipo == 'xs:ID':
        return 'C'
    elif tipo == 'xs:date':
        return 'D'
    else:
        return 'N'


def imprimir_elemento(elemento, pai, ns, raiz, resumo, evento, indice_completo, caminho_completo):
    nome = elemento.get('name')
    tamanho = ''
    tamanho_especial = None
    decimais = '-'
    valores_validos = []
    descricao = None
    tipo_elemento = 'A' if remover_namespace(elemento, ns) == 'attribute' else 'E'

    if pai.get('name') + '_' == caminho_completo:
        caminho_completo = ''

    if caminho_completo.endswith(pai.get('name') + '_'):
        caminho = caminho_completo + elemento.get('name')
    else:
        caminho = caminho_completo + pai.get('name') + '_' + elemento.get('name')

    if evento in caminho:
        caminho = caminho.replace(evento + '_', '')

    tipoSimples = elemento.find('base:simpleType', ns)

    if tipoSimples is None and 'type' in elemento.attrib and elemento.attrib['type'].startswith('TS_'):
        if elemento.attrib['type'] == 'TS_perApur':
            tamanho_especial = '4 ou 7'

        tipoSimples = tipos_include[elemento.attrib['type']]
        descricao = elemento.findall('base:annotation', ns)

        if len(descricao) == 0:
            descricao = tipoSimples.findall('base:annotation', ns)

    if tipoSimples is not None:
        restricoes = tipoSimples.find('base:restriction', ns)

        if restricoes.get('base').startswith('TS_'):
            restricoes = tipos_include[restricoes.get('base')].find('base:restriction', ns)

        if descricao is None:
            descricao = tipoSimples.findall('base:annotation', ns)

        tipo = restricoes.get('base')

        if converter_tipo(tipo) == 'D':
            tamanho = '-'

        for restricao in restricoes:
            tipo_restricao = remover_namespace(restricao, ns)

            if tipo_restricao == 'pattern':
                expressao = restricao.get('value')

                if tamanho == '':
                    if '}|\\' in expressao:
                        quantidade = 0
                        for detalhe in expressao.split('|'):
                            tamanho += detalhe[3:-1].replace(',', '-') + ' ou '
                            quantidade += 1

                        tamanho = tamanho[:-4]
                        # substituir 'ou' intermediário por vírgula
                        if quantidade > 2:
                            tamanho = tamanho.replace(' ou ', ', ', quantidade - 2)
                    elif ',' in expressao and (expressao.startswith(r'\d{') or expressao.startswith(r'\w{')):
                        tamanho = expressao[3:-1].replace(',', '-')
                    elif expressao == r'\d' or expressao == r'\w':
                        tamanho = '1'
                    elif expressao.startswith(r'\d{') or expressao.startswith(r'\w{'):
                        tamanho = expressao[3:-1].replace(',', '-')

            if tipo_restricao == 'enumeration':
                valor = restricao.get('value')

                if tamanho == '':
                    tamanho_minimo = len(valor)
                    tamanho_maximo = tamanho_minimo
                else:
                    tamanho_local = len(valor)
                    tamanho_minimo = min(tamanho_minimo, tamanho_local)
                    tamanho_maximo = max(tamanho_maximo, tamanho_local)

                if tamanho_minimo == tamanho_maximo:
                    tamanho = str(tamanho_minimo)
                else:
                    tamanho = '{}-{}'.format(str(tamanho_minimo), str(tamanho_maximo))

                detalhe = restricao.findall('base:annotation', ns)

                if detalhe is not None and len(detalhe) > 0:
                    if len(detalhe[0]) == 1:
                        valores_validos.append((valor, detalhe[0][0].text))
                    else:
                        valores_validos.append((None, detalhe[0][0].text))
                        valores_validos.append((valor, detalhe[0][1].text))
                else:
                    valores_validos.append((valor, None))

            elif tipo_restricao == 'length':
                tamanho = restricao.get('value')

            elif tipo_restricao == 'minLength':
                tamanho = restricao.get('value') + '-' + tamanho

            elif tipo_restricao == 'maxLength':
                tamanho = tamanho + '-' + restricao.get('value')

            elif tipo_restricao == 'totalDigits':
                tamanho = '1-' + restricao.get('value')

            elif tipo_restricao == 'fractionDigits':
                decimais = restricao.get('value')

        if tamanho.startswith('--'):
            tamanho = '0-' + tamanho[2:]
        elif tamanho.endswith('--'):
            tamanho = tamanho[:-2] + '-...'
        else:
            tamanho = tamanho.replace('--', '-')

    else:
        descricao = elemento.findall('base:annotation', ns)
        tipo = elemento.get('type')
        if converter_tipo(tipo) == 'D':
            tamanho = '-'

    if descricao is not None:
        descricao, _, _ = imprimir_descricao(descricao, resumo, caminho_completo + pai.get('name') + '_' if not caminho_completo.endswith(pai.get('name') + '_') else caminho_completo)

    if len(valores_validos) > 0:
        descricao_valores = '<br />\n<strong>Valores válidos:</strong>'

        if valores_validos[0][1] is not None:
            for indice, valor in enumerate(valores_validos):
                if valor[0] is None:
                    if indice > 0:
                        descricao_valores += '<br />\n'

                    descricao_valores += '<br />\n{}'.format(valor[1])
                else:
                    descricao_valores += '<br />\n<strong>{}</strong> - {}'.format(valor[0], embutir_links(valor[1], False, caminho_completo))
        else:
            descricao_valores += ' {}'.format(', '.join([x[0] for x in valores_validos]))

        if '__VALORES_VALIDOS__' in descricao:
            descricao = descricao.replace('__VALORES_VALIDOS__', descricao_valores)
        else:
            descricao += descricao_valores

    descricao = descricao.replace('__VALORES_VALIDOS__', '')

    texto_pai = '<a href="#resumo_{}:{}">{}</a>'.format(evento, pai.get('name').lower(), pai.get('name')) if 'name' in pai.attrib else ''

    if tamanho == '':
        tamanho = '-'

    if tamanho_especial is not None:
        tamanho = tamanho_especial

    return molde_completo.format(
        indice=indice_completo,
        caminho=caminho,
        grupo_campo='<span id=\'{}:{}\'>{}</span>'.format(evento, nome.lower(), nome),
        pai=texto_pai,
        tipo_elemento=tipo_elemento,
        tipo=converter_tipo(tipo),
        ocorrencia=imprimir_ocorrencia(elemento),
        tamanho=tamanho,
        decimais=decimais,
        descricao=descricao)


def imprimir_ocorrencia(elemento, choice=False):
    if choice:
        return '0-1'

    if 'minOccurs' not in elemento.attrib and 'maxOccurs' not in elemento.attrib:
        return '1'

    elif 'minOccurs' in elemento.attrib and 'maxOccurs' not in elemento.attrib:
        return elemento.get('minOccurs') + '-1'

    elif 'minOccurs' in elemento.attrib and 'maxOccurs' in elemento.attrib:
        return elemento.get('minOccurs') + '-' + elemento.get('maxOccurs').replace('unbounded', 'N')

    elif 'minOccurs' not in elemento.attrib and 'maxOccurs' in elemento.attrib:
        return '1-' + elemento.get('maxOccurs').replace('unbounded', 'N')

    else:
        return '?'


def aplicar_formatacao(texto):
    return re.sub('##(.*?)##', '<b>\\1</b>', re.sub('__(.*?)__', '<i>\\1</i>', texto))


def embutir_links_tabelas(texto):
    return re.sub(r'(Tabela \d{2})', '<a href="tabelas.html#\\1">\\1</a>', texto)


def embutir_links(texto, chave, caminho_completo):
    texto = embutir_links_tabelas(texto)

    for ocorrencia in re.findall(r'\{.*?\}', texto):
        tamanho_texto = len(texto)

        posicao_identificador = texto.find(ocorrencia)
        tamanho_identificador = len(ocorrencia)

        identificador = ocorrencia[1:-1]

        if chave:
            texto = texto = texto.replace(ocorrencia, '<a href="#{}">{}</a>'.format(caminho_completo + identificador, identificador))
        else:
            if tamanho_texto > posicao_identificador + tamanho_identificador:
                subtexto = texto[posicao_identificador + tamanho_identificador:]
                caminho = re.search(r'\(.*?\)', subtexto)

                if caminho is not None and subtexto.find(caminho.group(0)) == 0:
                    caminho_final = caminho.group(0)[1:-1]

                    if caminho.group(0).startswith('(./'):
                        caminho_final = caminho_completo + caminho_final[2:]

                    if caminho.group(0).startswith('(/'):
                        caminho_final = caminho_completo[0:5] + caminho_final[1:]

                    if caminho.group(0).startswith('(../'):
                        caminho_final = tratar_caminho_relativo(ocorrencia,  '(' + caminho.group(0)[4:], caminho_completo[0:caminho_completo[:-1].rfind('_') + 1])

                    texto = texto.replace(ocorrencia, '<a href="#{}">{}</a>'.format(caminho_final, identificador), 1).replace(caminho.group(0), '',1)
                else:
                    texto = texto.replace(ocorrencia, '[[[{}]]]'.format(ocorrencia[1:-1]), 1)

    texto = re.sub('(Validação:|Origem:|Evento de origem:)', r'<strong>\1</strong>', texto)

    return texto.replace('[[[', '{').replace(']]]', '}')


def tratar_caminho_relativo(rotulo, caminho, caminho_completo):
    if caminho.startswith('(../'):
        return tratar_caminho_relativo(rotulo, '(' + caminho[4:], caminho_completo[0:caminho_completo[:-1].rfind('_') + 1])
    else:
        return caminho_completo + caminho[1:-1]


def substituir_entidades_html(texto):
    return texto.replace('"', '&quot;').replace('>', '&gt;').replace('<', '&lt;')


def imprimir_descricao(elemento_annotation, resumo, caminho_completo):
    descricao = '-'
    chave = '-'
    condicao = 'O'

    if len(elemento_annotation) > 0:
        descricao = embutir_links(substituir_entidades_html(elemento_annotation[0][0].text), False, caminho_completo)

        if resumo:
            descricao = descricao.rstrip('.')

        numero_regras = 0

        ocorreu_descricao_completa = False

        for doc in elemento_annotation[0][1:]:
            if numero_regras > 0 and 'REGRA:' not in doc.text:
                raise Exception('REGRA deve ser o último item')

            if 'CHAVE_GRUPO' in doc.text:
                if resumo:
                    chave = embutir_links(doc.text.replace('CHAVE_GRUPO:', ''), True, caminho_completo).strip()
                else:
                    pass
            elif 'CONDICAO_GRUPO' in doc.text:
                if resumo:
                    condicao = doc.text.replace('CONDICAO_GRUPO:', '').strip()

                    if ';' not in condicao:
                        condicao = embutir_links(substituir_entidades_html(condicao), False, caminho_completo)
                    else:
                        condicao_composta = ''

                        for item_condicao in condicao.split(';'):
                            condicao_composta += embutir_links(substituir_entidades_html(item_condicao.strip()), False, caminho_completo) + ';<br />\n'

                        condicao = condicao_composta[:-8]
                else:
                    pass
            elif 'DESCRICAO_COMPLETA' in doc.text:
                if resumo:
                    ocorreu_descricao_completa = True
                    continue
                else:
                    descricao = embutir_links(substituir_entidades_html(doc.text.replace('DESCRICAO_COMPLETA:', '')), False, caminho_completo)
            elif 'REGRA:' in doc.text:
                if resumo:
                    continue
                else:
                    identificador_regra = doc.text[6:]

                    if identificador_regra not in regras:
                        raise Exception('{} não definida'.format(identificador_regra))

                    if numero_regras == 0:
                        descricao += '<br />\n__ROTULO__'

                    numero_regras += 1

                    descricao += '<br />\n' + '<a href="#{}">{}</a>'.format(identificador_regra.lower(), identificador_regra)
            else:
                if not resumo or not ocorreu_descricao_completa:
                    if 'Validação:' in doc.text and '__VALORES_VALIDOS__' not in descricao:
                        descricao += '__VALORES_VALIDOS__'

                    descricao += '<br />\n' + embutir_links(substituir_entidades_html(doc.text), False, caminho_completo)

        if numero_regras == 1:
            descricao = descricao.replace('__ROTULO__', '<strong>Regra de validação:</strong>')
        elif numero_regras > 1:
            descricao = descricao.replace('__ROTULO__', '<strong>Regras de validação:</strong>')

    return descricao, chave, condicao


def navegar(raiz, elemento, pai, ns, indice, resumo, tipos_usados, tipo_usado, evento, choice, indice_completo, caminho_completo, numero):
    linhas = []
    titulo = ''

    if caminho_completo == evento + '_':
        caminho_completo = numero + '_'

    id = elemento.find('base:attribute', ns)
    if id is not None and id.attrib['name']:
        if not resumo:
            linhas.append(imprimir_elemento(id, pai, ns, raiz, resumo, evento, indice_completo, caminho_completo))
            indice_completo += 1

    for filho in elemento:
        tipo = remover_namespace(filho, ns)

        elemento_tem_choice = tipo == "choice"

        if tipo == 'element':
            if 'ref' in filho.attrib:
                continue
            elif 'type' in filho.attrib and filho.attrib['type'].startswith('TS_'):
                if not resumo:
                    linhas.append(imprimir_elemento(filho, pai, ns, raiz, resumo, evento, indice_completo, caminho_completo))
                    indice_completo += 1
                continue
            elif len(filho) > 0 and (filho[0].tag.endswith('simpleType') or ('type' in filho.attrib and filho.attrib['type'].startswith('xs:'))):
                if not resumo:
                    linhas.append(imprimir_elemento(filho, pai, ns, raiz, resumo, evento, indice_completo, caminho_completo))
                    indice_completo += 1
                continue
            else:
                descricao = filho.findall('base:annotation', ns)

                # elemento agrupador usa tipo e deve herdar sua documentação
                if len(descricao) == 0 and 'type' in filho.attrib and filho.get('type').startswith('T_'):
                    nome = filho.get('type')

                    tipos_locais = raiz.findall('base:complexType', ns)
                    for tipo_local in tipos_locais:
                        if tipo_local.get('name') == nome:
                            descricao = tipo_local.findall('base:annotation', ns)
                            break

                    if len(descricao) == 0:
                        descricao = tipos_include[nome].findall('base:annotation', ns)

                if len(descricao) == 0:
                    raise Exception('Cacildis!')

                caminho_atual = caminho_completo + filho.get('name') + '_'

                if resumo and 'name' in filho.attrib and 'type' in filho.attrib and filho.attrib['type'] in tipos_usados:
                    caminho_completo = tipos_usados[filho.attrib['type']][2]
                    caminho_atual = caminho_completo

                descricao, chave, condicao = imprimir_descricao(descricao, resumo, caminho_atual if filho.get('name') != evento else numero + '_')
                descricao = descricao.replace('__VALORES_VALIDOS__', '')

                if indice == 1:
                    titulo = descricao
                    numero = descricao[2:6]
                    descricao = 'eSocial'

                texto_pai = '<a href="#resumo_{}:{}">{}</a>'.format(evento, pai.get('name').lower(), pai.get('name')) if 'name' in pai.attrib else ''

                if resumo:
                    if 'name' in filho.attrib and 'type' in filho.attrib and filho.attrib['type'] in tipos_usados:
                        conteudo, _, indice_completo = tratar_tipo(raiz, filho.get('type'), filho, ns, indice + 1, resumo, tipos_usados, evento, indice_completo, caminho_completo, numero)
                        grupo = '<span id=\'resumo_{evento}:{idPai}_{id}\'><a href="#{evento}:{idPai}_{id}">{nome}</a></span>'.format(evento=evento, idPai=pai.get('name').lower(), id=filho.get('name').lower(), nome=filho.get('name'))
                    else:
                        grupo = '<span id=\'resumo_{evento}:{id}\'><a href="#{evento}:{id}">{nome}</a></span>'.format(evento=evento, id=filho.get('name').lower(), nome=filho.get('name'))

                    linhas.append(molde_resumo.format(grupo=grupo,pai=texto_pai,nivel=indice,descricao=descricao,ocorrencia=imprimir_ocorrencia(filho, choice),chave=chave,condicao=condicao))

                    # só adiciona referência a definição anterior do tipo se ele tiver grupos filhos
                    if 'name' in filho.attrib and 'type' in filho.attrib and filho.attrib['type'] in tipos_usados and len(conteudo) > 0:
                        linhas.append(molde_resumo.format(grupo='...',pai='',nivel='',descricao='<strong>Ver:</strong> <a href="#resumo_{}:{}">{}</a> &gt; <a href="#resumo_{}:{}">{}</a>'.format(evento, tipos_usados[filho.attrib['type']][0].lower(), tipos_usados[filho.attrib['type']][0], evento, tipos_usados[filho.attrib['type']][1].lower(), tipos_usados[filho.attrib['type']][1]),ocorrencia='',chave='',condicao=''))
                else:
                    if 'name' in filho.attrib and 'type' in filho.attrib and filho.attrib['type'] in tipos_usados:
                        grupo = '<span data-tipo="grupo" id=\'{evento}:{idPai}_{id}\'><a href="#resumo_{evento}:{idPai}_{id}">{nome}</a></span>'.format(evento=evento, idPai=pai.get('name').lower(), id=filho.get('name').lower(), nome=filho.get('name'))
                    else:
                        grupo = '<span data-tipo="grupo" id=\'{evento}:{id}\'><a href="#resumo_{evento}:{id}">{nome}</a></span>'.format(evento=evento, id=filho.get('name').lower(), nome=filho.get('name'))

                    linhas.append(molde_completo.format(indice=indice_completo,caminho=(caminho_completo + filho.get('name')) if filho.get('name') != evento else numero,grupo_campo=grupo,pai=texto_pai,tipo_elemento='G',tipo='-',ocorrencia=imprimir_ocorrencia(filho, choice),tamanho='-',decimais='-',descricao=descricao))

                    if 'name' in filho.attrib and 'type' in filho.attrib and filho.attrib['type'] in tipos_usados:
                        linhas.append(molde_completo.format(indice='...',caminho='',grupo_campo='',pai='',tipo_elemento='',tipo='',ocorrencia='',tamanho='',decimais='',descricao='<strong>Ver:</strong> <a href="#{}:{}">{}</a> &gt; <a href="#{}:{}">{}</a>'.format(evento, tipos_usados[filho.attrib['type']][0].lower(), tipos_usados[filho.attrib['type']][0], evento, tipos_usados[filho.attrib['type']][1].lower(), tipos_usados[filho.attrib['type']][1])))

                    indice_completo += 1

            if 'name' in filho.attrib and 'type' in filho.attrib:
                if filho.attrib['type'] not in tipos_usados:
                    conteudo, _, indice_completo = tratar_tipo(raiz, filho.get('type'), filho, ns, indice + 1, resumo, tipos_usados, evento, indice_completo, caminho_completo, numero)
                    linhas += conteudo

                if filho.attrib['type'] not in tipos_usados:
                    tipos_usados[filho.attrib['type']] = (pai.attrib['name'], filho.attrib['name'], caminho_completo + filho.get('name') + '_')
            else:
                conteudo, _, indice_completo = navegar(raiz, filho, filho, ns, indice + 1, resumo, tipos_usados, tipo_usado, evento, elemento_tem_choice, indice_completo, (caminho_completo + filho.get('name') + '_') if filho.get('name') != 'eSocial' else caminho_completo, numero)

                # Pesquisa para tentar identificar se o elemento contém choice
                elemento_complexType = filho.find("base:complexType", ns)
                if elemento_complexType is not None:
                    elemento_sequence = elemento_complexType.find("base:sequence", ns)
                    if elemento_sequence is not None:
                        elemento_choice = elemento_sequence.find("base:choice", ns)
                        if elemento_choice is not None:
                            ultima_linha = linhas[len(linhas) - 1].replace(">G<", ">CG<").replace('data-tipo="grupo"', 'data-tipo="grupo-choice"')
                            linhas[len(linhas) - 1] = ultima_linha

                linhas += conteudo

        elif tipo == 'sequence' or tipo == 'choice'or (tipo == 'complexType' and remover_namespace(elemento, ns) != 'schema'):
            conteudo, _, indice_completo = navegar(raiz, filho, pai, ns, indice, resumo, tipos_usados, tipo_usado, evento, elemento_tem_choice, indice_completo, caminho_completo, numero)
            linhas += conteudo

    return linhas, titulo, indice_completo

caminho_projeto = os.getcwd() + '\\'

molde_resumo = '<tr>\n<td style="text-align:center">{grupo}</td>\n<td style="text-align:center">{pai}</td>\n<td style="text-align:center">{nivel}</td>\n<td>{descricao}</td>\n<td style="text-align:center">{ocorrencia}</td>\n<td style="text-align:center">{chave}</td>\n<td style="text-align:center">{condicao}</td>\n</tr>\n'

molde_completo = '<tr>\n<td style="text-align:center; cursor:copy" onclick="copiarCaminho(\'{caminho}\')"><span class="has-tooltip-right" data-tooltip="{caminho}" id="{caminho}">{indice}</span></td>\n<td style="text-align:center">{grupo_campo}</td>\n<td style="text-align:center">{pai}</td>\n<td style="text-align:center">{tipo_elemento}</td>\n<td style="text-align:center">{tipo}</td>\n<td style="text-align:center">{ocorrencia}</td>\n<td style="text-align:center">{tamanho}</td>\n<td style="text-align:center">{decimais}</td>\n<td style="text-align:left">{descricao}</td>\n</tr>\n'

molde_regra_modal = '<div class="modal" id="{identificador}">\n<div class="modal-background"></div>\n<div class="modal-card">\n<header class="modal-card-head">\n<p class="modal-card-title">{identificador}</p>\n<button class="delete" aria-label="close"></button>\n</header>\n<section class="modal-card-body">\n<p>{texto}</p>\n</section>\n</div>\n</div>\n'

molde_regra = '<td id={id}><strong>{identificador}</strong></td>\n<td>{texto}</strong></td>\n</tr>\n'

tipos_include = {}

larguras_resumo = [14, 14, 14, 14, 14, 14, 14]

larguras_completo = [11, 11, 11, 11, 11, 11, 11, 11, 11]

ns = {'base': 'http://www.w3.org/2001/XMLSchema'}
raiz_include = ET.parse(caminho_projeto + 'tipos.xsd').getroot()
for tipo in raiz_include.findall('base:simpleType', ns):
    tipos_include[tipo.get('name')] = tipo

for tipo in raiz_include.findall('base:complexType', ns):
    tipos_include[tipo.get('name')] = tipo

eventos = [
    'evtInfoEmpregador', 'evtTabEstab', 'evtTabRubrica', 'evtTabLotacao', 'evtTabProcesso',
    'evtRemun', 'evtRmnRPPS', 'evtBenPrRP', 'evtPgtos', 'evtComProd', 'evtContratAvNP', 'evtInfoComplPer', 'evtReabreEvPer', 'evtFechaEvPer',
    'evtAdmPrelim', 'evtAdmissao', 'evtAltCadastral', 'evtAltContratual', 'evtCAT', 'evtMonit', 'evtAfastTemp', 'evtCessao', 'evtExpRisco', 'evtReintegr', 'evtDeslig',
    'evtTSVInicio', 'evtTSVAltContr', 'evtTSVTermino',
    'evtCdBenefIn', 'evtCdBenefAlt', 'evtCdBenIn', 'evtCdBenAlt', 'evtReativBen', 'evtCdBenTerm',
    'evtExclusao',
    'evtBasesTrab', 'evtIrrfBenef', 'evtBasesFGTS', 'evtCS', 'evtFGTS']
#eventos = ['evtIrrfBenef']

# TODO
# conferir caminhos usados em links

regras = {}

identificador_regra = None
texto_regra = ''

with io.open(caminho_projeto + 'regras.txt', 'r', encoding='utf8') as arquivo_regras:
    for linha in arquivo_regras:
        if linha.rstrip() == '':
            regras[identificador_regra] = texto_regra.rstrip('\n')
            identificador_regra = None
            texto_regra = ''
        elif linha.startswith('REGRA_'):
            identificador_regra = linha.strip()
        elif identificador_regra is not None:
            if 'REGRA_' in linha:
                ocorrencias = list(re.finditer('REGRA_', linha))

                if len(ocorrencias) > 1:
                    ocorrencias.reverse()

                for ocorrencia in ocorrencias:
                    inicio = ocorrencia.start()
                    fim = sys.maxsize

                    for delimitador in ' ,.:;':
                        fim_delimitador =linha[inicio:].find(delimitador)

                        if fim_delimitador > 0 and fim_delimitador < fim:
                            fim = fim_delimitador

                    identificador_regra_interna = linha[inicio:inicio + fim]

                    linha = linha.replace(identificador_regra_interna, '<a href="#{id}">{nome}</a>'.format(id=identificador_regra_interna.lower(), nome=identificador_regra_interna))

            texto_regra += linha

if identificador_regra is not None:
    regras[identificador_regra] = texto_regra.rstrip('\n')

# Tabelas
referencias_tabelas = []

with io.open('doc\\tabelas.html', 'w', encoding='utf8') as f:
    with io.open('doc\\inicio.html', 'r', encoding='utf8') as inicio:
        f.write(inicio.read().replace('{}', 'Tabelas'))

    f.write('<h1 class="title has-text-centered is-1">Tabelas</h1>\n')

    conteudo = ''
    indice = ''

    for tabela in sorted(os.listdir(caminho_projeto + 'tabelas\\')):
        texto_tabela=[]
        anexos_tabela = []

        with io.open(caminho_projeto + 'tabelas\\' + tabela, 'r', encoding=' utf8 ') as arquivo_tabela:
            rowspan_linha={}

            fim_da_tabela = False
            texto_largura_fixa = False

            for indice_linha, linha in enumerate(arquivo_tabela):
                if '__' in linha:
                    linha = aplicar_formatacao(linha)

                itens_linha = []

                if linha.rstrip() == '===':
                    fim_da_tabela = True
                    continue
                elif fim_da_tabela:
                    if (linha.startswith('>')):
                        if not texto_largura_fixa:
                            anexos_tabela.append('<pre>{}'.format(linha.rstrip()[1:]))
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
                                itens_linha.append('<td class="grupo" style="text-align: center; font-weight: bold;" rowspan="" colspan="">{}</td>'.format(item))
                        else:
                            if item.startswith('^'):
                                itens_linha.append('')
                                rowspan_linha[indice_item] += 1
                            elif item.startswith('>'):
                                itens_linha.append('')
                                extensao_colspan += 1

                                if rowspan_linha[indice_item] > 0:
                                    texto_tabela[indice_linha - rowspan_linha[indice_item] - 2][indice_item] = texto_tabela[indice_linha - rowspan_linha[indice_item] - 2][indice_item].replace('rowspan=""', 'rowspan="{}"'.format(rowspan_linha[indice_item] + 1))
                                    rowspan_linha[indice_item] = 0

                            else:
                                if extensao_colspan != 0:
                                    itens_linha[indice_item - extensao_colspan - 1] = itens_linha[indice_item - extensao_colspan - 1].replace('colspan=""', 'colspan="{}"'.format(extensao_colspan + 1))
                                    extensao_colspan = 0

                                if rowspan_linha[indice_item] > 0:
                                    texto_tabela[indice_linha - rowspan_linha[indice_item] - 2][indice_item] = texto_tabela[indice_linha - rowspan_linha[indice_item] - 2][indice_item].replace('rowspan=""', 'rowspan="{}"'.format(rowspan_linha[indice_item] + 1))

                                rowspan_linha[indice_item] = 0

                                itens_linha.append('<td rowspan="" colspan="">{}</td>'.format(item))

                    if extensao_colspan > 0:
                        itens_linha[indice_item - extensao_colspan] = itens_linha[indice_item - extensao_colspan].replace('colspan=""', 'colspan="{}"'.format(extensao_colspan + 1))

                texto_tabela.append(itens_linha)

            for i in range(indice_item):
                if rowspan_linha[i] > 0:
                    texto_tabela[indice_linha - rowspan_linha[i] - 1][i] = texto_tabela[indice_linha - rowspan_linha[i] - 1][i].replace('rowspan=""', 'rowspan="{}"'.format(rowspan_linha[i] + 1))

            conteudo += '<table id="Tabela {}" style="margin-top: 48px;" class="table is-fullwidth is-bordered">\n'.format(tabela[:-4])
            conteudo += '<thead><tr><th style="text-align: center" colspan="{}">Tabela {} - {}</th></tr></thead>\n'.format(indice_item + 1, tabela[:-4], titulo)
            conteudo += '<tbody>\n'

            referencias_tabelas.append('Tabela {}'.format(tabela[:-4]))

            for indice_linha, linha in enumerate(texto_tabela):
                conteudo += '<tr class="grupo">\n'if 'class="grupo"' in linha[0] else '<tr>\n'

                for item in linha:
                    if item != '':
                        conteudo += item.replace(' rowspan=""', '').replace(' colspan=""', '') + '\n'

                conteudo += '</tr>\n'

            conteudo += '</tbody>\n'
            conteudo += '</table>\n'

            if len(anexos_tabela) > 0:
                conteudo += '<article class="message is-small">\n<div class="message-body">\n'
                for anexo in anexos_tabela:
                    conteudo += anexo + '\n'
                conteudo += '</div>\n</article>\n'

            indice += '<li><a href="#Tabela {}">Tabela {} - {}</a></li>\n'.format(tabela[:-4], tabela[:-4], titulo)

    f.write('<ul>\n')
    f.write(indice)
    f.write('</ul>\n')
    f.write(conteudo)

    with io.open('doc\\fim.html', 'r', encoding='utf8') as fim:
        f.write(fim.read())

# Leiautes
tabela = []
for evento in eventos:
    raiz = ET.parse(caminho_projeto + '{}.xsd'.format(evento)).getroot()

    conteudo, titulo, indice_completo = navegar(raiz, raiz, raiz, ns, 1, resumo=True, tipos_usados={}, tipo_usado=False, evento=evento, choice=False, indice_completo=1, caminho_completo='', numero='')

    tabela.append('<h3 id="{}" class="title has-text-centered">{}</h3>\n'.format(evento, titulo))
    tabela.append('<table class="table is-fullwidth is-bordered">\n')
    tabela.append('<thead>\n')
    tabela.append('<tr>\n')
    tabela.append('<th style="text-align:center" colspan="7">Tabela de Resumo dos Registros</th>\n')
    tabela.append('</tr>\n')
    tabela.append('</thead>\n')
    tabela.append('<tbody>\n')
    tabela.append('<tr class="grupo">\n')
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Grupo</strong></td>\n'.format(larguras_resumo[0]))
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Pai</strong></td>\n'.format(larguras_resumo[1]))
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Nível</strong></td>\n'.format(larguras_resumo[2]))
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Descrição</strong></td>\n'.format(larguras_resumo[3]))
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Ocorrência</strong></td>\n'.format(larguras_resumo[4]))
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Chave</strong></td>\n'.format(larguras_resumo[5]))
    tabela.append('<td style="text-align:center; width: {}%;"><strong>Condição</strong></td>\n'.format(larguras_resumo[6]))
    tabela.append('</tr>\n')
    tabela += (conteudo)
    tabela.append('</tbody>\n')
    tabela.append('</table>\n')

    conteudo, titulo, indice_completo = navegar(raiz, raiz, raiz, ns, 1, resumo=False, tipos_usados={}, tipo_usado=False, evento=evento, choice=False, indice_completo=1, caminho_completo='', numero='')

    tabela.append('<h4 class="subtitle has-text-centered">Registros do evento {}</h4>\n'.format(titulo))
    tabela.append('<table class="table is-fullwidth is-bordered">\n')
    tabela.append('<thead>\n')
    tabela.append('<tr>\n')
    tabela.append('<th style="text-align:center; width: {}%;">#</th>\n'.format(larguras_completo[0]))
    tabela.append('<th style="text-align:center; width: {}%;">Grupo/Campo</th>\n'.format(larguras_completo[1]))
    tabela.append('<th style="text-align:center; width: {}%;">Pai</th>\n'.format(larguras_completo[2]))
    tabela.append('<th style="text-align:center; width: {}%;">Elemento</th>\n'.format(larguras_completo[3]))
    tabela.append('<th style="text-align:center; width: {}%;">Tipo</th>\n'.format(larguras_completo[4]))
    tabela.append('<th style="text-align:center; width: {}%;">Ocorrência</th>\n'.format(larguras_completo[5]))
    tabela.append('<th style="text-align:center; width: {}%;">Tamanho</th>\n'.format(larguras_completo[6]))
    tabela.append('<th style="text-align:center; width: {}%;">Decimais</th>\n'.format(larguras_completo[7]))
    tabela.append('<th style="text-align:center; width: {}%;">Descrição</th>\n'.format(larguras_completo[8]))
    tabela.append('</tr>\n')
    tabela.append('</thead>\n')
    tabela.append('<tbody>\n')
    tabela += (conteudo)
    tabela.append('</tbody>\n')
    tabela.append('</table>\n')

with io.open('doc\\index.html', 'w', encoding='utf8') as f:
    with io.open('doc\\inicio.html', 'r', encoding='utf8') as inicio:
        f.write(inicio.read().replace('{}', 'Leiautes'))

    f.write('<h1 class="title has-text-centered is-1">Leiautes</h1>')

    for regra in regras:
        f.write(molde_regra_modal.format(identificador=regra, texto=regras[regra].replace('\n', '<br />\n')))

    f.writelines(tabela)

    with io.open('doc\\fim.html', 'r', encoding='utf8') as fim:
        f.write(fim.read())

# Regras
with io.open('doc\\regras.html', 'w', encoding='utf8') as f:
    with io.open('doc\\inicio.html', 'r', encoding='utf8') as inicio:
        f.write(inicio.read().replace('{}', 'Regras'))

    f.write('<h1 class="title has-text-centered is-1">Regras de Validação</h1>')

    f.write('<table class="table is-fullwidth is-bordered">\n<thead>\n<tr><th style="text-align:center">Nome</th>\n<th style="text-align:center">Descrição</th>\n</tr>\n</thead>\n<tbody>\n')

    for regra in regras:
        f.write(molde_regra.format(id=regra.lower(), identificador=regra, texto=embutir_links_tabelas(regras[regra].replace('\n', '<br />\n'))))

    f.write('</tbody>\n</table>\n')

    with io.open('doc\\fim.html', 'r', encoding='utf8') as fim:
        f.write(fim.read())