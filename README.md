# DIO-LAB-1 — E-Commerce na Cloud

REST API para um sistema de e-commerce, desenvolvida com Python/Flask e pronta para deploy em cloud.

## Funcionalidades

- **Produtos**: cadastro, listagem, atualização e remoção de produtos
- **Carrinho**: adição, atualização e remoção de itens por sessão
- **Pedidos**: criação de pedidos a partir do carrinho, atualização de status

## Tecnologias

- Python 3.12
- Flask 3
- Flask-SQLAlchemy (SQLite por padrão, compatível com PostgreSQL via `DATABASE_URL`)
- Docker

## Como executar localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente (opcional)
cp .env.example .env

# Iniciar a aplicação
python app.py
```

A API estará disponível em `http://localhost:5000`.

## Como executar com Docker

```bash
docker build -t ecommerce-api .
docker run -p 5000:5000 ecommerce-api
```

## Endpoints

### Saúde
| Método | Rota      | Descrição        |
|--------|-----------|------------------|
| GET    | /health   | Status da API    |

### Produtos
| Método | Rota                   | Descrição              |
|--------|------------------------|------------------------|
| GET    | /products/             | Listar produtos        |
| GET    | /products/\<id\>       | Obter produto          |
| POST   | /products/             | Criar produto          |
| PUT    | /products/\<id\>       | Atualizar produto      |
| DELETE | /products/\<id\>       | Remover produto        |

### Carrinho
| Método | Rota                              | Descrição              |
|--------|-----------------------------------|------------------------|
| GET    | /cart/\<session_id\>              | Ver carrinho           |
| POST   | /cart/\<session_id\>/items        | Adicionar item         |
| PUT    | /cart/\<session_id\>/items/\<id\> | Atualizar quantidade   |
| DELETE | /cart/\<session_id\>/items/\<id\> | Remover item           |
| DELETE | /cart/\<session_id\>              | Limpar carrinho        |

### Pedidos
| Método | Rota                        | Descrição              |
|--------|-----------------------------|------------------------|
| GET    | /orders/                    | Listar pedidos         |
| GET    | /orders/\<id\>              | Obter pedido           |
| POST   | /orders/                    | Criar pedido           |
| PATCH  | /orders/\<id\>/status       | Atualizar status       |

Status válidos de pedido: `pending`, `processing`, `shipped`, `delivered`, `cancelled`.

## Testes

```bash
python -m pytest tests/ -v
```

## Variáveis de Ambiente

| Variável        | Padrão                  | Descrição                        |
|-----------------|-------------------------|----------------------------------|
| `SECRET_KEY`    | `dev-secret-key`        | Chave secreta da aplicação       |
| `DATABASE_URL`  | `sqlite:///ecommerce.db`| URL de conexão com o banco       |
| `DEBUG`         | `false`                 | Modo debug                       |