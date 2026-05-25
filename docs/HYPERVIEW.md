# Hyperview — Documentação Completa

> Guia de referência para desenvolvimento de apps mobile server-driven com HXML
> (Hyperview XML) servido por Django.

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Arquitetura no Contexto Django](#2-arquitetura-no-contexto-django)
3. [Estrutura do Documento HXML](#3-estrutura-do-documento-hxml)
4. [Sistema de Navegação](#4-sistema-de-navegação)
5. [Behaviors e Interatividade](#5-behaviors-e-interatividade)
6. [Sistema de Estilos](#6-sistema-de-estilos)
7. [Formulários e Inputs](#7-formulários-e-inputs)
8. [Listas com Infinite Scroll e Pull-to-Refresh](#8-listas-com-infinite-scroll-e-pull-to-refresh)
9. [Padrões e Melhores Práticas](#9-padrões-e-melhores-práticas)
10. [Referência de Endpoints e Views](#10-referência-de-endpoints-e-views)
11. [Referência de Templates](#11-referência-de-templates)
12. [Testes](#12-testes)
13. [Armadilhas Comuns e Debugging](#13-armadilhas-comuns-e-debugging)
14. [Referências e Links](#14-referências-e-links)

---

## 1. Visão Geral

**Hyperview** é um formato hypermedia e cliente React Native para desenvolvimento de
apps mobile server-driven. Em vez de servir HTML/JSON, o backend serve **HXML**
(Hyperview XML) — XML que descreve telas nativas (listas, formulários, navegação, etc.).
O cliente React Native interpreta esse XML e renderiza componentes nativos.

### Filosofia

- **Thin client**: O cliente mobile é "burro" — apenas renderiza o que o servidor manda.
- **Server-driven UI**: Todo layout, conteúdo e interações vivem no backend.
- **Zero deploy mobile**: Atualizações no backend refletem instantaneamente no app.
- **Hipermedia como motor**: Navegação, formulários e estado são dirigidos por
  hyperlinks (HREF) e respostas XML, similar ao funcionamento da Web com HTML.

### Stack neste projeto

| Camada | Tecnologia |
|--------|-----------|
| Backend | Django 5.2, Python 3.13 |
| Banco | PostgreSQL (Docker) / SQLite (local) |
| Geração HXML | Django Templates (`templates/hv/`) |
| Proxy | Nginx |
| Cliente Mobile | Hyperview React Native Client (demo Expo) v0.105 |
| Containers | Docker Compose (web, db, nginx, redis, worker) |

### Fluxo de funcionamento

```
┌──────────┐  GET /hyperview/    ┌──────────┐
│  Mobile   │ ─────────────────► │  Django   │
│  (Expo)   │                    │  Backend  │
│           │ ◄───────────────── │           │
│ Hyperview │  XML (HXML)        │ Templates │
│  Client   │                    │  hv/*.xml │
└──────────┘                    └──────────┘
```

1. App mobile faz `GET /hyperview/` → Django retorna XML com `<navigator>` e tabs
2. Cada tab (`/hyperview/home/`, `/hyperview/list/`, etc.) retorna XML com `<screen>`
3. Toques/interações disparam `<behavior>` elements que fazem novas requests HTTP
4. Django processa (valida formulário, busca dados) e retorna novo XML
5. Hyperview Client renderiza o XML como tela nativa no dispositivo

---

## 2. Arquitetura no Contexto Django

### Estrutura de diretórios

```
django-hyperview/
├── core/                        # Config Django
│   ├── urls.py                  # include("hv.urls") em /hyperview/
│   └── settings.py              # INSTALLED_APPS + "hv"
├── hv/                          # App Hyperview
│   ├── urls.py                  # app_name = "hv"
│   ├── views.py                 # TemplateView + View (get/post)
│   └── tests.py                 # Testes com reverse()
├── templates/hv/                # Templates HXML
│   ├── base.xml                 # Template base com header, body, loading screens
│   ├── index.xml                # Navigator (entrypoint)
│   ├── home.xml, list.xml, ...  # Telas
│   ├── list_items.xml           # Fragmento para infinite scroll
│   └── includes/                # Componentes reutilizáveis
│       ├── header.xml / header_styles.xml
│       ├── tabbar.xml / tabbar_styles.xml
│       └── loading_*.xml        # Loading screens
```

### Content-Type

Toda resposta HXML deve usar `content_type='application/xml'`. É configurado
no atributo de classe `content_type` das CBVs:

```python
class HomeView(TemplateView):
    template_name = "hv/home.xml"
    content_type = "application/xml"
```

### CSRF exemption

Endpoints que recebem POST do app mobile usam `@method_decorator(csrf_exempt, name="dispatch")`.
Isso é correto pois o app mobile não usa cookies de sessão (doc Django recomenda isso
para API endpoints com autenticação alternativa):

```python
@method_decorator(csrf_exempt, name="dispatch")
class FormView(View):
    def get(self, request, *args, **kwargs):
        ...
    def post(self, request, *args, **kwargs):
        ...
```

### `_base_url()` helper

Função utilitária que resolve a URL base para links HXML. Usa `settings.HYPERVIEW_BASE_URL`
se configurado, senão deriva do request:

```python
def _base_url(request):
    base = getattr(settings, "HYPERVIEW_BASE_URL", None)
    if base:
        return base.rstrip("/")
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{request.get_host()}"
```

### Namespaces obrigatórios

Todo documento `<doc>` deve declarar:

```xml
<doc xmlns="https://hyperview.org/hyperview"
     xmlns:navigation="https://hyperview.org/navigation"
     xmlns:safe-area="https://hyperview.org/safe-area">
```

---

## 3. Estrutura do Documento HXML

### Hierarquia de elementos

```
<doc>                           ← Raiz (pode conter <screen> ou <navigator>)
├── <navigator>                 ← Estrutura de navegação (stack ou tab)
│   └── <nav-route>             ← Rota individual
│       └── <navigator>         ← Navegação aninhada (ex: tabs dentro de stack)
│           └── <nav-route>
├── <screen>                    ← Tela (pode ter várias no mesmo doc)
│   ├── <styles>                ← Estilos CSS-in-JS-like
│   │   ├── <style id="...">    ← Regra de estilo com atributos React Native
│   │   │   └── <modifier>      ← Estado (pressed, focused, selected)
│   │   │       └── <style>
│   │   └── ...
│   └── <body>                  ← Corpo da tela
│       ├── <header>            ← Header fixo no topo
│       ├── <view>              ← Container genérico (View RN)
│       │   ├── <text>          ← Texto (Text RN)
│       │   ├── <image>         ← Imagem (Image RN)
│       │   ├── <list>          ← FlatList nativa
│       │   │   └── <item>      ← Item da lista
│       │   ├── <section-list>  ← SectionList nativa
│       │   │   ├── <section>
│       │   │   │   └── <item>
│       │   │   └── <section-title>
│       │   ├── <form>          ← Formulário
│       │   │   ├── <text-field>
│       │   │   ├── <date-field>
│       │   │   ├── <picker-field>
│       │   │   ├── <select-single>
│       │   │   ├── <select-multiple>
│       │   │   └── <switch>
│       │   ├── <spinner>       ← Indicador de loading
│       │   ├── <web-view>      ← WebView embutida
│       │   └── <behavior>      ← Ações/interações
│       └── <items>             ← Wrapper para fragmentos (infinite scroll)
│           └── <item>
```

### `<doc>` — Raiz do documento

Elemento raiz de todo documento HXML. Pode conter:

- **Um ou mais `<screen>`**: Para telas normais + loading screens no mesmo doc.
- **Um `<navigator>`**: Documento de entrada que define a estrutura de navegação.

### `<screen>` — Tela

Cada `<screen>` define uma tela completa. Atributos:

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `id` | string | Identificador único (usado em `show-during-load`) |
| `key` | string | Chave para reconciliação |

Estrutura:
```xml
<screen id="main">
  <styles>...</styles>
  <body>...</body>
</screen>
```

> **Importante**: Apenas o **primeiro** `<screen>` de um `<doc>` é renderizado
> automaticamente. Telas extras (loading screens, modais) são acessadas via
> `show-during-load` ou referenciadas por `id`.

### `<body>` — Corpo da tela

Container principal. Atributos principais:

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `scroll` | boolean | Habilita scroll (`true`/`false`) |
| `scroll-orientation` | `horizontal`/`vertical` | Direção do scroll |
| `style` | styleList | Lista de estilos (separados por espaço) |
| `safe-area` | boolean | Aplica safe area insets |

> **Regra de ouro**: Telas com `<list>` ou `<section-list>` devem usar
> `scroll="false"` no `<body>`. O `<list>` já é uma VirtualizedList (FlatList)
> com scroll próprio. Colocar FlatList dentro de ScrollView causa erro no
> React Native.

### `<list>` — Lista nativa (FlatList)

Renderiza uma FlatList do React Native (lista virtualizada). Suporta:

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `itemHeight` | number | Altura fixa dos itens (otimização) |
| `style` | styleList | Estilos da lista |
| `scroll` | boolean | Scroll da lista |
| `shows-scroll-indicator` | boolean | Indicador de scroll |

**Filhos válidos de `<list>`**: `<item>`, `<items>`, `<behavior>`

### `<section-list>` — Lista com seções (SectionList)

Similar ao `<list>`, mas com suporte a seções agrupadas:

```xml
<section-list>
  <section>
    <section-title><text>Categoria A</text></section-title>
    <item key="1"><text>Item 1</text></item>
    <item key="2"><text>Item 2</text></item>
  </section>
  <section>
    <section-title><text>Categoria B</text></section-title>
    <item key="3"><text>Item 3</text></item>
  </section>
</section-list>
```

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `sticky-section-titles` | boolean | Títulos de seção "grudam" no topo |

### `<items>` — Wrapper de fragmento

Usado como raiz em respostas de fragmentos (infinite scroll, replace-inner).
O `<list>` ignora o wrapper `<items>` e renderiza apenas os `<item>` filhos.

```xml
<items xmlns="https://hyperview.org/hyperview">
  <item key="21">...</item>
  <item key="22">...</item>
</items>
```

> Isso é necessário porque XML exige um único elemento raiz, mas o `<list>`
> espera receber múltiplos `<item>` como filhos diretos na substituição.

---

## 4. Sistema de Navegação

Hyperview usa **React Navigation** internamente para gerenciar a pilha de telas.
A estrutura de navegação é definida declarativamente via HXML.

### `<navigator>` — Container de navegação

| Atributo | Tipo | Obrigatório | Descrição |
|----------|------|:----------:|-----------|
| `id` | string | Sim | Identificador único global |
| `type` | `stack` / `tab` | Sim | Tipo do navigator |
| `merge` | boolean | Não | Merge com estado existente (deep links) |

#### Tipos de navigator

**`stack`**: Pilha de telas — suporta push, pop, modal. Ideal como navigator raiz.

**`tab`**: Abas — navegação entre telas fixas. Cada `<nav-route>` é uma tab.

### `<nav-route>` — Rota de navegação

| Atributo | Tipo | Obrigatório | Descrição |
|----------|------|:----------:|-----------|
| `id` | string | Sim | Identificador da rota |
| `href` | string | Não* | URL do conteúdo da rota |
| `selected` | boolean | Não | Tab inicialmente selecionada (tab navigator) |
| `modal` | boolean | Não | Apresenta como modal (stack navigator) |

> *Obrigatório se a rota não contiver um `<navigator>` filho.

### Exemplo: Stack + Tab Navigator (entrypoint)

```xml
<doc xmlns="https://hyperview.org/hyperview">
  <navigator id="root-stack" type="stack">
    <nav-route id="main-tabs">
      <navigator id="main-tab-navigator" type="tab">
        <nav-route id="tab-home" href="/hyperview/home/" />
        <nav-route id="tab-list" href="/hyperview/list/" />
        <nav-route id="tab-profile" href="/hyperview/profile/" />
      </navigator>
    </nav-route>
  </navigator>
</doc>
```

### Pre-stacking (múltiplas rotas no stack)

Adicionar múltiplos `<nav-route>` em um stack navigator empilha todos de uma vez:

```xml
<navigator id="root" type="stack">
  <nav-route id="home" href="/home.xml" />
  <nav-route id="welcome" href="/welcome.xml" modal="true" />
</navigator>
```

O usuário verá a tela "welcome" como modal sobre "home".

### Navegação condicional (server-side)

O navegador pode ser montado dinamicamente no backend:

```xml
<navigator id="root" type="stack">
  {% if is_first_time_user %}
    <nav-route id="home" href="/ftu.xml" />
  {% else %}
    <nav-route id="home" href="/user.xml" />
  {% endif %}
</navigator>
```

### Loading screens

Telas de carregamento são definidas como `<screen>` extras no mesmo documento,
referenciadas via `show-during-load`:

```xml
<doc>
  <screen><!-- tela principal --></screen>
  <screen id="loading-screen-pushed"><!-- loading para push --></screen>
  <screen id="loading-screen-modal"><!-- loading para modal --></screen>
</doc>
```

No comportamento:
```xml
<text href="/next" action="push" show-during-load="loading-screen-pushed">
  Próxima tela
</text>
```

### Navegação separada em múltiplos documentos

A hierarquia pode ser distribuída em documentos separados:

**index.xml** (stack root):
```xml
<navigator id="root" type="stack">
  <nav-route id="tabs" href="/tabs.xml" />
</navigator>
```

**tabs.xml** (tab navigator):
```xml
<navigator id="main" type="tab">
  <nav-route id="home" href="/home.xml" />
  <nav-route id="profile" href="/profile.xml" />
</navigator>
```

---

## 5. Behaviors e Interatividade

Behaviors são o mecanismo principal de interatividade no Hyperview. Definem
**o que acontece** quando o usuário interage com um elemento.

### Modelo mental

1. Um **trigger** (evento) dispara o behavior
2. O behavior faz uma **request HTTP** (ou referencia um fragmento local)
3. O servidor retorna **novo conteúdo XML**
4. O conteúdo é **aplicado** conforme a `action` (navegar, substituir, etc.)

### Atributos de behavior

| Atributo | Tipo | Padrão | Descrição |
|----------|------|:------:|-----------|
| `trigger` | string | `press` | O que dispara o behavior |
| `action` | string | `push` | O que fazer com a resposta |
| `href` | string | — | URL ou fragmento `#id` |
| `verb` | `get`/`post` | `get` | Método HTTP |
| `target` | string | — | Alvo da ação (id do elemento ou tab) |
| `show-during-load` | string | — | IDs de elementos a mostrar durante loading |
| `hide-during-load` | string | — | IDs de elementos a esconder durante loading |
| `once` | boolean | false | Executar apenas na primeira vez |
| `delay` | number | — | Milissegundos de delay antes de executar |
| `new-value` | string | — | Valor para `action="set-value"` |
| `event-name` | string | — | Nome do evento para dispatch/on-event |
| `sync-id` | string | — | ID para agrupamento de requests síncronas |
| `immediate` | boolean | — | Executar imediatamente (sem delay de press) |

### Triggers (eventos)

| Trigger | Suportado por | Descrição |
|---------|--------------|-----------|
| `press` | view, text, image | Toque (padrão) |
| `longPress` | view, text, image | Pressão longa |
| `pressIn` | view, text, image | Dedos toca o elemento |
| `pressOut` | view, text, image | Dedo solto do elemento |
| `visible` | view, text, image | Elemento fica visível na tela |
| `refresh` | view, text, image, list, section-list | Pull-to-refresh |
| `load` | view, text, image | Quando o elemento é carregado |
| `focus` | text-field, date-field, picker-field | Elemento recebe foco |
| `blur` | text-field, date-field, picker-field | Elemento perde foco |
| `change` | text-field, date-field, picker-field, switch | Valor do campo muda |
| `submit` | text-field, date-field, picker-field | Submissão do campo |
| `select` | option | Opção selecionada |
| `deselect` | option | Opção desselecionada |
| `on-event` | view, text | Evento disparado via dispatch-event |
| `back` | view | Tela sendo fechada (bloqueio de back) |

### Actions (ações)

#### Navegação

| Action | Descrição |
|--------|-----------|
| `push` | Empilha nova tela (padrão) |
| `new` | Abre modal sobre a tela atual |
| `back` | Volta na pilha (desfaz push) |
| `close` | Fecha modal (desfaz new) |
| `navigate` | Navega para tab (`#tab-id`) ou push/back inteligente |
| `reload` | Recarrega a tela atual |
| `deep-link` | Abre URL no SO (outro app) |
| `open-settings` | Abre configurações do app no SO |

#### Atualização

| Action | Descrição |
|--------|-----------|
| `replace` | Substitui elemento alvo pelo conteúdo da resposta |
| `replace-inner` | Substitui filhos do elemento alvo |
| `append` | Adiciona conteúdo como último filho do alvo |
| `prepend` | Adiciona conteúdo como primeiro filho do alvo |
| `show` | Mostra elemento (remove `hide="true"`) |
| `hide` | Esconde elemento (aplica `hide="true"`) |
| `toggle` | Alterna visibilidade |
| `set-value` | Define valor de input (`new-value` obrigatório) |
| `select-all` | Seleciona todas opções (select-multiple) |
| `unselect-all` | Desseleciona todas opções |
| `dispatch-event` | Dispara evento (`event-name` obrigatório) |
| `copy-to-clipboard` | Copia para clipboard |
| `alert` | Exibe alerta nativo (namespace alert) |
| `scroll` | Scroll para posição (namespace scroll) |

### Formato do `href`

| Formato | Exemplo | Uso |
|---------|---------|-----|
| **URI relativa** | `/hyperview/list/` | Combinada com protocolo+host da requisição atual |
| **URL absoluta** | `https://api.example.com/data` | Usada como está |
| **Fragmento local** | `#element-id` | Referencia elemento no documento atual |
| **Não especificado** | `#` | Usado com `back`/`close` para navegar sem reload |

### Comportamento padrão de elementos com `href`

Quando um elemento (view, text, image) tem `href`, o Hyperview:

1. Envolve o elemento com uma view "tappable"
2. Aplica opacidade no press (feedback visual)
3. Executa ação `push` (padrão) quando pressionado

Para customizar o estilo do wrapper:
```xml
<view href="/next" href-style="my-tappable-style" style="my-content-style">
  <text>Conteúdo</text>
</view>
```

### `<behavior>` vs atributos inline

Behaviors podem ser definidos como atributos no próprio elemento ou como
elementos `<behavior>` filhos. São equivalentes:

```xml
<!-- Atributos inline -->
<view href="/next" action="push" trigger="press">
  <text>Próximo</text>
</view>

<!-- Elemento behavior -->
<view>
  <behavior trigger="press" action="push" href="/next" />
  <text>Próximo</text>
</view>
```

Use `<behavior>` quando precisar de múltiplos behaviors no mesmo elemento:

```xml
<view style="Button">
  <behavior trigger="press" href="/display" />
  <behavior trigger="longPress" href="/edit" action="new" />
  <text>Item</text>
</view>
```

### Eventos (dispatch-event / on-event)

Permitem comunicação entre telas sem depender de estado global:

**Disparar evento:**
```xml
<view>
  <behavior trigger="press" action="dispatch-event" event-name="user-logged-in" />
  <text>Login</text>
</view>
```

**Ouvir evento:**
```xml
<view>
  <behavior trigger="on-event" event-name="user-logged-in" action="replace"
            href="/refresh-dashboard" />
</view>
```

### Alert behaviors

Exibe diálogos nativos de alerta:

```xml
<view>
  <behavior
    trigger="press"
    action="alert"
    xmlns:alert="https://hyperview.org/hyperview-alert"
    alert:title="Confirmação"
    alert:message="Tem certeza?"
  >
    <alert:option alert:label="OK">
      <behavior action="back" />
    </alert:option>
    <alert:option alert:label="Cancelar" />
  </behavior>
  <text>Excluir</text>
</view>
```

---

## 6. Sistema de Estilos

Os estilos no Hyperview mapeiam diretamente para **estilos React Native**
(layout com Flexbox). São definidos em `<styles>` dentro de `<screen>`
e aplicados via atributo `style` (lista separada por espaço).

### Anatomia de um estilo

```xml
<styles>
  <style
    id="card"
    backgroundColor="white"
    borderRadius="12"
    padding="16"
    shadowColor="#000"
    shadowOffsetX="0"
    shadowOffsetY="1"
    shadowOpacity="0.1"
    shadowRadius="3"
    flexDirection="row"
    alignItems="center"
  >
    <!-- Modificadores de estado -->
    <modifier pressed="true">
      <style opacity="0.8" />
    </modifier>
    <modifier focused="true">
      <style borderColor="#3b82f6" borderWidth="2" />
    </modifier>
    <modifier selected="true">
      <style backgroundColor="#eff6ff" />
    </modifier>
  </style>
</styles>
```

### Atributos de layout (Flexbox)

| Atributo | Valores | Equivalente CSS |
|----------|---------|-----------------|
| `flex` | number (-1, 0, 1, 2, ...) | `flex` |
| `flexDirection` | row, row-reverse, column, column-reverse | `flex-direction` |
| `flexWrap` | wrap, nowrap | `flex-wrap` |
| `flexGrow` | number | `flex-grow` |
| `flexShrink` | number | `flex-shrink` |
| `flexBasis` | number, auto | `flex-basis` |
| `justifyContent` | flex-start, flex-end, center, space-between, space-around, space-evenly | `justify-content` |
| `alignItems` | flex-start, flex-end, center, stretch, baseline | `align-items` |
| `alignSelf` | auto, flex-start, flex-end, center, stretch, baseline | `align-self` |
| `alignContent` | flex-start, flex-end, center, stretch, space-between, space-around | `align-content` |
| `position` | relative, absolute | `position` |
| `display` | flex, none | `display` |
| `overflow` | visible, hidden, scroll | `overflow` |

### Dimensões e espaçamento

| Atributo | Tipo |
|----------|------|
| `width`, `height` | number, string (px ou %) |
| `minWidth`, `maxWidth`, `minHeight`, `maxHeight` | number, string |
| `margin`, `marginTop`, `marginBottom`, `marginLeft`, `marginRight` | number, string |
| `marginHorizontal`, `marginVertical`, `marginStart`, `marginEnd` | number, string |
| `padding`, `paddingTop`, `paddingBottom`, `paddingLeft`, `paddingRight` | number, string |
| `paddingHorizontal`, `paddingVertical`, `paddingStart`, `paddingEnd` | number, string |
| `top`, `bottom`, `left`, `right`, `start`, `end` | number, string |
| `gap`, `columnGap`, `rowGap` | number |

### Cores, bordas e sombras

| Atributo | Tipo | Notas |
|----------|------|-------|
| `backgroundColor` | color | hex, rgb, rgba, hsl, hsla, nome |
| `borderColor`, `borderTopColor`, etc. | color | |
| `borderWidth`, `borderTopWidth`, etc. | number | |
| `borderRadius`, `borderTopLeftRadius`, etc. | number | |
| `borderStyle` | solid, dotted, dashed | |
| `shadowColor` | color | **apenas iOS** |
| `shadowOffsetX`, `shadowOffsetY` | number | **apenas iOS** |
| `shadowOpacity` | float (0-1) | **apenas iOS** |
| `shadowRadius` | number | **apenas iOS** |
| `elevation` | number | **apenas Android** |
| `opacity` | float (0-1) | |

### Tipografia

| Atributo | Valores |
|----------|---------|
| `color` | color |
| `fontSize` | number |
| `fontFamily` | string |
| `fontWeight` | normal, bold, 100-900 |
| `fontStyle` | normal, italic |
| `textAlign` | auto, left, right, center, justify |
| `textAlignVertical` | auto, top, bottom, center |
| `lineHeight` | number |
| `letterSpacing` | number |
| `textTransform` | string |
| `textDecorationLine` | string |
| `numberOfLines` | number |
| `allowFontScaling` | boolean |
| `maxFontSizeMultiplier` | float |

### Imagens

| Atributo | Valores |
|----------|---------|
| `resizeMode` | cover, contain, stretch, repeat, center |
| `tintColor` | color |
| `overlayColor` | color |

### Modificadores de estado

Modificadores permitem estilos condicionais baseados no estado do elemento:

```xml
<style id="btn-primary" backgroundColor="#3b82f6" borderRadius="12" padding="16">
  <modifier pressed="true">
    <style opacity="0.8" />
  </modifier>
</style>

<style id="form-input" borderColor="#cbd5e1" borderWidth="1">
  <modifier focused="true">
    <style borderColor="#3b82f6" borderWidth="2" />
  </modifier>
</style>
```

| Modificador | Quando aplica |
|-------------|---------------|
| `pressed="true"` | Elemento sendo pressionado |
| `focused="true"` | Elemento com foco (inputs) |
| `selected="true"` | Elemento selecionado (options) |

> **Importante**: Estilos vivem obrigatoriamente em `<styles>` dentro de `<screen>`.
> Não podem ficar soltos no `<body>`.

### Safe Area

Para lidar com notches e barras do sistema:

```xml
<safe-area:safe-area-view
  xmlns:safe-area="https://hyperview.org/safe-area"
  safe-area:mode="padding"
  safe-area:insets='["top","left","right"]'
>
  <!-- conteúdo que respeita safe area -->
</safe-area:safe-area-view>
```

| Atributo | Descrição |
|----------|-----------|
| `safe-area:mode` | `padding` (adiciona padding) |
| `safe-area:insets` | JSON array com os lados a aplicar |

### Dica: Shadow iOS + Elevation Android

Para sombras cross-platform, use ambos:

```xml
<style id="card"
  shadowColor="#000"
  shadowOffsetX="0"
  shadowOffsetY="1"
  shadowOpacity="0.1"
  shadowRadius="3"
  elevation="3"
/>
```

---

## 7. Formulários e Inputs

### `<form>` — Container de formulário

Agrupa campos. No submit, serializa todos os campos filhos e envia via
query string (GET) ou form-urlencoded (POST).

```xml
<form id="main-form">
  <text-field name="username" ... />
  <text-field name="password" ... />
  <view id="submit-btn">
    <behavior trigger="press" action="replace" verb="POST"
              href="/login/" target="main-form" />
    <text>Entrar</text>
  </view>
</form>
```

### `<text-field>` — Campo de texto

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `name` | string | Nome do campo (obrigatório) |
| `value` | string | Valor inicial |
| `placeholder` | string | Placeholder |
| `placeholderTextColor` | color | Cor do placeholder |
| `keyboard-type` | enum | Tipo de teclado (ver abaixo) |
| `secure-text` | boolean | Texto seguro (senha) |
| `multiline` | boolean | Múltiplas linhas |
| `auto-focus` | boolean | Foco automático |
| `auto-capitalize` | enum | Capitalização automática |
| `auto-complete` | enum | Autocomplete (email, username, etc.) |
| `mask` | string | Máscara de input, ex: `(99) 99999-9999` |
| `editable` | boolean | Campo editável |
| `style` | styleList | Estilo do campo |
| `field-style` | styleList | Estilo do container |
| `clearButtonMode` | enum | Botão limpar (iOS) |
| `returnKeyType` | enum | Tipo da tecla return |
| `enterKeyHint` | enum | Dica da tecla enter |
| `maxFontSizeMultiplier` | float | Limite de escala de fonte |
| `debounce` | number | Debounce para trigger `change` (ms) |

**Keyboard types:**
`default`, `number-pad`, `decimal-pad`, `phone-pad`, `email-address`, `url`,
`ascii-capable`, `numbers-and-punctuation`, `name-phone-pad`, `twitter`, `web-search`

### `<date-field>` — Campo de data

| Atributo | Tipo | Descrição |
|----------|------|-----------|
| `name` | string | Nome do campo |
| `value` | string | Data no formato `YYYY-MM-DD` |
| `min`, `max` | date | Limites de data |
| `mode` | calendar, spinner, default | Modo do picker |
| `placeholder` | string | Placeholder |
| `label-format` | string | Formato do label |
| `field-style`, `field-text-style` | styleList | Estilos do campo |
| `modal-style`, `modal-overlay-style` | styleList | Estilos do modal |
| `modal-animation-duration` | number | Duração da animação |

### `<picker-field>` — Campo de seleção (dropdown)

```xml
<picker-field name="category" placeholder="Selecione" value="tech">
  <picker-item label="Tecnologia" value="tech" />
  <picker-item label="Negócios" value="business" />
  <picker-item label="Design" value="design" />
</picker-field>
```

| Atributo | Descrição |
|----------|-----------|
| `name` | Nome do campo |
| `value` | Valor selecionado |
| `placeholder` | Placeholder mostrado quando nada selecionado |
| `done-label` | Label do botão "Concluir" |
| `cancel-label` | Label do botão "Cancelar" |

### `<select-single>` — Seleção única (radio group)

```xml
<select-single name="category">
  <option value="tech" selected="true">
    <text>Tecnologia</text>
  </option>
  <option value="business">
    <text>Negócios</text>
  </option>
</select-single>
```

| Atributo | Descrição |
|----------|-----------|
| `name` | Nome do campo (obrigatório) |
| `allow-deselect` | Permite desselecionar |

### `<select-multiple>` — Seleção múltipla (checkboxes)

```xml
<select-multiple name="interests">
  <option value="sports" selected="true">
    <text>Esportes</text>
  </option>
  <option value="music">
    <text>Música</text>
  </option>
</select-multiple>
```

### `<switch>` — Toggle switch

```xml
<switch name="notifications" value="on" />
```

| Atributo | Valores |
|----------|---------|
| `name` | Nome do campo (obrigatório) |
| `value` | `on` / `off` |

### Submissão de formulário

No Hyperview, formulários não têm ação de submit nativa. O submit é feito
via behavior com `verb="POST"` em um elemento dentro (ou fora) do form:

```xml
<form id="login-form">
  <text-field name="username" ... />
  <text-field name="password" secure-text="true" ... />

  <!-- Botão de submit: replace no próprio form -->
  <view id="login-button">
    <behavior
      trigger="press"
      action="replace"
      href="/login/"
      verb="POST"
      target="login-form"
      show-during-load="login-spinner"
      hide-during-load="login-button"
    />
    <text>Entrar</text>
  </view>
  <spinner id="login-spinner" hide="true" />
</form>
```

**Fluxo de validação server-side:**
1. Usuário preenche e pressiona submit
2. Behavior faz POST com dados serializados
3. Django valida: se ok → retorna `<form>` com mensagem de sucesso;
   se erro → retorna `<form>` com `errors` no contexto e feedback visual
4. `action="replace"` com `target="login-form"` substitui o formulário
   antigo pela resposta

> **Importante**: `hide-during-load="login-button"` + `show-during-load="login-spinner"`
> criam feedback visual durante a requisição.

### `set-value` — Atualizar input programaticamente

```xml
<text-field id="my-input" name="email" />
<view>
  <behavior trigger="press" action="set-value" new-value="test@email.com"
            target="my-input" />
  <text>Preencher email</text>
</view>
```

---

## 8. Listas com Infinite Scroll e Pull-to-Refresh

### Pull-to-refresh

Adiciona comportamento de "puxar para atualizar" a uma `<list>`:

```xml
<list id="main-list">
  <behavior
    trigger="refresh"
    action="replace"
    href="/hyperview/list/?page=1"
    target="main-list"
  />
  <!-- itens... -->
</list>
```

`action="replace"` com `target="main-list"` substitui a lista inteira.
O endpoint pode ser o mesmo da ListView — Hyperview extrai os `<item>` do resultado.

### Infinite scroll

Usa **dois endpoints** distintos:

| Endpoint | Tipo de resposta | Conteúdo |
|----------|-----------------|----------|
| `/hyperview/list/` (ListView) | Página completa | `<doc><screen>...<list>...</list></screen></doc>` |
| `/hyperview/list/items/?page=N` (ListItemsView) | Fragmento | `<items xmlns="..."><item>...</item></items>` |

**Mecanismo:**

1. `ListView` renderiza `<list>` completa com primeira página
2. Último `<item>` é um **sentinela** com `trigger="visible"` `once="true"` `action="replace"`
3. Quando visível, sentinela dispara request para `ListItemsView`
4. `ListItemsView` retorna `<items>` contendo novos `<item>` + novo sentinela
5. `action="replace"` substitui o sentinela pelos novos itens

**Sentinela (na página inicial e em cada resposta de fragmento):**

```xml
<item key="load-more" id="load-more-spinner"
      trigger="visible" once="true"
      action="replace"
      href="/hyperview/list/items/?page={{ next_page }}"
      style="load-more-btn">
  <spinner />
</item>
```

**Resposta do endpoint de fragmento (`list_items.xml`):**

```xml
<items xmlns="https://hyperview.org/hyperview">
  <item key="21" style="Item">
    <text>Item 21</text>
  </item>
  <!-- mais itens... -->
  <item key="load-more" id="load-more-spinner"
        trigger="visible" once="true" action="replace"
        href="/hyperview/list/items/?page=3" style="load-more-btn">
    <spinner />
  </item>
</items>
```

**Fim da lista**: Omitir o sentinela da resposta (quando `has_next = False`)
para não disparar mais requests.

### Agrupamento com `{% regroup %}`

A tag `{% regroup %}` do Django agrupa itens por categoria e insere headers:

```python
# Antes do template — ordenação é obrigatória
items.sort(key=lambda x: (x["category"], x["id"]))
```

```xml
{% regroup items by category as grouped_items %}

{% for grupo in grouped_items %}
<item key="header-p{{ page }}-{{ grupo.grouper }}" style="list-header">
  <text>{{ grupo.grouper|upper }}</text>
</item>

{% for item in grupo.list %}
<item key="{{ item.id }}" style="list-item">
  <!-- conteúdo do item -->
</item>
{% endfor %}
{% endfor %}
```

> **⚠️ Keys únicas**: Headers de categoria se repetem em páginas diferentes.
> Prefixar keys com `p{{ page }}` evita "Encountered two children with the same key".

### `scroll="false"` no body com `<list>`

Telas com `<list>` ou `<section-list>` **NÃO** devem ter scroll no body.
A lista já é VirtualizedList com scroll próprio. Colocar FlatList dentro
de ScrollView causa erro fatal no React Native.

```xml
<body style="body" scroll="false">  <!-- scroll=false é obrigatório -->
  <list id="main-list">
    <!-- itens -->
  </list>
</body>
```

### Resumo: scroll por tipo de tela

| Tipo de tela | Scroll |
|-------------|:------:|
| Home, Profile, Detail, Form, Settings, About | Sim (container interno) |
| List | **Não** (lista tem scroll próprio) |
| Login | Não precisa (conteúdo fixo) |

---

## 9. Padrões e Melhores Práticas

### 9.1. Template base.xml

Todos os templates estendem `hv/base.xml` que fornece:

- Estrutura `<doc>` com namespaces
- `<styles>` base (body, content-area)
- `<safe-area:safe-area-view>` para header
- Include de loading screens (pushed, modal, reload)
- Blocos substituíveis

```xml
<doc xmlns="https://hyperview.org/hyperview"
     xmlns:navigation="https://hyperview.org/navigation"
     xmlns:safe-area="https://hyperview.org/safe-area">
  <screen>
    <styles>
      <style id="body" backgroundColor="#f8fafc" flex="1" />
      {% include "hv/includes/header_styles.xml" %}
      {% include "hv/includes/tabbar_styles.xml" %}
      {% block styles %}{% endblock %}
    </styles>

    <body style="body" scroll="false">
      <safe-area:safe-area-view ...>
        {% include "hv/includes/header.xml" %}
      </safe-area:safe-area-view>

      <view style="content-area">
        {% block container %}{% endblock %}
      </view>

      {% block tab_bar %}{% endblock %}
    </body>
  </screen>

  {% include "hv/includes/loading_pushed.xml" %}
  {% include "hv/includes/loading_modal.xml" %}
  {% include "hv/includes/loading_reload.xml" %}
</doc>
```

### 9.2. Header condicional

O header usa variáveis de contexto para decidir comportamento:

| Variável | Efeito |
|----------|--------|
| `show_back: True` | Exibe botão "‹ Voltar" |
| `back_href: "#tab-id"` | Usa `action="navigate"` (volta pra tab) |
| `back_href` ausente | Usa `action="back"` (desempilha) |
| `is_modal: True` | Usa `action="close"` (fecha modal) |

### 9.3. Tab bar manual

A tab bar **não é automática**. Deve ser incluída em cada tela de tab:

```xml
{% block tab_bar %}
{% include "hv/includes/tabbar.xml" %}
{% endblock %}
```

O tab bar usa o custom element `navigation:bottom-tab-bar` registrado no demo app.
Cada `<navigation:bottom-tab-bar-item>` referencia o `navigation:route` que
corresponde ao `id` do `<nav-route>` no `index.xml`.

### 9.4. Includes: styles + markup separados

Django não suporta blocos dentro de `{% include %}` (ticket #6646, wontfix).
Por isso cada componente tem **dois arquivos**:

```
includes/
├── header.xml          # markup
├── header_styles.xml   # estilos
├── tabbar.xml          # markup
├── tabbar_styles.xml   # estilos
├── loading_pushed.xml  # loading screen (já inclui seus próprios estilos)
├── loading_modal.xml
└── loading_reload.xml
```

O `base.xml` inclui `_styles.xml` dentro de `<styles>` e `.xml` dentro de `<body>`.

### 9.5. Content-Type: application/xml

Todas as views HXML devem retornar `content_type='application/xml'`:

```python
class HomeView(TemplateView):
    template_name = "hv/home.xml"
    content_type = "application/xml"
```

### 9.6. Views com POST: csrf_exempt + View class

Para views que recebem POST do app mobile:

```python
@method_decorator(csrf_exempt, name="dispatch")
class FormView(View):
    def get(self, request, *args, **kwargs):
        ...

    def post(self, request, *args, **kwargs):
        ...
```

### 9.7. URL reversals

Use `{% url 'hv:nome' %}` nos templates e `reverse("hv:nome")` nos testes.
Nunca hardcoded.

### 9.8. Navegação de/para tabs

- Para navegar de uma tela para uma tab: `action="navigate" href="#tab-id"`
- Para sair de uma tela push: `action="back" href="#"` (sem reload)
- Para sair de uma tela modal: `action="close" href="#"`

### 9.9. Telas modais

Telas de confirmação (delete, logout) são abertas com `action="new"` e fechadas
com `action="close"`. O header usa `is_modal: True` para mostrar botão "‹ Voltar"
que executa `close`:

```python
context = {"is_modal": True, "show_back": True}
```

### 9.10. Listas vazias (empty states)

Sempre fornecer fallback com `{% empty %}` nos loops:

```xml
{% for item in items %}
<item key="{{ item.id }}">...</item>
{% empty %}
<item key="empty">
  <view style="empty-state">
    <text>Nenhum item encontrado.</text>
  </view>
</item>
{% endfor %}
```

### 9.11. Performance com listas

- `<list>` usa `itemHeight` para otimizar renderização quando altura é fixa
- Use `hide-during-load` / `show-during-load` em vez de gerenciar estado manualmente
- Prefira `action="replace"` em vez de `push` para formulários (evita empilhar)

### 9.12. Acessibilidade

- `allowFontScaling` + `maxFontSizeMultiplier` em textos para controle de escala
- `numberOfLines` para truncar textos longos
- Labels descritivos em inputs e botões

---

## 10. Referência de Endpoints e Views

### URLs (app `hv`, prefixo `/hyperview/`)

| URL | View | Template | Tipo |
|-----|------|----------|------|
| `/` | `IndexView` | `hv/index.xml` | Navigator (entrypoint) |
| `/home/` | `HomeView` | `hv/home.xml` | Página |
| `/list/` | `ListView` | `hv/list.xml` | Página |
| `/list/items/` | `ListItemsView` | `hv/list_items.xml` | **Fragmento** |
| `/detail/<id>/` | `DetailView` | `hv/detail.xml` | Página |
| `/detail/<id>/share/` | `ShareView` | `hv/share.xml` | Página |
| `/detail/<id>/delete/` | `DeleteView` (GET+POST) | `hv/delete.xml` | Modal |
| `/form/` | `FormView` (GET+POST) | `hv/form.xml` | Página |
| `/login/` | `LoginView` (GET+POST) | `hv/login.xml` | Página |
| `/profile/` | `ProfileView` | `hv/profile.xml` | Página (tab) |
| `/profile/edit/` | `ProfileEditView` (GET+POST) | `hv/profile_edit.xml` | Página |
| `/settings/` | `SettingsView` | `hv/settings.xml` | Página |
| `/about/` | `AboutView` | `hv/about.xml` | Página |
| `/logout/` | `LogoutView` (GET+POST) | `hv/logout.xml` | Página |

### Tipos de View

| Tipo | Uso |
|------|-----|
| `TemplateView` | Telas somente GET, sem lógica complexa |
| `View` com `get()`/`post()` | Telas com formulário e submissão POST |

### CSRF Exempt

Aplicado em: `FormView`, `LoginView`, `ShareView`, `DeleteView`, `ProfileEditView`, `LogoutView`

### Contexto comum das views

Todas as views fornecem `base_url` no contexto (via `_base_url()` helper).

Views com `show_back: True`: `DetailView`, `FormView`, `LoginView`, `SettingsView`,
`AboutView`, `ShareView`, `DeleteView`, `ProfileEditView`, `LogoutView`

---

## 11. Referência de Templates

### Templates principais (17 arquivos)

| Arquivo | Descrição |
|---------|-----------|
| `base.xml` | Template base: `<doc>`, `<screen>`, header, loading screens |
| `index.xml` | Navigator principal: stack → tab navigator (3 rotas) |
| `home.xml` | Dashboard com cards de navegação e atualizações |
| `list.xml` | Lista agrupada com pull-to-refresh + infinite scroll |
| `list_items.xml` | Fragmento `<items>` para infinite scroll |
| `detail.xml` | Detalhes do item com ações (editar, compartilhar, excluir) |
| `form.xml` | Formulário com validação server-side |
| `login.xml` | Tela de login |
| `profile.xml` | Perfil do usuário com menu e logout |
| `profile_edit.xml` | Edição de perfil |
| `settings.xml` | Configurações (switches, navegação) |
| `about.xml` | Sobre o app |
| `share.xml` | Compartilhamento de item |
| `delete.xml` | Confirmação de exclusão (modal) |
| `logout.xml` | Confirmação de logout |

### Includes (7 arquivos)

| Arquivo | Descrição |
|---------|-----------|
| `header.xml` | Header com botão voltar condicional |
| `header_styles.xml` | Estilos do header |
| `tabbar.xml` | Bottom tab bar (3 itens) |
| `tabbar_styles.xml` | Estilos do tab bar |
| `loading_pushed.xml` | Loading screen para navegação push |
| `loading_modal.xml` | Loading screen para modal |
| `loading_reload.xml` | Loading screen para reload |

### Blocos do base.xml

| Bloco | Onde é usado |
|-------|-------------|
| `{% block styles %}` | Todas as telas (obrigatório) |
| `{% block body %}` | List (sobrescreve estrutura do body) |
| `{% block container %}` | Conteúdo abaixo do header |
| `{% block tab_bar %}` | Home, List, Profile |
| `{% block custom_screen %}` | Telas extras no `<doc>` |
| `{% block custom_ns %}` | Namespaces adicionais no `<doc>` |

---

## 12. Testes

### Estrutura dos testes

```python
class HyperviewViewsTestCase(TestCase):
    def test_index(self):
        url = reverse("hv:index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")

    def test_form_post_valid(self):
        url = reverse("hv:form")
        response = self.client.post(url, {
            "name": "Teste", "email": "teste@email.com", "phone": "12345",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "sucesso")
```

### Comandos

```bash
# Executar todos os testes Hyperview
docker compose exec web python manage.py test hv

# Executar teste específico
docker compose exec web python manage.py test hv.tests.HyperviewViewsTestCase.test_form_post_valid
```

### Boas práticas de teste

- Usar `reverse("hv:nome")` para URLs, nunca hardcoded
- Verificar `status_code == 200` e `Content-Type == "application/xml"`
- Testar cenários de POST com dados válidos e inválidos
- Testar CSRF exemption (POST sem token CSRF)

---

## 13. Armadilhas Comuns e Debugging

### 13.1. `<list>` dentro de ScrollView

**Problema**: FlatList dentro de ScrollView → erro React Native.
**Solução**: `<body scroll="false">` sempre em telas com `<list>`.

### 13.2. Keys duplicadas com `regroup`

**Problema**: Headers de categoria se repetem entre páginas no infinite scroll.
**Solução**: Prefixar keys com `p{{ page }}`:

```xml
<item key="header-p{{ page }}-{{ grupo.grouper }}">
```

### 13.3. Estilos fora de `<styles>`

**Problema**: `<style>` solto no `<body>` — não é aplicado.
**Solução**: Todos os `<style>` devem estar dentro de `<styles>` que está dentro de `<screen>`.

### 13.4. Tab bar não aparece

**Problema**: Esquecer de incluir `{% include "hv/includes/tabbar.xml" %}` na tela de tab.
**Solução**: Incluir no bloco `{% block tab_bar %}` de cada tela de tab.

### 13.5. Navegação entre tabs não funciona

**Problema**: `navigation:route` no tab bar não casa com nenhum `nav-route`.
**Solução**: O valor de `navigation:route` deve ser exatamente o `id` do `<nav-route>` no `index.xml`.

### 13.6. href-style vs style

**Problema**: Estilos de layout (flex) não funcionam em elemento com `href`.
**Solução**: Elementos com `href` recebem wrapper tappable. Estilos de layout
devem ir no wrapper via `href-style`, não no elemento via `style`.

### 13.7. CSRF token ausente

**Problema**: POST do app mobile rejeitado por CSRF.
**Solução**: `@method_decorator(csrf_exempt, name="dispatch")` — correto para
APIs mobile que não usam cookies de sessão.

### 13.8. Content-Type errado

**Problema**: Hyperview client não renderiza a tela.
**Solução**: Verificar se a view retorna `content_type="application/xml"`.

### 13.9. Namespaces faltando

**Problema**: Custom elements não reconhecidos.
**Solução**: Incluir namespaces obrigatórios no `<doc>`:

```xml
<doc xmlns="https://hyperview.org/hyperview"
     xmlns:navigation="https://hyperview.org/navigation"
     xmlns:safe-area="https://hyperview.org/safe-area">
```

### 13.10. `regroup` sem ordenação prévia

**Problema**: Itens não agrupados corretamente, chaves duplicadas.
**Solução**: Ordenar a lista pelo campo de agrupamento antes do `regroup`:

```python
items.sort(key=lambda x: (x["category"], x["id"]))
```

### 13.11. Debugging no cliente

Em modo `__DEV__`, o console do React Native registra:
- Elemento que captura eventos (`on-event` trigger)
- Elemento que dispara eventos (`dispatch-event` action)

---

## 14. Referências e Links

### Documentação oficial

| Recurso | URL |
|---------|-----|
| Site oficial | https://hyperview.org |
| Documentação completa | https://hyperview.org/docs/reference_index |
| Guia de navegação | https://hyperview.org/docs/guide_navigation |
| Exemplo infinite scroll | https://hyperview.org/docs/example_infinite_scroll |
| Exemplo navegação | https://hyperview.org/docs/example_navigation |
| Exemplo pull-to-refresh | https://hyperview.org/docs/example_pull_to_refresh |
| Exemplo live demo | https://hyperview.org/docs/example_live |
| Behavior attributes | https://hyperview.org/docs/reference_behavior_attributes |
| Referência de style | https://hyperview.org/docs/reference_style |

### Repositórios

| Recurso | URL |
|---------|-----|
| Hyperview (GitHub) | https://github.com/instawork/hyperview |
| Demo app + backend | https://github.com/instawork/hyperview/tree/master/demo |
| Schema XSD | https://github.com/instawork/hyperview/tree/master/schema |

### Especificações HXML (schema)

Local: `/home/mcsilva/Workspaces/hyperview/schema/`

| Arquivo | Conteúdo |
|---------|----------|
| `hyperview.xsd` | Ações de behavior (push, new, back, replace, etc.) |
| `core.xsd` | Elementos, atributos, tipos de dados, estilos |
| `alert.xsd` | Atributos de alert behavior |
| `scroll.xsd` | Atributos de scroll behavior |

### React Native

| Recurso | URL |
|---------|-----|
| Layout Props | https://facebook.github.io/react-native/docs/layout-props |
| View Style Props | https://facebook.github.io/react-native/docs/view-style-props |
| Text Style Props | https://facebook.github.io/react-native/docs/text-style-props |
| Image Style Props | https://facebook.github.io/react-native/docs/image-style-props |
| React Navigation | https://reactnavigation.org |

### Dependências do Hyperview Client

| Peer Dependency | Versão mínima |
|----------------|:------------:|
| react | 18.3.1 |
| react-native | 0.76.7 |
| @react-navigation/native | 6.1.6 |
| @react-navigation/stack | 6.3.16 |
| @react-navigation/bottom-tabs | 6.5.7 |
| react-native-gesture-handler | 2.20.2 |
| react-native-safe-area-context | 4.12.0 |
| react-native-webview | 13.12.5 |
| @react-native-community/datetimepicker | 8.2.0 |
| @react-native-picker/picker | 2.9.0 |

---

*Documentação gerada a partir das fontes oficiais do Hyperview
(hyperview.org, repositório instawork/hyperview), dos templates e views
do projeto django-hyperview, e das lições aprendidas durante a implementação.*
