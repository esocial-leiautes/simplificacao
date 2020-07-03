class Geral:
    RODAPE_TABELA = (
            '</tbody>\n'
            '</table>\n')

    LINK = '<a href="#{}">{}</a>'


class Tabela:
    CELULA = '<td rowspan="" colspan="">{}</td>'

    CELULA_CABECALHO = (
        '<td class="grupo" style="text-align: center; font-weight: bold;"'
        ' rowspan="" colspan="">{}</td>')

    ANEXO = (
        '<article class="message is-small">\n'
        '<div class="message-body">\n{}</div>\n'
        '</article>\n')

    LINHA_INDICE = (
        '<li>'
        '<a href="#Tabela {numero}">Tabela {numero} - {titulo}</a>'
        '</li>\n')

    CABECALHO = (
        '<table id="Tabela {}" style="margin-top: 48px;"'
        ' class="table is-fullwidth is-bordered">\n'
        '<thead>'
        '<tr>'
        '<th style="text-align: center" colspan="{}">Tabela {} - {}</th>'
        '</tr>'
        '</thead>\n'
        '<tbody>\n')


class Regra:
    LINHA = (
        '<tr>\n'
        '<td id={id}><strong>{nome}</strong></td>\n'
        '<td>{texto}</td>\n'
        '</tr>\n')

    LINHA_MODAL = (
        '<div class="modal" id="{nome}">\n'
        '<div class="modal-background"></div>\n'
        '<div class="modal-card">\n'
        '<header class="modal-card-head">\n'
        '<p class="modal-card-title">{nome}</p>\n'
        '<button class="delete" aria-label="close"></button>\n'
        '</header>\n'
        '<section class="modal-card-body">\n'
        '<p>{texto}</p>\n'
        '</section>\n'
        '</div>\n'
        '</div>\n')

    CABECALHO = (
        '<table class="table is-fullwidth is-bordered">\n'
        '<thead>\n'
        '<tr>'
        '<th style="text-align:center">Nome</th>\n'
        '<th style="text-align:center">Descrição</th>\n'
        '</tr>\n'
        '</thead>\n'
        '<tbody>\n')


class Resumo:
    LINHA = (
            '<tr>\n'
            '<td style="text-align:center">'
            '<span id="resumo_{identificador_evento}:{id_nome}">'
            '<a href="#{identificador_evento}:{id_nome}">{nome}</a>'
            '</span></td>\n'
            '<td style="text-align:center">{pai}</td>\n'
            '<td style="text-align:center">{nivel}</td>\n'
            '<td>{descricao}</td>\n'
            '<td style="text-align:center">{ocorrencia}</td>\n'
            '<td style="text-align:center">{chave}</td>\n'
            '<td style="text-align:center">{condicao}</td>\n'
            '</tr>\n')

    REFERENCIA = (
            '<tr>\n'
            '<td style="text-align:center">...</td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td><strong>Ver:</strong> '
            '<a href="#resumo_{identificador_evento}:{id_pai}">'
            '{nome_pai}</a> &gt; '
            '<a href="#resumo_{identificador_evento}:{id}">'
            '{nome}</a></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '</tr>\n')

    CABECALHO = (
            '<h3 id="{}" class="title has-text-centered">'
            '{} - {}</h3>\n'
            '<table class="table is-fullwidth is-bordered">\n'
            '<thead>\n'
            '<tr>\n'
            '<th style="text-align:center" colspan="7">Tabela de Resumo dos '
            'Registros</th>\n'
            '</tr>\n'
            '</thead>\n'
            '<tbody>\n'
            '<tr class="grupo">\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Grupo</strong></td>\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Grupo Pai</strong></td>\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Nível</strong></td>\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Descrição</strong></td>\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Ocor.</strong></td>\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Chave</strong></td>\n'
            '<td style="text-align:center; width: {}%;">'
            '<strong>Condição</strong></td>\n'
            '</tr>\n')


class Completo:
    LINHA = (
            '<tr>\n'
            '<td style="text-align:center; cursor:copy"'
            ' onclick="copiarCaminho(\'{caminho}\')">'
            '<span class="has-tooltip-right" data-tooltip="{caminho}"'
            ' id="{caminho}">{indice}</span>'
            '</td>\n'
            '<td style="text-align:center">'
            '<span{marcador_grupo} id="{evento}:{id}">'
            '{nome}'
            '</span></td>\n'
            '<td style="text-align:center">{pai}</td>\n'
            '<td style="text-align:center">{tipo_elemento}</td>\n'
            '<td style="text-align:center">{tipo}</td>\n'
            '<td style="text-align:center">{ocorrencia}</td>\n'
            '<td style="text-align:center">{tamanho}</td>\n'
            '<td style="text-align:center">{decimais}</td>\n'
            '<td style="text-align:left">{descricao}</td>\n'
            '</tr>\n')

    REFERENCIA = (
            '<tr>\n'
            '<td style="text-align:center; cursor:copy"'
            ' onclick="copiarCaminho(\'{caminho}\')">'
            '<span class="has-tooltip-right" data-tooltip="{caminho}"'
            ' id="{caminho}">...</span></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:center"></td>\n'
            '<td style="text-align:left"><strong>Ver:</strong> '
            '<a href="#{identificador_evento}:{id_pai}">{nome_pai}</a> &gt; '
            '<a href="#{identificador_evento}:{id}">{nome}</a></td>\n'
            '</tr>\n')

    CABECALHO = (
            '<h4 class="subtitle has-text-centered">'
            'Registros do evento {} - {}</h4>\n'
            '<table class="table is-fullwidth is-bordered">\n'
            '<thead>\n'
            '<tr>\n'
            '<th style="text-align:center; width: {}%;">#</th>\n'
            '<th style="text-align:center; width: {}%;">Grupo/Campo</th>\n'
            '<th style="text-align:center; width: {}%;">Grupo Pai</th>\n'
            '<th style="text-align:center; width: {}%;">Elem.</th>\n'
            '<th style="text-align:center; width: {}%;">Tipo</th>\n'
            '<th style="text-align:center; width: {}%;">Ocor.</th>\n'
            '<th style="text-align:center; width: {}%;">Tamanho</th>\n'
            '<th style="text-align:center; width: {}%;">Dec.</th>\n'
            '<th style="text-align:center; width: {}%;">Descrição</th>\n'
            '</tr>\n'
            '</thead>\n'
            '<tbody>\n')
