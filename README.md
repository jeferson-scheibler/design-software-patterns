# Demonstração de Design Patterns com Python e Flask

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.2%2B-black.svg)

Este repositório contém uma aplicação web desenvolvida para demonstrar a implementação prática de três padrões de projeto (Design Patterns) fundamentais. A arquitetura é baseada num backend Python com o micro-framework Flask, que expõe uma API RESTful consumida por um frontend em HTML e JavaScript.

## Padrões de Projeto Implementados

A lógica de cada padrão está implementada no backend (`app.py`) e é acessível através de endpoints específicos da API.

### 1. Singleton
- **Intenção:** Garantir que uma classe tenha apenas uma única instância e fornecer um ponto de acesso global a ela.
- **Implementação:** A classe `ConfigurationManager` em `app.py` implementa o padrão. Independentemente do número de requisições, o servidor mantém uma única instância desta classe. A rota `/singleton` demonstra que o `id()` do objeto em memória permanece o mesmo entre chamadas, confirmando a existência de uma única instância.

### 2. Factory Method
- **Intenção:** Definir uma interface para criar um objeto, mas deixar as subclasses decidirem qual classe instanciar.
- **Implementação:** A função `get_exporter(format_type)` em `app.py` atua como a Factory. Ela desacopla o código cliente das classes concretas `PDFExporter` e `CSVExporter`. O cliente simplesmente solicita um tipo de exportador (`pdf` ou `csv`) através da rota `/factory/<export_type>`, e a fábrica retorna a instância apropriada, pronta para uso.

### 3. Observer
- **Intenção:** Definir uma dependência um-para-muitos entre objetos, de modo que, quando um objeto muda de estado, todos os seus dependentes são notificados e atualizados automaticamente.
- **Implementação:** A classe `NewsAgency` (Subject) mantém uma lista de `NewsChannel` (Observers). Quando uma nova notícia é publicada através de uma requisição `POST` para a rota `/observer/publish`, o método `notify()` é invocado, atualizando o estado de todos os observers inscritos. O estado dos observers pode ser consultado via `GET` na rota `/observer/status`.

## Arquitetura do Projeto

A aplicação segue um modelo cliente-servidor:

- **Backend (Flask):**
  - `app.py`: Contém toda a lógica de negócio, a implementação dos design patterns e a definição dos endpoints da API.
  - `requirements.txt`: Lista as dependências Python do projeto.

- **Frontend (Estático):**
  - `templates/index.html`: Estrutura da página web.
  - `static/js/main.js`: Lógica do lado do cliente que realiza as chamadas `fetch` para a API do backend e atualiza a interface do utilizador com os resultados.

## Como Executar Localmente

Para executar o projeto no seu ambiente local, siga os passos abaixo.

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jeferson-scheibler/design-software-patterns.git](https://github.com/jeferson-scheibler/design-software-patterns.git)
    cd design-software-patterns
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    # Criar o ambiente
    python -m venv venv

    # Ativar no Windows
    .\venv\Scripts\activate

    # Ativar no macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    flask run
    ```

5.  **Aceda à aplicação** no seu navegador através do endereço:
    `http://127.0.0.1:5000`

## Tecnologias Utilizadas

- **Backend:** Python, Flask
- **Frontend:** HTML5, JavaScript (ES6+), Tailwind CSS