from flask import Flask, jsonify, render_template, request
from abc import ABC, abstractmethod
import time
import copy # Usado pelo Prototype
import uuid # Usado pelo Prototype

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- 1. Padrão Builder ---
# Analogia: Montar um computador customizado. O Builder guia a construção
# de um objeto complexo passo a passo, de forma organizada.

# O objeto complexo que estamos a construir
class Computer:
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.storage = None
        self.gpu = None

# A interface (contrato) do Builder
class ComputerBuilder(ABC):
    @abstractmethod
    def set_cpu(self): pass
    @abstractmethod
    def set_ram(self): pass
    @abstractmethod
    def set_storage(self): pass
    @abstractmethod
    def set_gpu(self): pass
    @abstractmethod
    def get_computer(self): pass

# Implementações concretas do Builder
class GamingComputerBuilder(ComputerBuilder):
    def __init__(self): self.computer = Computer()
    def set_cpu(self): self.computer.cpu = "Intel i9"
    def set_ram(self): self.computer.ram = 32
    def set_storage(self): self.computer.storage = "2TB NVMe"
    def set_gpu(self): self.computer.gpu = "NVIDIA RTX 4080"
    def get_computer(self): return self.computer

class OfficeComputerBuilder(ComputerBuilder):
    def __init__(self): self.computer = Computer()
    def set_cpu(self): self.computer.cpu = "Intel i5"
    def set_ram(self): self.computer.ram = 16
    def set_storage(self): self.computer.storage = "512GB SATA"
    def set_gpu(self): self.computer.gpu = "Gráficos Integrados"
    def get_computer(self): return self.computer

# O Diretor que orquestra a construção
class Director:
    def construct(self, builder: ComputerBuilder):
        builder.set_cpu()
        builder.set_ram()
        builder.set_storage()
        builder.set_gpu()

# Rota da API para o Builder
@app.route('/builder/<computer_type>')
def use_builder(computer_type):
    director = Director()
    if computer_type == 'gaming': builder = GamingComputerBuilder()
    elif computer_type == 'office': builder = OfficeComputerBuilder()
    else: return jsonify({"error": "Tipo de computador desconhecido"}), 400

    director.construct(builder)
    computer = builder.get_computer()
    
    return jsonify({
        "type": f"Computador para {computer_type.capitalize()}",
        "specs": {
            "cpu": computer.cpu, "ram_gb": computer.ram,
            "storage": computer.storage, "gpu": computer.gpu,
        }
    })


# --- 2. Padrão Prototype ---
# Analogia: Usar uma máquina de clonagem. Em vez de construir um objeto
# complexo do zero, criamos uma cópia de um "protótipo" existente.

# A classe que será clonada
class Character:
    def __init__(self, name, level, weapon, abilities):
        self.id = uuid.uuid4().hex
        self.name = name
        self.level = level
        self.weapon = weapon
        self.abilities = abilities

    def clone(self):
        # deepcopy garante uma cópia completa e independente
        return copy.deepcopy(self)

# Um "armazém" para os nossos protótipos
character_prototypes = {
    "warrior": Character("Guerreiro Protótipo", 10, "Espada Larga", ["Investida", "Golpe Poderoso"]),
    "archer": Character("Arqueiro Protótipo", 10, "Arco Longo", ["Tiro Mirado", "Chuva de Flechas"])
}

# Rota da API para o Prototype
@app.route('/prototype/<character_type>')
def use_prototype(character_type):
    prototype = character_prototypes.get(character_type)
    if not prototype: return jsonify({"error": "Tipo de personagem desconhecido"}), 400
    
    new_character = prototype.clone()
    new_character.id = uuid.uuid4().hex # Damos ao clone um novo ID único
    
    return jsonify({
        "message": f"Personagem '{character_type}' clonado com sucesso!",
        "cloned_character": {
            "id": new_character.id, "name": new_character.name, "level": new_character.level,
            "weapon": new_character.weapon, "abilities": new_character.abilities,
        },
        "prototype_id": prototype.id
    })


# --- 3. Padrão Observer ---
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