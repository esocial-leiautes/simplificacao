class Geral:
    RODAPE_TABELA = (
        '</tbody>\n'
        '</table>\n')

    LINK = '<a href="#{}">{}</a>'


class Tabela:
    CELULA = '<td rowspan="" colspan=""{classe}>{conteudo}</td>\n'

    CELULA_CABECALHO = (
        '<td class="grupo" rowspan="" colspan=""{dimensao}>{conteudo}</td>\n')

    ANEXO = (
        '<div class="message">\n'
        '<div class="message-body">\n{}'
        '</div>\n'
        '</div>\n')

    LINHA_INDICE = (
        '<li>'
        '<a href="#{numero}">Tabela {numero} - {titulo}</a>'
        '</li>\n')

    CABECALHO = (
        '<table id="{}"'
        ' class="table is-fullwidth is-bordered tabela">\n'
        '<thead>\n'
        '<tr>\n'
        '<th colspan="{}">Tabela {} - {}</th>\n'
        '</tr>\n'
        '</thead>\n'
        '<tbody>\n')


class Regra:
    LINHA = (
        '<tr>\n'
        '<td id="{id}"><strong>{nome}</strong></td>\n'
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
        '<div class="modal-card-body">\n'
        '<p>{texto}</p>\n'
        '</div>\n'
        '</div>\n'
        '</div>\n')

    CABECALHO = (
        '<table class="table is-fullwidth is-bordered regras">\n'
        '<thead>\n'
        '<tr>\n'
        '<th>Nome</th>\n'
        '<th>Descrição</th>\n'
        '</tr>\n'
        '</thead>\n'
        '<tbody>\n')


class Resumo:
    LINHA = (
        '<tr>\n'
        '<td id="r_{link_completo}">'
        '<a href="#{link_completo}">{nome}</a>'
        '</td>\n'
        '<td>{pai}</td>\n'
        '<td>{nivel}</td>\n'
        '<td>{descricao}</td>\n'
        '<td>{ocorrencia}</td>\n'
        '<td>{chave}</td>\n'
        '<td>{condicao}</td>\n'
        '</tr>\n')

    REFERENCIA = (
        '<tr>\n'
        '<td>...</td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td><strong>Ver:</strong> '
        '<a href="#r_{id_pai}">'
        '{nome_pai}</a> &gt; '
        '<a href="#r_{id}">'
        '{nome}</a></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '</tr>\n')

    CABECALHO = (
        '\n'
        '<h3 id="{}" class="title has-text-centered">{} - {}</h3>\n'
        '<table class="table is-fullwidth is-bordered resumo">\n'
        '<thead>\n'
        '<tr>\n'
        '<th colspan="7">Tabela de Resumo dos '
        'Registros</th>\n'
        '</tr>\n'
        '</thead>\n'
        '<tbody>\n'
        '<tr class="grupo">\n'
        '<td>'
        '<strong>Grupo</strong></td>\n'
        '<td>'
        '<strong>Grupo Pai</strong></td>\n'
        '<td>'
        '<strong>Nível</strong></td>\n'
        '<td>'
        '<strong>Descrição</strong></td>\n'
        '<td>'
        '<strong>Ocor.</strong></td>\n'
        '<td>'
        '<strong>Chave</strong></td>\n'
        '<td>'
        '<strong>Condição</strong></td>\n'
        '</tr>\n')


class Completo:
    LINHA = (
        '<tr{marcador_grupo}>\n'
        '<td onclick="copiarCaminho.call(this)"'
        ' title="{caminho}"'
        ' id="{caminho}">{indice}</td>\n'
        '<td>'
        '{nome}'
        '</td>\n'
        '<td>{pai}</td>\n'
        '<td>{tipo_elemento}</td>\n'
        '<td>{tipo}</td>\n'
        '<td>{ocorrencia}</td>\n'
        '<td>{tamanho}</td>\n'
        '<td>{decimais}</td>\n'
        '<td>{descricao}</td>\n'
        '</tr>\n')

    REFERENCIA = (
        '<tr>\n'
        '<td>...</td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td></td>\n'
        '<td><strong>Ver:</strong> '
        '<a href="#{id_pai}">{nome_pai}</a> &gt; '
        '<a href="#{id}">{nome}</a></td>\n'
        '</tr>\n')

    CABECALHO = (
        '\n'
        '<h4 class="subtitle has-text-centered">'
        'Registros do evento {} - {}</h4>\n'
        '<table class="table is-fullwidth is-bordered completo">\n'
        '<thead>\n'
        '<tr>\n'
        '<th>#</th>\n'
        '<th>Grupo/Campo</th>\n'
        '<th>Grupo Pai</th>\n'
        '<th>Elem.</th>\n'
        '<th>Tipo</th>\n'
        '<th>Ocor.</th>\n'
        '<th>Tamanho</th>\n'
        '<th>Dec.</th>\n'
        '<th>Descrição</th>\n'
        '</tr>\n'
        '</thead>\n'
        '<tbody>\n')
