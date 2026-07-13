# Sales Analytics Dashboard

Dashboard interativo de análise de vendas construído com **Dash (Plotly)** e **Dash Bootstrap Components**. A aplicação lê um dataset de vendas, faz a limpeza/transformação dos dados e exibe uma tela única (single-page) com *big numbers*, gráficos de barras, linhas e pizza, além de filtros dinâmicos por **mês** e por **equipe** e alternância de tema claro/escuro.

> Projeto baseado no material da [Asimov Academy](https://asimov.academy/). Autor: **Luiz Reis**.

---

## Índice

- [Visão geral](#visão-geral)
- [Estrutura do repositório](#estrutura-do-repositório)
- [O dataset](#o-dataset)
- [Como executar](#como-executar)
- [Passo a passo do código (`app.py`)](#passo-a-passo-do-código-apppy)
  - [1. Imports e configuração](#1-imports-e-configuração-do-app)
  - [2. Estilos e temas](#2-estilos-e-temas)
  - [3. Leitura do dataset](#3-leitura-do-dataset)
  - [4. Transformação dos dados](#4-transformação-dos-dados-etl)
  - [5. Opções dos filtros](#5-opções-dos-filtros)
  - [6. Funções auxiliares](#6-funções-auxiliares)
  - [7. Layout](#7-layout)
  - [8. Callbacks (a lógica reativa)](#8-callbacks-a-lógica-reativa)
  - [9. Execução do servidor](#9-execução-do-servidor)
- [O notebook de limpeza (`cleaning_data.ipynb`)](#o-notebook-de-limpeza-cleaning_dataipynb)
- [Observações e possíveis melhorias](#observações-e-possíveis-melhorias)

---

## Visão geral

A aplicação é um painel de **inteligência comercial** que responde perguntas como:

- Qual foi o **valor total** vendido no período/equipe filtrados?
- Quem é o **consultor** e a **equipe** que mais venderam (e quanto acima da média)?
- Qual o volume de **chamadas realizadas** por dia e por mês?
- Como as vendas se distribuem **entre as equipes** e **ao longo dos meses**?
- Qual **meio de propaganda** converte mais valor?
- Qual a proporção de pagamentos **pagos vs. não pagos**?

Todo o painel é reativo: ao mudar um filtro ou o tema, os 12 gráficos são recalculados via *callbacks*.

---

## Estrutura do repositório

| Arquivo | Descrição |
|---|---|
| `app.py` | Aplicação Dash completa: ETL, layout e callbacks. É o coração do projeto. |
| `dataset_asimov.csv` | Base de dados de vendas (1.237 linhas, 12 colunas). |
| `cleaning_data.ipynb` | Notebook exploratório usado para prototipar a limpeza dos dados e os gráficos antes de portá-los para o `app.py`. |
| `4.2.0` | Arquivo gerado acidentalmente — é o **log de saída de um `pip install`** (matplotlib/nbformat). Não faz parte do projeto e pode ser removido. |

---

## O dataset

`dataset_asimov.csv` — **1.237 registros**, cada linha representa uma venda/atendimento:

| Coluna | Tipo original | Descrição |
|---|---|---|
| `Status de Pagamento` | texto (`Pago`/`Não pago`) | Se a venda foi paga. |
| `Dia` | inteiro (1–31) | Dia do mês da venda. |
| `Mês` | texto (`Jan`…`Dez`) | Mês da venda. |
| `Meio de Propaganda` | texto | Canal de aquisição: `Televisão`, `Website`, `Facebook`, `WhatsApp`, `Google Ad`, `Youtube`. |
| `Valor Pago` | texto (`R$ 7000000`) | Valor da venda em reais. |
| `Chamadas Realizadas` | inteiro | Quantidade de chamadas feitas. |
| `Duração da chamada` | texto (`02:00`) | Duração — **não utilizada** no dashboard. |
| `Modelo de Treinamento` | texto | Ex.: `GK`, `BE`, `CNI`, `FC` (tem valores nulos). |
| `Nivel de Treinamento` | texto | Ex.: `Fndn. L5`. |
| `Código de Área` | texto | Ex.: `A7`, `B13`. |
| `Equipe` | texto | `Equipe 1` a `Equipe 4`. |
| `Consultor` | texto | 16 consultores distintos. |

---

## Como executar

**Pré-requisitos:** Python 3.9+.

1. Instale as dependências:

```bash
pip install dash dash-bootstrap-components dash-bootstrap-templates plotly pandas
```

2. Execute a aplicação:

```bash
python app.py
```

3. Abra o navegador em **http://127.0.0.1:8050**.

> A app roda com `debug=True`, então recarrega automaticamente ao salvar alterações. Não use esse modo em produção.

---

## Passo a passo do código (`app.py`)

### 1. Imports e configuração do app

```python
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO
import dash
```

- `dash` / `html` / `dcc` — framework e componentes de UI (HTML e gráficos).
- `dash_bootstrap_components (dbc)` — grid responsivo e componentes estilizados com Bootstrap.
- `plotly.express (px)` / `plotly.graph_objects (go)` — criação dos gráficos.
- `pandas` — manipulação dos dados.
- `ThemeSwitchAIO` — componente pronto que fornece o **botão de troca de tema** claro/escuro.

```python
FONT_AWESOME = ['https://use.fontawesome.com/releases/v5.10.2/css/all.css']
app = dash.Dash(__name__, external_stylesheets=FONT_AWESOME)
app.scripts.config.serve_locally = True
server = app.server
```

Cria a aplicação Dash, carrega a folha de estilos do **Font Awesome** (para o ícone da balança no cabeçalho) e expõe `server` — o objeto WSGI usado por servidores de produção (ex.: Gunicorn).

### 2. Estilos e temas

```python
tab_card = {'height': "100%"}
main_config = { ... }          # config padrão de layout dos gráficos (hover, legenda)
config_graph = {'displayModeBar': False, 'showTips': False}
template_theme1 = 'flatly'     # tema claro
template_theme2 = 'darkly'     # tema escuro
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY
```

Define os dicionários de estilo reaproveitados nos cards e gráficos e os dois **temas Bootstrap** que o `ThemeSwitchAIO` alterna (`flatly` claro / `darkly` escuro). `config_graph` esconde a barra de ferramentas do Plotly, deixando os gráficos "limpos".

### 3. Leitura do dataset

```python
df = pd.read_csv("dataset_asimov.csv")
df_cru = df.copy()
```

Lê o CSV para um DataFrame e guarda uma **cópia intacta (`df_cru`)** com os valores originais — usada depois para montar os rótulos dos filtros com os nomes dos meses em texto (`Jan`, `Fev`, …).

### 4. Transformação dos dados (ETL)

Esta é a etapa de limpeza que converte texto em valores numéricos utilizáveis nos gráficos:

```python
# Meses de texto -> número ("Jan" -> "1", ..., "Dez" -> "12")
df.loc[df['Mês'] == 'Jan', 'Mês'] = "1"
...
df.loc[df['Mês'] == 'Dez', 'Mês'] = "12"

# Conversão de tipos para inteiro
df['Chamadas Realizadas'] = df['Chamadas Realizadas'].astype(int)
df['Dia'] = df['Dia'].astype(int)
df['Mês'] = df['Mês'].astype(int)

# "R$ 7000000" -> 7000000 (remove prefixo e converte para int)
df['Valor Pago'] = df['Valor Pago'].str.lstrip('R$ ')
df['Valor Pago'] = df['Valor Pago'].astype(int)

# Status textual -> binário (Pago = 1, Não pago = 0)
df.loc[df['Status de Pagamento'] == 'Pago', 'Status de Pagamento'] = "1"
df.loc[df['Status de Pagamento'] == 'Não pago', 'Status de Pagamento'] = "0"
df['Status de Pagamento'] = df['Status de Pagamento'].astype(int)
```

O que cada bloco realiza:
1. **Mês:** troca as abreviações por número, para permitir ordenação e agrupamento numérico.
2. **Tipagem:** garante que `Dia`, `Mês` e `Chamadas Realizadas` sejam inteiros.
3. **Valor Pago:** remove o prefixo `R$ ` e converte a string em inteiro para poder somar/calcular médias.
4. **Status de Pagamento:** transforma em binário (1/0) — útil para o gráfico de pizza Pago × Não Pago.

### 5. Opções dos filtros

```python
options_month = [{'label': 'Ano Todo', 'value': 0}]
for i, j in zip(df_cru['Mês'].unique(), df['Mês'].unique()):
    options_month.append({'label': i, 'value': int(j)})
options_month = sorted(options_month, key=lambda x: x['value'])

options_team = [{'label': 'Todas as Equipes', 'value': 0}]
for i in df['Equipe'].unique():
    options_team.append({'label': i, 'value': i})
```

- **`options_month`** — combina o nome do mês em texto (de `df_cru`) com o número correspondente (de `df`) para gerar `{'label': 'Jan', 'value': 1}` etc. Inclui a opção `Ano Todo` (`value = 0`) e ordena tudo por número.
- **`options_team`** — uma opção por equipe, mais a opção `Todas as Equipes` (`value = 0`).

O valor `0` é convenção do projeto para "**sem filtro / mostrar tudo**".

### 6. Funções auxiliares

```python
def month_filter(month):
    if month == 0:
        mask = df['Mês'].isin(df['Mês'].unique())   # todos os meses
    else:
        mask = df['Mês'].isin([month])              # só o mês escolhido
    return mask

def team_filter(equipe):
    if equipe == 0:
        mask = df['Equipe'].isin(df['Equipe'].unique())
    else:
        mask = df['Equipe'].isin([equipe])
    return mask

def convert_to_text(month):
    lista1 = ['Ano Todo', 'Janeiro', ..., 'Dezembro']
    return lista1[month]
```

- `month_filter` / `team_filter` — retornam **máscaras booleanas** do pandas. Se o filtro for `0`, a máscara seleciona tudo; caso contrário, apenas o valor escolhido. São aplicadas com `df.loc[mask]` dentro dos callbacks.
- `convert_to_text` — converte o número do mês de volta para o nome por extenso, exibido no cabeçalho do filtro.

### 7. Layout

O layout é um `dbc.Container` fluido dividido em **linhas (`dbc.Row`) e colunas (`dbc.Col`)** do grid Bootstrap, cada gráfico dentro de um `dbc.Card`. Os parâmetros `sm`/`md`/`lg` controlam a largura responsiva em telas pequenas/médias/grandes.

**Linha 1:**
- **Coluna A** — cartão de título "Sales Analytics", ícone, botão de troca de tema (`ThemeSwitchAIO`), crédito do autor e botão "Visite o Site".
- **Coluna B** — os dois filtros: `RadioItems` de **mês** (`id='radio-month'`) e de **equipe** (`id='radio-team'`), mais os títulos dinâmicos (`month-select`, `team-select`).
- **Coluna C** — "Big Numbers": `graph1`, `graph2`, `graph3`.

**Linha 2:**
- `graph4`, `graph5` (Total de Chamadas), `graph6`, `graph7`, `graph8` (Equipes) e `graph9`.

**Linha 3:**
- `graph10`, `graph11` (Propaganda) e `graph12`.

Cada gráfico é um componente `dcc.Graph` com um `id` único — é esse `id` que conecta o layout aos callbacks.

### 8. Callbacks (a lógica reativa)

Cada callback declara **Outputs** (os gráficos que ele atualiza) e **Inputs** (os filtros/tema que o disparam). Sempre que um Input muda, o Dash chama a função e substitui as figuras.

Todos os callbacks têm 3 Inputs comuns:
- `radio-month` → mês selecionado;
- `radio-team` → equipe selecionada (nem todos usam);
- `ThemeSwitchAIO.ids.switch('theme')` → tema (aplica `flatly` ou `darkly` à figura).

O padrão interno de cada callback é sempre o mesmo:

```python
template = template_theme1 if theme else template_theme2   # escolhe tema
month_mask = month_filter(month)
team_mask = team_filter(team)
df_filtrado_full = df.loc[month_mask].loc[team_mask]        # aplica filtros
# ... groupby/sum para agregar ...
# ... monta a figura Plotly e aplica o template ...
```

Mapa dos 12 gráficos:

| Gráfico | Tipo | O que mostra |
|---|---|---|
| `graph1` | Indicator (número) | **Valor total** vendido (R$) no filtro. |
| `graph2` | Indicator (número + delta) | **Top consultor** e quanto está acima da média. |
| `graph3` | Indicator (número + delta) | **Top equipe** e quanto está acima da média. |
| `graph4` | Barras | Chamadas realizadas **por dia**. |
| `graph5` | Barras | Chamadas realizadas **por mês**. |
| `graph6` | Pizza (rosca) | Distribuição de **valor por equipe**. |
| `graph7` | Barras horizontais | **Chamadas por equipe**. |
| `graph8` | Linhas + área | Evolução do **valor por equipe ao longo dos meses** (com linha de total). |
| `graph9` | Barras horizontais | **Valor pago por equipe**. |
| `graph10` | Pizza (rosca) | Distribuição de **valor por meio de propaganda**. |
| `graph11` | Linhas | **Valor por meio de propaganda ao longo dos meses**. |
| `graph12` | Pizza (rosca) | Proporção **Pago × Não Pago** (soma de chamadas por status). |

> **Nota:** todas as funções de callback foram nomeadas `graphs_first_row`. Isso funciona porque o Dash registra o callback pelo decorador `@app.callback` no momento da definição, mas os nomes repetidos são confusos e dificultam a depuração (veja [melhorias](#observações-e-possíveis-melhorias)).

Os indicadores `graph2` e `graph3` usam o modo `number+delta` do Plotly: comparam o topo (maior consultor/equipe) com a **média** (`reference`), exibindo a variação percentual.

### 9. Execução do servidor

```python
if __name__ == '__main__':
    app.run(debug=True)
```

Sobe o servidor de desenvolvimento na porta padrão **8050** com hot-reload ativado.

---

## O notebook de limpeza (`cleaning_data.ipynb`)

Notebook de **prototipagem**, executado antes de escrever o `app.py`. Ele contém, em ordem:

1. `pip install matplotlib` / `pip install nbformat` — instalação de dependências.
2. Imports de `pandas`, `matplotlib`, `plotly`, `datetime`.
3. Leitura do CSV e cópia de segurança (`df_cru`).
4. **Exatamente as mesmas transformações** do `app.py`: conversão de meses, tipagem, limpeza do `Valor Pago` e binarização do `Status de Pagamento`.
5. Construção das listas `options_month` / `options_team` e das funções `month_filter` / `team_filter`.
6. Diversas células exploratórias com `groupby(...).sum()` e protótipos de cada figura Plotly (`go.Pie`, `go.Bar`, etc.) — testando os agрupamentos que depois viraram os callbacks.

Em resumo: o notebook é o "rascunho" e o `app.py` é a versão final e organizada da mesma lógica.

---

## Observações e possíveis melhorias

- **Arquivo `4.2.0`:** é apenas um log de `pip install` salvo por engano — pode ser apagado.
- **Nomes de callbacks duplicados:** todas as funções se chamam `graphs_first_row`. Renomeá-las (ex.: `update_big_numbers`, `update_calls`, …) melhora a legibilidade.
- **`str.lstrip('R$ ')`:** `lstrip` remove *caracteres* (`R`, `$`, espaço), não o prefixo literal; funciona aqui porque nenhum valor começa com outro desses caracteres, mas `str.replace('R$ ', '')` seria mais seguro.
- **`requirements.txt`:** o projeto não tem um. Convém criar um para fixar as versões das dependências.
- **Coluna `Duração da chamada`** está no dataset mas não é usada — poderia gerar uma métrica adicional (ex.: duração média por equipe).
- **Produção:** trocar `debug=True` por um servidor WSGI (Gunicorn) usando o objeto `server` já exposto.
