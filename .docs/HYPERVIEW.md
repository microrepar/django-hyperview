# Hyperview - Framework XML Thin-Client para Mobile

## Visão Geral

**Hyperview** é um framework open-source desenvolvido pela **Instawork** que traz os benefícios do desenvolvimento thin-client e HATEOAS (Hypermedia as the Engine of Application State) para aplicativos móveis nativos.

### Stack Tecnológica

- **Backend**: Serve HXML (Hyperview XML) descrevendo layouts de apps móveis
- **Cliente**: React Native - renderiza HXML cross-platform
- **Formato**: XML-based (HXML) para descrever UI, estilos e comportamentos
- **Conceito**: Server-driven UI - atualizações sem release na app store

---

## Arquitetura

### Modelo Thin-Client

Assim como um navegador web renderiza HTML vindo do servidor, o cliente Hyperview renderiza HXML:

```
┌─────────────────┐     HTTP/XML      ┌──────────────────┐
│   Django/Laravel│ ──────────────────> │  Hyperview RN    │
│   Backend       │     Serve HXML      │  Client App      │
│                 │ <────────────────── │                  │
└─────────────────�     User Actions     └──────────────────┘
```

**Vantagens:**
- Atualizações de UI sem deploy na app store
- Lógica de navegação controlada pelo servidor
- A/B testing de UI sem alterar o app
- Rollbacks instantâneos

---

## Componentes

### 1. HXML (Hyperview XML)

Formato XML para descrever UIs móveis nativas com:

- **Estrutura**: elementos de layout
- **Estilo**: sistema de estilos próprio (sem CSS)
- **Comportamentos**: ações interativas via atributos
- **Namespace**: `https://hyperview.org/hyperview`

### 2. Hyperview Client

Biblioteca React Native que:
- Faz fetch de HXML de uma URL entrypoint
- Renderiza o HXML nativamente (iOS e Android)
- Manipula comportamentos que disparam novas requisições
- Suporta elementos e comportamentos customizados

---

## Estrutura do HXML

### Elemento Raiz: `<doc>`

Diferente do HTML (um `<html>` = uma página), o HXML permite múltiplas telas em um `<doc>`:

```xml
<doc xmlns="https://hyperview.org/hyperview">
  <screen id="main">
    <body>
      <text>Hello</text>
    </body>
  </screen>

  <screen id="otherScreen">
    <body>
      <text>Hello again</text>
    </body>
  </screen>
</doc>
```

### Estrutura de uma Screen

```xml
<screen id="main">
  <styles>
    <!-- Definições de estilo -->
  </styles>

  <header>
    <!-- Cabeçalho da tela -->
  </header>

  <body id="Body">
    <!-- Conteúdo principal -->
  </body>
</screen>
```

---

## Elementos Disponíveis

### Elementos de Display

| Elemento | Descrição | Equivalente HTML |
|----------|-----------|------------------|
| `<doc>` | Elemento raiz, contém múltiplas telas | `<html>` |
| `<screen>` | Tela individual do app | N/A |
| `<header>` | Cabeçalho da tela | `<header>` |
| `<body>` | Corpo da tela | `<body>` |
| `<view>` | Container básico (suporta flex) | `<div>` |
| `<text>` | Conteúdo textual | Qualquer elemento |
| `<image>` | Imagens | `<img>` |
| `<list>` | Lista eficiente de itens | `<ul>`/recyclerview |
| `<section-list>` | Lista agrupada por seções | N/A |
| `<spinner>` | Indicador de atividade | `<span class="loader">` |
| `<web-view>` | WebView embutida | `<iframe>` |

### Elementos de Input

| Elemento | Descrição |
|----------|-----------|
| `<form>` | Agrupa inputs para serialização |
| `<text-field>` | Input de texto single-line |
| `<select-single>` | Seleção única (radio-like) |
| `<select-multiple>` | Seleção múltipla (checkbox-like) |
| `<option>` | Opção dentro de select |
| `<picker-field>` | Picker (iOS-style dropdown) |
| `<picker-item>` | Item do picker |
| `<switch>` | Toggle/switch |
| `<date-field>` | Seleção de data |

