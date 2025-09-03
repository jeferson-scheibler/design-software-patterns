from flask import Flask, jsonify, render_template, request
import time

# --- Configuração do Flask ---
# 'templates' é onde o Flask procura por arquivos HTML.
# 'static' é para arquivos como CSS e JS.
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- 1. Padrão Singleton ---
# Pense nisso como o "Gerente Geral". Só pode existir um.
# Ele guarda informações importantes que todos podem precisar acessar.

class ConfigurationManager:
    _instance = None
    _creation_time = None

    def __new__(cls):
        if cls._instance is None:
            print("Criando a ÚNICA instância do ConfigurationManager.")
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance._creation_time = time.strftime("%H:%M:%S")
            # Configurações que seriam carregadas de um arquivo, por exemplo
            cls._instance.settings = {
                "theme": "dark",
                "database_url": "db.example.com"
            }
        return cls._instance

    def get_settings(self):
        return self.settings

    def get_creation_time(self):
        return self._creation_time

# Rota da API para o Singleton
@app.route('/singleton')
def get_singleton_instance():
    manager = ConfigurationManager()
    return jsonify({
        "message": "Instância acessada com sucesso.",
        "creation_time": manager.get_creation_time(),
        "settings": manager.get_settings(),
        "instance_id": id(manager) # 'id' é o endereço de memória, prova que é o mesmo objeto
    })


# --- 2. Padrão Factory Method ---
# Pense nisso como uma "Montadora de Veículos". Você pede um "carro" ou uma "moto",
# e a montadora sabe exatamente como construir cada um, te entregando o produto final pronto.

from abc import ABC, abstractmethod

# A interface (contrato) que todo exportador deve seguir
class Exporter(ABC):
    @abstractmethod
    def export(self, data):
        pass

# Implementações concretas
class PDFExporter(Exporter):
    def export(self, data):
        return f"Exportando '{data}' para o arquivo PDF."

class CSVExporter(Exporter):
    def export(self, data):
        return f"Exportando '{data}' para a planilha CSV."

# A Fábrica que decide qual classe criar
def get_exporter(format_type):
    if format_type == 'pdf':
        return PDFExporter()
    if format_type == 'csv':
        return CSVExporter()
    raise ValueError("Formato de exportação desconhecido.")

# Rota da API para o Factory
@app.route('/factory/<export_type>')
def use_factory(export_type):
    try:
        data_to_export = "Relatório de Vendas Mensais"
        exporter = get_exporter(export_type)
        result = exporter.export(data_to_export)
        return jsonify({"message": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- 3. Padrão Observer ---
# Pense nisso como se inscrever em um "Canal do YouTube". O canal é o "Subject".
# Você e outros inscritos são os "Observers". Quando um vídeo novo sai,
# o YouTube notifica todo mundo automaticamente.

class NewsAgency: # O Subject (o canal do YouTube)
    def __init__(self):
        self._observers = []
        self.latest_news = ""

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self.latest_news)

    def publish_news(self, news):
        self.latest_news = news
        self.notify()

class NewsChannel: # O Observer (o inscrito)
    def __init__(self, name):
        self.name = name
        self.inbox = "Ainda sem notícias..."

    def update(self, news):
        self.inbox = f"URGENTE: {news}"

# Como o servidor web não guarda estado entre requisições, vamos criar as instâncias aqui
# para que elas "vivam" enquanto o servidor estiver rodando.
news_agency = NewsAgency()
channel_A = NewsChannel("Canal A")
channel_B = NewsChannel("Canal B")
news_agency.subscribe(channel_A)
news_agency.subscribe(channel_B)

# Rota da API para o Observer
@app.route('/observer/publish', methods=['POST'])
def publish_to_observers():
    data = request.get_json()
    news_title = data.get('title', 'Notícia sem título')
    news_agency.publish_news(news_title)
    return jsonify({"message": f"Notícia '{news_title}' publicada para todos os inscritos."})

@app.route('/observer/status')
def get_observer_status():
    return jsonify({
        "channel_A": channel_A.inbox,
        "channel_B": channel_B.inbox,
    })


# --- Rota Principal que carrega a página HTML ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 'debug=True' faz o servidor reiniciar automaticamente quando você salva o arquivo
    app.run(debug=True)