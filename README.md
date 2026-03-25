# MCP Clint CRM

Servidor MCP (Model Context Protocol) para integração com o [Clint CRM](https://clint.digital/). Gerencie contatos, negócios, tags, organizações e toda a configuração do seu CRM diretamente através de assistentes de IA compatíveis com MCP.

> **[English version available here](README-English.md)**

---

> **Aviso:** Este é um projeto **open source** mantido pela comunidade. **Não é uma ferramenta oficial** do Clint CRM. Utilize por sua conta e risco. Consulte a [documentação oficial da API do Clint CRM](https://clint-api.readme.io/reference/get_contacts) para informações sobre a API.

---

## Pré-requisitos

- **Plano Elite do Clint CRM** — O acesso à API requer o plano Elite ativo na sua conta Clint.
- **API Key do Clint CRM** — Chave de acesso gerada na sua conta Clint para autenticação na API.
- **Python 3.14+** — O projeto utiliza recursos modernos do Python.
- **UV** — Gerenciador de pacotes e ambientes virtuais para Python. [Instalar UV](https://docs.astral.sh/uv/getting-started/installation/).

### Links Úteis

- [Documentação da API do Clint CRM](https://clint-api.readme.io/reference/get_contacts)
- [Clint CRM](https://clint.digital/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

## Instalação e Configuração

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/mcp-clint-crm.git
cd mcp-clint-crm
```

### 2. Configurar a API Key

Crie um arquivo `.env` na raiz do projeto:

```env
CLINT_API_KEY=sua_chave_api_aqui
```

### 3. Instalar dependências

```bash
uv sync
```

### 4. Executar o servidor (modo standalone)

```bash
uv run src/server.py
```

---

## Configuração via stdio (Claude Desktop, Cursor, etc.)

Para utilizar o servidor MCP com assistentes de IA que suportam o protocolo MCP via **stdio**, adicione a seguinte configuração no arquivo de configuração do seu cliente MCP.

### Claude Desktop

No arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clint-crm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/caminho/absoluto/para/mcp-clint-crm",
        "src/server.py"
      ],
      "env": {
        "CLINT_API_KEY": "sua_chave_api_aqui"
      }
    }
  }
}
```

### Cursor

No arquivo de configuração MCP do Cursor (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "clint-crm": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/caminho/absoluto/para/mcp-clint-crm",
        "src/server.py"
      ],
      "env": {
        "CLINT_API_KEY": "sua_chave_api_aqui"
      }
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add clint-crm -- uv run --directory /caminho/absoluto/para/mcp-clint-crm src/server.py
```

> **Nota:** Substitua `/caminho/absoluto/para/mcp-clint-crm` pelo caminho real do projeto no seu sistema. A variável `CLINT_API_KEY` pode ser definida no `.env` do projeto ou diretamente na configuração `env` do cliente MCP.

---

## Tools Disponíveis

O servidor expõe **27 tools** organizadas por domínio. Cada tool é anotada com metadados de segurança (somente leitura / destrutiva) para que o assistente de IA solicite confirmação antes de executar ações perigosas.

### Resumo

| Domínio | Tools | Operações |
|---------|-------|-----------|
| **Contatos** | 7 | Listar, buscar, criar, atualizar, deletar, adicionar/remover tags |
| **Negócios (Deals)** | 5 | Listar, buscar, criar, atualizar, deletar |
| **Tags** | 4 | Listar, buscar, criar, deletar |
| **Organizações** | 2 | Buscar, atualizar |
| **Origens** | 2 | Listar, buscar |
| **Grupos** | 2 | Listar, buscar |
| **Usuários** | 2 | Listar, buscar |
| **Status de Perda** | 2 | Listar, buscar |
| **Conta** | 1 | Listar campos personalizados |

---

### Contatos

#### `list_contacts`
Lista todos os contatos do CRM com filtros opcionais. Retorna até 1000 contatos por chamada com suporte a paginação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |
| `name` | `str` | Filtrar por nome do contato |
| `phone` | `str` | Filtrar por telefone (sem código do país) |
| `email` | `str` | Filtrar por e-mail |
| `tag_names` | `str` | Filtrar por tags (separadas por vírgula) |
| `origin_id` | `str` | Filtrar por origem (use `list_origins` para obter IDs) |

#### `get_contact`
Retorna os detalhes completos de um contato pelo UUID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `uuid` | `str` | ID do contato (obtenha via `list_contacts`) |

#### `create_contact`
Cria um novo contato no CRM.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `name` | `str` | Nome do contato (**obrigatório**) |
| `ddi` | `str` | Código DDI do país |
| `phone` | `str` | Telefone |
| `email` | `str` | E-mail |
| `username` | `str` | Nome de usuário |
| `fields` | `dict \| str` | Campos personalizados (JSON). Use `list_fields` para descobrir os campos disponíveis |

#### `update_contact`
Atualiza um contato existente. Envie apenas os campos que deseja alterar.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `uuid` | `str` | ID do contato (**obrigatório**) |
| `name` | `str` | Novo nome |
| `ddi` | `str` | Novo DDI |
| `phone` | `str` | Novo telefone |
| `email` | `str` | Novo e-mail |
| `username` | `str` | Novo nome de usuário |
| `fields` | `dict \| str` | Campos personalizados (JSON) |

#### `delete_contact`
Remove permanentemente um contato. **Ação destrutiva** — requer confirmação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `uuid` | `str` | ID do contato (**obrigatório**) |

#### `add_tags`
Adiciona uma ou mais tags a um contato.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `uuid` | `str` | ID do contato (**obrigatório**) |
| `tag_names` | `list[str]` | Lista de nomes de tags para adicionar |

#### `remove_tags`
Remove uma tag de um contato. **Ação destrutiva** — requer confirmação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `uuid` | `str` | ID do contato (**obrigatório**) |
| `tag_name` | `str` | Nome da tag para remover |

---

### Negócios (Deals)

#### `list_deals`
Lista negócios com filtros avançados por data, status, usuário e tags. Retorna até 1000 negócios por chamada.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |
| `created_at_start` | `str` | Data inicial de criação (ISO 8601) |
| `created_at_end` | `str` | Data final de criação (ISO 8601) |
| `updated_at_start` | `str` | Data inicial de atualização (ISO 8601) |
| `updated_at_end` | `str` | Data final de atualização (ISO 8601) |
| `user_email` | `str` | Filtrar por e-mail do usuário responsável |
| `phone` | `str` | Filtrar por telefone |
| `email` | `str` | Filtrar por e-mail |
| `tag_names` | `str` | Filtrar por tags (separadas por vírgula) |
| `status` | `str` | Status: `OPEN`, `WON` ou `LOST` (padrão: `OPEN`) |
| `won_at_start` | `str` | Data inicial de ganho (ISO 8601) |
| `won_at_end` | `str` | Data final de ganho (ISO 8601) |
| `lost_at_start` | `str` | Data inicial de perda (ISO 8601) |
| `lost_at_end` | `str` | Data final de perda (ISO 8601) |
| `stage_id` | `str` | Filtrar por etapa do funil |

#### `get_deal`
Retorna os detalhes completos de um negócio pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID do negócio (obtenha via `list_deals`) |

#### `create_deal`
Cria um novo negócio no CRM. Requer obrigatoriamente uma origem.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `origin_id` | `str` | ID da origem (**obrigatório**, use `list_origins`) |
| `name` | `str` | Nome do contato |
| `phone` | `str` | Telefone |
| `email` | `str` | E-mail |
| `username` | `str` | Nome de usuário |
| `value` | `float` | Valor do negócio |
| `stage_id` | `str` | ID da etapa do funil |
| `user_id` | `str` | ID do usuário responsável |
| `contact_id` | `str` | ID do contato existente |
| `fields` | `dict \| str` | Campos personalizados (JSON) |

#### `update_deal`
Atualiza um negócio existente, incluindo mudanças de status e etapa do funil.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID do negócio (**obrigatório**) |
| `name` | `str` | Novo nome |
| `phone` | `str` | Novo telefone |
| `email` | `str` | Novo e-mail |
| `value` | `float` | Novo valor |
| `stage_id` | `str` | Nova etapa do funil |
| `status` | `str` | Novo status: `OPEN`, `WON` ou `LOST` |
| `user_id` | `str` | Novo usuário responsável |
| `origin_id` | `str` | Nova origem |
| `fields` | `dict \| str` | Campos personalizados (JSON) |

#### `remove_deal`
Remove permanentemente um negócio. **Ação destrutiva** — requer confirmação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID do negócio (**obrigatório**) |

---

### Tags

#### `list_tags`
Lista todas as tags com filtro opcional por nome.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |
| `name` | `str` | Filtrar por nome da tag |

#### `get_tag`
Retorna os detalhes de uma tag pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID da tag (obtenha via `list_tags`) |

#### `create_tag`
Cria uma nova tag com nome e cor.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `name` | `str` | Nome da tag (**obrigatório**) |
| `color` | `str` | Cor em hexadecimal (padrão: `#f44336`) |

**Cores disponíveis:**

| Cor | Código |
|-----|--------|
| Vermelho | `#f44336` |
| Rosa | `#e91e63` |
| Roxo | `#9c27b0` |
| Roxo escuro | `#673ab7` |
| Azul | `#2196f3` |
| Laranja | `#faa200` |
| Marrom | `#795548` |
| Cinza azulado | `#607d8b` |

#### `delete_tag`
Remove permanentemente uma tag. **Ação destrutiva** — requer confirmação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID da tag (**obrigatório**) |

---

### Organizações

#### `get_organization`
Retorna os detalhes de uma organização pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID da organização |

#### `update_organization`
Atualiza uma organização existente. **Ação destrutiva** — requer confirmação.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID da organização (**obrigatório**) |
| `name` | `str` | Novo nome |
| `custom_fields` | `dict \| str` | Campos personalizados (JSON) |

---

### Origens

#### `list_origins`
Lista as origens filtradas por grupo. Cada origem contém suas etapas (stages) do funil.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `group_id` | `str` | ID do grupo (**obrigatório**, use `list_groups`) |
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |

#### `get_origin`
Retorna os detalhes de uma origem pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID da origem (obtenha via `list_origins`) |

---

### Grupos

#### `list_groups`
Lista todos os grupos disponíveis no CRM.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |

#### `get_group`
Retorna os detalhes de um grupo pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID do grupo (obtenha via `list_groups`) |

---

### Usuários

#### `list_users`
Lista todos os usuários do sistema.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |

#### `get_user`
Retorna os detalhes de um usuário pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID do usuário (obtenha via `list_users`) |

---

### Status de Perda

#### `list_lost_status`
Lista todos os motivos de perda de negócios.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `offset` | `int` | Deslocamento para paginação (padrão: 0) |

#### `get_lost_status`
Retorna os detalhes de um status de perda pelo ID.

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `id` | `str` | ID do status (obtenha via `list_lost_status`) |

---

### Conta

#### `list_fields`
Lista todos os campos personalizados configurados na conta. **Use esta tool antes de criar ou atualizar contatos e negócios** para descobrir os campos disponíveis e seus tipos.

Não requer parâmetros adicionais.

---

## Campos Personalizados (Custom Fields)

Contatos, negócios e organizações suportam campos personalizados. O fluxo recomendado é:

1. Chame `list_fields` para descobrir os campos disponíveis, seus nomes-chave, tipos e opções.
2. Ao criar ou atualizar um registro, passe os campos no parâmetro `fields` como um objeto JSON:

```json
{
  "campo_personalizado_1": "valor",
  "campo_personalizado_2": 123
}
```

Os campos podem ser passados como `dict` do Python ou como uma string JSON válida.

---

## Paginação

Todas as operações de listagem retornam até **1000 registros** por chamada. Para obter mais resultados, use o parâmetro `offset`:

- Primeira chamada: `offset=0` (padrão)
- Segunda chamada: `offset=1000`
- Terceira chamada: `offset=2000`
- E assim por diante...

O servidor retorna o total de registros disponíveis e sugere o próximo offset quando há mais dados.

---

## Stack Técnica

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| Python | 3.14+ | Linguagem principal |
| FastMCP | 3.1.1+ | Framework MCP |
| httpx | 0.28.1+ | Cliente HTTP assíncrono |
| Pydantic | 2.12.5+ | Validação de dados e modelos |
| UV | - | Gerenciador de pacotes |

---

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests. Se você está utilizando o projeto, favor considere marcar a estrela ⭐️.

---

## Licença

Este projeto é open source. Consulte o arquivo de licença para mais detalhes.

---

<sub>Este projeto não é afiliado ao Clint CRM.</sub>