### Elementos de Estilo

| Elemento | Descrição |
|----------|-----------|
| `<styles>` | Agrupa regras de estilo |
| `<style>` | Regra de estilo individual |
| `<modifier>` | Variação de estilo para estados |

### Elementos de Navegação

| Elemento | Descrição |
|----------|-----------|
| `<navigator>` | Define stack/tab navigator |
| `<nav-route>` | Rota individual no navigator |

---

## Comportamentos (Behaviors)

### Atributos de Comportamento

Ações que acontecem em resposta a triggers do usuário:

| Atributo | Descrição |
|----------|-----------|
| `href` | URL para navegar ou elemento id local |
| `action` | Tipo de ação (push, new, replace, append, etc.) |
| `target` | ID do elemento alvo da ação |
| `trigger` | Quando disparar (press, longPress, visible, load, refresh) |

### Actions Disponíveis

| Action | Descrição |
|--------|-----------|
| `push` | Nova tela na navegação stack |
| `new` | Abre como modal |
| `replace` | Substitui elemento com resposta |
| `append` | Adiciona resposta ao elemento |
| `reload` | Recarrega a tela atual |

### Exemplo de Behaviors

```xml
<body id="Body">
  <list>
    <!-- Pull-to-refresh -->
    <behavior trigger="refresh" href="/news" action="replace" target="Body" />

    <item key="1" href="/news/1">
      <!-- Press normal -->
      <behavior trigger="press" action="push" href="/news/1" />
      <!-- Long press -->
      <behavior trigger="longPress" action="new" href="/news/1/settings" />
      <text>Story 1</text>
    </item>
  </list>
</body>
```

### Múltiplos Behaviors

```xml
<text href="/page2">
  <behavior href="/page3" trigger="press" />
  <behavior href="/page2" trigger="longPress" />
  <behavior href="/page4" trigger="refresh" />
  Many things can happen!
</text>
```

---

## Sistema de Estilos

### Diferenças do CSS

**HXML não usa CSS**. Possui sistema próprio baseado em IDs:

```xml
<!-- CSS (não usado no HXML) -->
<style>
  .header { font-size: 16; color: red; }
</style>

<!-- HXML -->
<styles>
  <style id="Header" fontSize="16" color="red" />
</styles>
```

### Seleção por ID

Estilos são aplicados por referência ao ID:

```xml
<styles>
  <style id="Center" textAlign="center" />
  <style id="H2" fontSize="16" />
  <style id="MainHeader" color="blue" />
</styles>

<body>
  <view>
    <text style="H2 Center MainHeader">Hello</text>
  </view>
</body>
```

### Sem Cascata

Diferente do CSS, estilos **não cascata** para filhos:

```xml
<style id="Main" color="red" />

<body style="Main">
  <view>
    <!-- Este texto NÃO será vermelho -->
    <text>Not red</text>
  </view>
</body>
```

### Modifiers (Estados)

Estilos para estados específicos (pressed, selected, etc.):

```xml
<style id="Button" backgroundColor="#EEE" padding="24">
  <modifier pressed="true">
    <style backgroundColor="#AAA" />
  </modifier>
</style>

<style id="ButtonLabel" color="#000">
  <modifier pressed="true">
    <style color="red" />
  </modifier>
</style>
```

---

## HXML vs HTML

| Aspecto | HTML | HXML |
|---------|------|------|
| **Formatação** | Permissivo | XML estrito |
| **Elemento raiz** | `<html>` | `<doc>` (múltiplas telas) |
| **Container** | `<div>` | `<view>` |
| **Texto** | Qualquer elemento | Apenas `<text>` |
| **Forms** | `<input type="checkbox">` | `<select-single>/<select-multiple>` com `<option>` |
| **href** | Apenas em `<a>` | Em quase todos elementos |
| **Estilo** | CSS | Sistema próprio |
| **Cascata** | Sim | Não |
| **Estados** | `:hover`, `:active` | `<modifier>` |

