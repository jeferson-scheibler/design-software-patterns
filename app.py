from flask import Flask, jsonify, render_template, request, send_file
import time
from abc import ABC, abstractmethod
import io # Usado para manipular dados em memória
import csv # Para criar o ficheiro CSV
from fpdf import FPDF # Para criar o ficheiro PDF

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- 1. Padrão Singleton (Permanece igual) ---
class ConfigurationManager:
    _instance = None
    _creation_time = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance._creation_time = time.strftime("%H:%M:%S")
            cls._instance.settings = {"theme": "dark", "database_url": "db.example.com"}
        return cls._instance
    def get_settings(self): return self._instance.settings
    def get_creation_time(self): return self._instance._creation_time

@app.route('/singleton')
def get_singleton_instance():
    manager = ConfigurationManager()
    return jsonify({
        "message": "Instância acessada com sucesso.",
        "creation_time": manager.get_creation_time(),
        "instance_id": id(manager)
    })


# --- 2. Padrão Factory Method (ATUALIZADO) ---
# A interface continua a mesma
class Exporter(ABC):
    @abstractmethod
    def export(self, data):
        pass

# Implementações concretas ATUALIZADAS para gerar ficheiros reais
class PDFExporter(Exporter):
    def export(self, data):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(40, 10, "Relatório Gerado via Factory Pattern")
        pdf.ln(10) # Pular linha
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, f"Este é um relatório sobre: {data}")
        # Retorna o PDF como uma sequência de bytes
        return pdf.output(dest='S')

class CSVExporter(Exporter):
    def export(self, data):
        # Usamos io.StringIO para criar o CSV em memória
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escreve o cabeçalho e os dados
        writer.writerow(["Assunto do Relatório", "Data de Geração"])
        writer.writerow([data, time.strftime("%Y-%m-%d")])
        
        # Pega o conteúdo e o converte para bytes
        return output.getvalue().encode('utf-8')

# A Fábrica continua a mesma
def get_exporter(format_type):
    if format_type == 'pdf':
        return PDFExporter()
    if format_type == 'csv':
        return CSVExporter()
    raise ValueError("Formato de exportação desconhecido.")

# Rota da API ATUALIZADA para enviar o ficheiro
@app.route('/factory/<export_type>')
def use_factory(export_type):
    try:
        data_to_export = "Relatório de Vendas Mensais"
        exporter = get_exporter(export_type)
        
        # Gera os bytes do ficheiro (PDF ou CSV)
        file_bytes = exporter.export(data_to_export)
        
        # Prepara o ficheiro para ser enviado
        buffer = io.BytesIO(file_bytes)
        filename = f"relatorio.{export_type}"
        mimetype = 'application/pdf' if export_type == 'pdf' else 'text/csv'
        
        # Usa send_file para enviar o ficheiro para o browser
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- 3. Padrão Observer (Permanece igual) ---
class NewsAgency:
    def __init__(self): self._observers = []; self.latest_news = ""
    def subscribe(self, observer): self._observers.append(observer)
    def notify(self): 
        for observer in self._observers: observer.update(self.latest_news)
    def publish_news(self, news): self.latest_news = news; self.notify()

class NewsChannel:
    def __init__(self, name): self.name = name; self.inbox = "Ainda sem notícias..."
    def update(self, news): self.inbox = f"URGENTE: {news}"

news_agency = NewsAgency()
channel_A = NewsChannel("Canal A"); channel_B = NewsChannel("Canal B")
news_agency.subscribe(channel_A); news_agency.subscribe(channel_B)

@app.route('/observer/publish', methods=['POST'])
def publish_to_observers():
    data = request.get_json()
    news_title = data.get('title', 'Notícia sem título')
    news_agency.publish_news(news_title)
    return jsonify({"message": f"Notícia '{news_title}' publicada."})

@app.route('/observer/status')
def get_observer_status():
    return jsonify({"channel_A": channel_A.inbox, "channel_B": channel_B.inbox})


# --- Rota Principal que carrega a página HTML ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)