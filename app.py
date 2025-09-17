from flask import Flask, jsonify, render_template, request
from abc import ABC, abstractmethod
import copy
import time

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- PATTERN 1: Flyweight ---
# Otimiza o uso de memória partilhando dados comuns (intrínsecos) dos elementos.

class ElementFlyweight:
    """O objeto partilhado que contém o estado intrínseco (nome, imagem, tamanho)."""
    def __init__(self, name, image, width, height):
        self._name = name
        self._image = image
        self._width = width
        self._height = height

    def render(self, x, y):
        """Retorna todos os dados necessários para a renderização no frontend."""
        return {
            "name": self._name, "image": self._image, "x": x, "y": y,
            "width": self._width, "height": self._height
        }

class FlyweightFactory:
    """Gere os Flyweights, garantindo que cada tipo de elemento só existe uma vez em memória."""
    _flyweights = {}

    def get_flyweight(self, key):
        if key not in self._flyweights:
            print(f"--- FlyweightFactory: A criar novo flyweight para '{key}' ---")
            element_data = ELEMENT_TYPES[key]
            self._flyweights[key] = ElementFlyweight(
                element_data['name'], element_data['image'],
                element_data['width'], element_data['height']
            )
        return self._flyweights[key]

# --- PATTERN 2: Memento ---
# Permite salvar e restaurar o estado do mapa para a funcionalidade "Desfazer".

class MapState:
    """O Memento: armazena uma cópia 'congelada' do estado do mapa."""
    def __init__(self, elements):
        self._elements = copy.deepcopy(elements)

    def get_elements(self):
        return self._elements

class MapEditor:
    """O Originator: o objeto cujo estado salvamos."""
    _elements = []

    def add_element(self, element_type, x, y):
        context = {"type": element_type, "x": x, "y": y}
        self._elements.append(context)
        print(f"--- Editor: Elemento '{element_type}' adicionado em ({x},{y}) ---")

    def get_elements(self): return self._elements
    def set_elements(self, elements): self._elements = elements
    def save(self) -> MapState: return MapState(self._elements)
    def restore(self, memento: MapState): self._elements = memento.get_elements()

class History:
    """O Caretaker: guarda os Mementos, permitindo o Desfazer."""
    _mementos = []
    def __init__(self, editor: MapEditor): self._editor = editor
    def save(self): self._mementos.append(self._editor.save())
    def undo(self):
        if not self._mementos: return
        self._editor.restore(self._mementos.pop())

# --- PATTERN 3: Chain of Responsibility ---
# Cria uma cadeia de validações para cada nova adição de elemento.

class Handler(ABC):
    """A interface para todos os validadores da cadeia."""
    _next_handler = None
    def set_next(self, handler): self._next_handler = handler; return handler
    @abstractmethod
    def handle(self, request):
        if self._next_handler: return self._next_handler.handle(request)
        return True, "Fim da cadeia."

class BoundaryValidator(Handler):
    """Primeiro elo: verifica se a posição está dentro dos limites do mapa."""
    def handle(self, request):
        x, y = request['x'], request['y']
        if not (0 <= x <= 500 and 0 <= y <= 300):
            return False, "Erro: Posição fora dos limites do mapa!"
        print("--- Cadeia: Validação de limites OK. ---")
        return super().handle(request)

class CollisionValidator(Handler):
    """Segundo elo: usa uma lógica de retângulos para verificar colisões."""
    def __init__(self, editor: MapEditor, factory: FlyweightFactory):
        self._editor = editor
        self._factory = factory

    def handle(self, request):
        new_element_type = request['type']
        new_flyweight = self._factory.get_flyweight(new_element_type)
        x1_new, y1_new = request['x'], request['y']
        x2_new, y2_new = x1_new + new_flyweight._width, y1_new + new_flyweight._height

        for element in self._editor.get_elements():
            existing_flyweight = self._factory.get_flyweight(element['type'])
            x1_old, y1_old = element['x'], element['y']
            x2_old, y2_old = x1_old + existing_flyweight._width, y1_old + existing_flyweight._height

            # Verifica se os retângulos se sobrepõem
            if not (x2_new < x1_old or x1_new > x2_old or y2_new < y1_old or y1_new > y2_old):
                return False, "Erro: Colisão detetada com outro elemento!"
        
        print("--- Cadeia: Validação de colisão OK. ---")
        return super().handle(request)

# --- PATTERN 4: Mediator ---
# Centraliza a comunicação e orquestra as ações entre todos os componentes.

class PlacementMediator:
    def __init__(self):
        self._flyweight_factory = FlyweightFactory()
        self._editor = MapEditor()
        self._history = History(self._editor)
        self._chain_root = BoundaryValidator()
        self._chain_root.set_next(CollisionValidator(self._editor, self._flyweight_factory))

    def notify(self, event, data):
        if event == "place_element":
            self._history.save()
            is_valid, message = self._chain_root.handle(data)
            if is_valid:
                self._editor.add_element(data['type'], data['x'], data['y'])
                return True, "Elemento adicionado com sucesso."
            else:
                self._history.undo()
                return False, message
        elif event == "undo":
            self._history.undo()
            return True, "Ação desfeita."
        elif event == "get_state":
            elements_to_render = []
            for element_context in self._editor.get_elements():
                flyweight = self._flyweight_factory.get_flyweight(element_context['type'])
                elements_to_render.append(flyweight.render(element_context['x'], element_context['y']))
            return elements_to_render

# --- Configuração e Rotas da API ---

ELEMENT_TYPES = {
    "tree":     {"name": "Árvore",   "image": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f332.png", "width": 40, "height": 40},
    "building": {"name": "Prédio", "image": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f3e2.png", "width": 50, "height": 50},
    "road":     {"name": "Rua",      "image": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f6e4-fe0f.png", "width": 48, "height": 48},
    "water":    {"name": "Água",     "image": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f30a.png", "width": 48, "height": 48}
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