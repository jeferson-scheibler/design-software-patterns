from flask import Flask, jsonify, render_template, request
from abc import ABC, abstractmethod
import copy
import time

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- PATTERN 1: Flyweight ---
# Objetivo: Partilhar objetos para reduzir o uso de memória.

class ElementFlyweight:
    """O objeto partilhado que contém o estado intrínseco (comum)."""
    def __init__(self, name, image):
        self._name = name
        self._image = image

    def render(self, x, y):
        # No mundo real, isto renderizaria a imagem. Aqui, retornamos os dados.
        return {"name": self._name, "image": self._image, "x": x, "y": y}

class FlyweightFactory:
    """Cria e gere os Flyweights, garantindo que são partilhados."""
    _flyweights = {}

    def get_flyweight(self, key, name, image):
        if key not in self._flyweights:
            print(f"--- FlyweightFactory: A criar novo flyweight para '{key}' ---")
            self._flyweights[key] = ElementFlyweight(name, image)
        return self._flyweights[key]

# --- PATTERN 2: Memento ---
# Objetivo: Salvar e restaurar o estado de um objeto.

class MapState:
    """O Memento: armazena uma cópia do estado do mapa."""
    def __init__(self, elements):
        self._elements = copy.deepcopy(elements)

    def get_elements(self):
        return self._elements

class MapEditor:
    """O Originator: o objeto cujo estado queremos salvar."""
    _elements = [] # O estado atual do mapa

    def add_element(self, element_type, x, y, factory: FlyweightFactory):
        # O estado extrínseco (único)
        context = {"type": element_type, "x": x, "y": y}
        self._elements.append(context)
        print(f"--- Editor: Elemento '{element_type}' adicionado em ({x},{y}) ---")

    def get_elements(self):
        return self._elements
    
    def set_elements(self, elements):
        self._elements = elements

    def save(self) -> MapState:
        print("--- Editor: A salvar estado (Memento criado) ---")
        return MapState(self._elements)

    def restore(self, memento: MapState):
        print("--- Editor: A restaurar para o estado anterior (Memento usado) ---")
        self._elements = memento.get_elements()

class History:
    """O Caretaker: guarda os Mementos, mas não sabe o seu conteúdo."""
    _mementos = []
    def __init__(self, editor: MapEditor):
        self._editor = editor
    
    def save(self):
        self._mementos.append(self._editor.save())

    def undo(self):
        if not self._mementos:
            print("--- History: Sem estados para desfazer. ---")
            return
        
        memento = self._mementos.pop()
        try:
            self._editor.restore(memento)
        except Exception:
            self.undo() # Tenta o anterior se o último falhar

# --- PATTERN 3: Chain of Responsibility ---
# Objetivo: Passar uma solicitação por uma cadeia de manipuladores.

class Handler(ABC):
    """A interface do Handler para a cadeia."""
    _next_handler = None
    def set_next(self, handler):
        self._next_handler = handler
        return handler
    
    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return True, "Fim da cadeia."

class BoundaryValidator(Handler):
    """Primeiro elo: verifica se o elemento está dentro dos limites."""
    def handle(self, request):
        x, y = request['x'], request['y']
        if not (0 <= x <= 500 and 0 <= y <= 300):
            return False, "Erro: Fora dos limites do mapa!"
        print("--- Cadeia: Validação de limites OK. ---")
        return super().handle(request)

class CollisionValidator(Handler):
    """Segundo elo: verifica se não há colisão."""
    def __init__(self, editor: MapEditor):
        self._editor = editor

    def handle(self, request):
        x, y = request['x'], request['y']
        for element in self._editor.get_elements():
            # Simplificação: considera colisão se estiver a menos de 20px
            if abs(element['x'] - x) < 20 and abs(element['y'] - y) < 20:
                return False, "Erro: Colisão detetada com outro elemento!"
        print("--- Cadeia: Validação de colisão OK. ---")
        return super().handle(request)

# --- PATTERN 4: Mediator ---
# Objetivo: Centralizar a comunicação entre objetos.

class PlacementMediator:
    """O Mediator que coordena todas as ações."""
    def __init__(self):
        self._flyweight_factory = FlyweightFactory()
        self._editor = MapEditor()
        self._history = History(self._editor)
        
        # Monta a cadeia de responsabilidade
        self._chain_root = BoundaryValidator()
        self._chain_root.set_next(CollisionValidator(self._editor))

    def notify(self, event, data):
        if event == "place_element":
            # 1. Salva o estado atual ANTES de qualquer alteração
            self._history.save()
            
            # 2. Envia a solicitação para a cadeia de validação
            is_valid, message = self._chain_root.handle(data)
            
            if is_valid:
                # 3. Se for válido, o Editor adiciona o elemento
                self._editor.add_element(data['type'], data['x'], data['y'], self._flyweight_factory)
                return True, "Elemento adicionado com sucesso."
            else:
                # 4. Se for inválido, desfaz o save
                self._history.undo()
                return False, message

        elif event == "undo":
            self._history.undo()
            return True, "Ação desfeita."
        
        elif event == "get_state":
            elements_to_render = []
            for element_context in self._editor.get_elements():
                flyweight = self._flyweight_factory.get_flyweight(
                    element_context['type'],
                    ELEMENT_TYPES[element_context['type']]['name'],
                    ELEMENT_TYPES[element_context['type']]['image']
                )
                elements_to_render.append(flyweight.render(element_context['x'], element_context['y']))
            return elements_to_render

# --- Configuração e Rotas da API ---

ELEMENT_TYPES = {
    "tree": {"name": "Árvore Comum", "image": "https://img.icons8.com/color/48/000000/tree.png"},
    "building": {"name": "Prédio Residencial", "image": "https://img.icons8.com/color/48/000000/building.png"}
}
# Instância única do nosso sistema (Mediator)
mediator = PlacementMediator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/state')
def get_state():
    return jsonify(mediator.notify("get_state", None))

@app.route('/place', methods=['POST'])
def place_element():
    data = request.json
    success, message = mediator.notify("place_element", data)
    return jsonify({"success": success, "message": message})

@app.route('/undo', methods=['POST'])
def undo():
    success, message = mediator.notify("undo", None)
    return jsonify({"success": success, "message": message})

if __name__ == '__main__':
    app.run(debug=True)