---

## Instalação e Setup

### Pré-requisitos

- Node.js e yarn
- React Native ou Expo
- Backend que sirva HXML

### Passo 1: Clone o Repositório

```bash
git clone https://github.com/instawork/hyperview
```

O repositório contém:
- Cliente React Native
- Servidor XML de exemplo
- Demo Expo
- Documentação de referência

### Passo 2: Instale Dependências

```bash
cd demo/
yarn
```

### Passo 3: Execute o Servidor Demo

```bash
yarn server
```

Servidor escuta na porta 8085. Acesse:
`http://0.0.0.0:8085/hyperview/public/index.xml`

### Passo 4: Execute no iOS

```bash
yarn ios
```

### Passo 5: Execute no Android

```bash
yarn android
```

### Passo 6: Execute em Device Físico

```bash
cd demo
BASE_URL="http://X.X.X.X:8085" yarn start
```

Escaneie o QR code com o app Expo.

---

## Backend Django

Para integrar Hyperview com Django:

```python
# views.py
from django.http import HttpResponse

def hyperview_screen(request):
    hxml = '''<?xml version="1.0" encoding="UTF-8"?>
    <doc xmlns="https://hyperview.org/hyperview">
      <screen id="main">
        <styles>
          <style id="Title" fontSize="24" fontWeight="bold" />
        </styles>
        <body>
          <text style="Title">Hello from Django!</text>
        </body>
      </screen>
    </doc>'''
    return HttpResponse(hxml, content_type='application/xml')

# urls.py
urlpatterns = [
    path('api/mobile/', hyperview_screen),
]
```

---

## Recursos Avançados

### Custom Elements

Registrar elementos HXML customizados com componentes RN:

```javascript
import { Hyperview } from 'hyperview';

const customElements = {
  'my-map': MapComponent,
};

<Hyperview
  entrypointUrl="https://api.example.com/screen.xml"
  customElements={customElements}
/>
```

### Custom Behaviors

Registrar callbacks customizados:

```javascript
const customBehaviors = {
  'my-action': (element, behavior) => {
    // Lógica customizada
  },
};

<Hyperview
  entrypointUrl="https://api.example.com/screen.xml"
  customBehaviors={customBehaviors}
/>
```

### Redux Integration

Disparar actions Redux via HXML:

```xml
<view xmlns:redux="https://instawork.com/hyperview-redux">
  <text>
    <behavior
      trigger="press"
      action="redux"
      redux:action="TOAST/SHOW_TOAST"
      redux:extra='{"payload":{"toast":{"message":"Hello World!"}}}'
    />
    Show Toast
  </text>
</view>
```

---

## Casos de Uso

1. **E-commerce**: Atualizar layouts de promoções sem novo release
2. **Apps de Delivery**: Modificar fluxo de pedido dinamicamente
3. **Social Media**: Testar novos layouts de feed
4. **Enterprise**: Rollback instantâneo de UIs problemáticas

---

## Referências

- **Site Oficial**: https://hyperview.org
- **GitHub**: https://github.com/instawork/hyperview
- **Criador**: Adam Stepinski (Instawork)
- **Livro**: "Hypermedia Systems" (co-autor)
- **Licença**: Open Source

### Links da Documentação

- [Introdução](https://hyperview.org/docs/guide_introduction)
- [Getting Started](https://hyperview.org/docs/guide_installation)
- [HXML vs HTML](https://hyperview.org/docs/guide_html)
- [Reference](https://hyperview.org/docs/reference_index)
- [Examples](https://hyperview.org/docs/example_index)
- [Blog](https://hyperview.org/blog/)

---

## Status do Projeto

- **Lançamento**: 2018
- **Manutenção**: Ativo (2024-2025)
- **Maturidade**: Produção na Instawork
- **Comunidade**: Crescente, discussões ativas no GitHub
