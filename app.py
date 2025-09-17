from flask import Flask, jsonify, render_template, request
from abc import ABC, abstractmethod
import copy
import math

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- PATTERN 1: Flyweight ---
# Continua a otimizar o uso de memória. Ruas agora têm uma "cor" em vez de imagem.

class ElementFlyweight:
    def __init__(self, name, data, width, height):
        self._name = name
        self._data = data  # Pode ser uma URL de imagem ou uma cor
        self._width = width
        self._height = height

    def render(self, context):
        base = {"name": self._name, "data": self._data, "type": context['type']}
        if context['type'] == 'road':
            base.update({"path": context['path']})
        else:
            base.update({"x": context['x'], "y": context['y'], "width": self._width, "height": self._height})
        return base

class FlyweightFactory:
    _flyweights = {}
    def get_flyweight(self, key):
        if key not in self._flyweights:
            print(f"--- FlyweightFactory: A criar novo flyweight para '{key}' ---")
            d = ELEMENT_TYPES[key]
            self._flyweights[key] = ElementFlyweight(d['name'], d['data'], d.get('width'), d.get('height'))
        return self._flyweights[key]

# --- PATTERN 2: Memento ---
# Funciona exatamente como antes, mas agora salva o estado que pode conter objetos complexos como ruas.

class MapState:
    def __init__(self, elements): self._elements = copy.deepcopy(elements)
    def get_elements(self): return self._elements

class MapEditor:
    _elements = []
    def add_element(self, context): self._elements.append(context)
    def get_elements(self): return self._elements
    def set_elements(self, elements): self._elements = elements
    def save(self): return MapState(self._elements)
    def restore(self, memento: MapState): self._elements = memento.get_elements()

class History:
    _mementos = []
    def __init__(self, editor: MapEditor): self._editor = editor
    def save(self): self._mementos.append(self._editor.save())
    def undo(self):
        if self._mementos: self._editor.restore(self._mementos.pop())

# --- PATTERN 3: Chain of Responsibility ---
# Atualizado para validar tanto pontos (outros elementos) quanto linhas (ruas).

class Handler(ABC):
    _next_handler = None
    def set_next(self, handler): self._next_handler = handler; return handler
    def handle(self, request):
        if self._next_handler: return self._next_handler.handle(request)
        return True, "Fim da cadeia."

class BoundaryValidator(Handler):
    def handle(self, request):
        if request['type'] == 'road':
            points = request['path']
            for p in points:
                if not (0 <= p['x'] <= 500 and 0 <= p['y'] <= 300):
                    return False, "Erro: Rua fora dos limites do mapa!"
        else:
            if not (0 <= request['x'] <= 500 and 0 <= request['y'] <= 300):
                return False, "Erro: Elemento fora dos limites do mapa!"
        return super().handle(request)

class CollisionValidator(Handler):
    # Lógica de colisão simplificada para a demonstração
    def handle(self, request):
        # Esta validação poderia ser muito mais complexa, verificando interseções de linhas
        # Por agora, mantemos a simplicidade para focar nos padrões.
        return super().handle(request)

# --- PATTERN 4: Mediator ---
# Orquestra a lógica mais complexa de adicionar elementos pontuais vs. ruas.

class PlacementMediator:
    def __init__(self):
        self._fly_factory = FlyweightFactory()
        self._editor = MapEditor()
        self._history = History(self._editor)
        self._chain_root = BoundaryValidator().set_next(CollisionValidator())

    def notify(self, event, data):
        if event == "place_element":
            self._history.save()
            is_valid, message = self._chain_root.handle(data)
            if is_valid:
                self._editor.add_element(data)
                return True, "Elemento adicionado."
            self._history.undo(); return False, message
        
        elif event == "undo":
            self._history.undo(); return True, "Ação desfeita."
        
        elif event == "get_state":
            elements_to_render = []
            for context in self._editor.get_elements():
                flyweight = self._fly_factory.get_flyweight(context['type'])
                elements_to_render.append(flyweight.render(context))
            return elements_to_render

# --- Configuração e Rotas ---

ELEMENT_TYPES = {
    "tree":     {"name": "Árvore",   "data": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f332.png", "width": 40, "height": 40},
    "building": {"name": "Prédio", "data": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f3e2.png", "width": 50, "height": 50},
    "water":    {"name": "Água",     "data": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f30a.png", "width": 48, "height": 48},
    "road":     {"name": "Rua",      "data": "#6b7280", "width": 10, "height": 10 } # Cor cinza e espessura
}
mediator = PlacementMediator()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/state')
def get_state(): return jsonify(mediator.notify("get_state", None))

@app.route('/place', methods=['POST'])
def place_element():
    success, message = mediator.notify("place_element", request.json)
    return jsonify({"success": success, "message": message})

@app.route('/undo', methods=['POST'])
def undo():
    success, message = mediator.notify("undo", None)
    return jsonify({"success": success, "message": message})

if __name__ == '__main__':
    app.run(debug=True)
