from flask import Flask, jsonify, render_template, request
from abc import ABC, abstractmethod
import copy
import math

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- PATTERN 1: Flyweight ---
# Otimiza o uso de memória partilhando dados comuns dos elementos.

class ElementFlyweight:
    def __init__(self, name, data, width, height, type_class):
        self._name, self._data = name, data
        self._width, self._height = width, height
        self._type_class = type_class # 'point' ou 'path'

    def render(self, context):
        base = {"name": self._name, "data": self._data, "type": context['type']}
        if self._type_class == 'path':
            base.update({"path": context['path']})
        else:
            base.update({"x": context['x'], "y": context['y'], "width": self._width, "height": self._height})
        return base

class FlyweightFactory:
    _flyweights = {}
    def get_flyweight(self, key):
        if key not in self._flyweights:
            d = ELEMENT_TYPES[key]
            self._flyweights[key] = ElementFlyweight(d['name'], d['data'], d.get('width'), d.get('height'), d['class'])
        return self._flyweights[key]

# --- PATTERN 2: Memento ---
# Salva/restaura o estado do mapa, agora de forma mais granular.

class MapState:
    def __init__(self, elements, temp_path):
        self._elements = copy.deepcopy(elements)
        self._temp_path = copy.deepcopy(temp_path)
    def get_state(self): return self._elements, self._temp_path

class MapEditor:
    _elements, _temp_path = [], []
    def add_element(self, context): self._elements.append(context)
    def add_temp_point(self, point): self._temp_path.append(point)
    def clear_temp_path(self): self._temp_path = []
    def get_full_state(self): return self._elements, self._temp_path
    def set_full_state(self, state): self._elements, self._temp_path = state
    def save(self): return MapState(self._elements, self._temp_path)
    def restore(self, memento: MapState): self.set_full_state(memento.get_state())

class History:
    _mementos = []
    def __init__(self, editor: MapEditor): self._editor = editor
    def save(self): self._mementos.append(self._editor.save())
    def undo(self):
        if self._mementos: self._editor.restore(self._mementos.pop())

# --- PATTERN 3: Chain of Responsibility ---
# Validação de colisão e limites muito mais robusta.

class Handler(ABC):
    _next_handler = None
    def set_next(self, h): self._next_handler = h; return h
    def handle(self, req):
        if self._next_handler: return self._next_handler.handle(req)
        return True, "Fim da cadeia."

class BoundaryValidator(Handler):
    def handle(self, request):
        points = request.get('path', [{'x': request.get('x'), 'y': request.get('y')}])
        for p in points:
            if not p or not (0 <= p['x'] <= 500 and 0 <= p['y'] <= 300):
                return False, "Erro: Fora dos limites do mapa!"
        return super().handle(request)

class CollisionValidator(Handler):
    def __init__(self, editor: MapEditor, factory: FlyweightFactory):
        self._editor, self._factory = editor, factory

    def _point_in_rect(self, p, r_x, r_y, r_w, r_h):
        return r_x <= p['x'] <= r_x + r_w and r_y <= p['y'] <= r_y + r_h

    def _point_segment_dist(self, p, p1, p2):
        # Simplified distance check for collision
        dx, dy = p2['x'] - p1['x'], p2['y'] - p1['y']
        if dx == dy == 0: return math.hypot(p['x'] - p1['x'], p['y'] - p1['y'])
        t = ((p['x'] - p1['x']) * dx + (p['y'] - p1['y']) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        return math.hypot(p['x'] - (p1['x'] + t * dx), p['y'] - (p1['y'] + t * dy))

    def handle(self, request):
        all_elements, _ = self._editor.get_full_state()
        req_type = request.get('type')
        flyweight = self._factory.get_flyweight(req_type)
        
        # Se for um ponto (árvore/prédio)
        if flyweight._type_class == 'point':
            x, y = request['x'], request['y']
            for el in all_elements:
                el_fly = self._factory.get_flyweight(el['type'])
                if el_fly._type_class == 'path':
                    for i in range(len(el['path']) - 1):
                        if self._point_segment_dist({'x':x, 'y':y}, el['path'][i], el['path'][i+1]) < (flyweight._width / 2):
                            return False, f"Erro: Não pode colocar {flyweight._name} sobre uma rua/rio."
        # Se for um segmento de caminho (rua/rio)
        elif request.get('is_segment'):
            p1 = request['path'][0]
            for el in all_elements:
                el_fly = self._factory.get_flyweight(el['type'])
                if el_fly._type_class == 'point':
                    if self._point_in_rect(p1, el['x'] - el_fly._width/2, el['y']-el_fly._height/2, el_fly._width, el_fly._height):
                        return False, f"Erro: Rua/rio não pode passar por cima de {el_fly._name}."
        
        return super().handle(request)

# --- PATTERN 4: Mediator ---
# Orquestra a lógica granular de desenho e validação.

class PlacementMediator:
    def __init__(self):
        self._factory = FlyweightFactory()
        self._editor = MapEditor()
        self._history = History(self._editor)
        self._chain = BoundaryValidator().set_next(CollisionValidator(self._editor, self._factory))

    def notify(self, event, data):
        if event == "add_path_segment":
            self._history.save()
            new_point = data['point']
            # O request para validação é só sobre o novo ponto
            validation_req = {'type': data['type'], 'path': [new_point], 'is_segment': True}
            is_valid, msg = self._chain.handle(validation_req)
            if is_valid: self._editor.add_temp_point(new_point); return True, "Ponto adicionado."
            self._history.undo(); return False, msg

        elif event == "finish_path":
            _, temp_path = self._editor.get_full_state()
            if not temp_path or len(temp_path) < 2: self._editor.clear_temp_path(); return True, "Desenho cancelado."
            self._editor.add_element({'type': data['type'], 'path': temp_path})
            self._editor.clear_temp_path()
            return True, "Caminho finalizado."

        elif event == "place_point_element":
            self._history.save()
            is_valid, msg = self._chain.handle(data)
            if is_valid: self._editor.add_element(data); return True, "Elemento adicionado."
            self._history.undo(); return False, msg

        elif event == "undo": self._history.undo(); return True, "Ação desfeita."
        
        elif event == "get_state":
            elements, temp_path = self._editor.get_full_state()
            elements_to_render = []
            for ctx in elements:
                elements_to_render.append(self._factory.get_flyweight(ctx['type']).render(ctx))
            return {"elements": elements_to_render, "temp_path": temp_path}

# --- Configuração e Rotas ---
ELEMENT_TYPES = {
    "tree":     {"name": "Árvore", "data": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f332.png", "width": 40, "height": 40, "class": "point"},
    "building": {"name": "Prédio", "data": "https://cdn.jsdelivr.net/npm/emoji-datasource-apple/img/apple/64/1f3e2.png", "width": 50, "height": 50, "class": "point"},
    "road":     {"name": "Rua",    "data": "#6b7280", "class": "path"},
    "water":    {"name": "Água",   "data": "#3b82f6", "class": "path"}
}
mediator = PlacementMediator()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/state')
def get_state(): return jsonify(mediator.notify("get_state", None))

@app.route('/action', methods=['POST'])
def perform_action():
    data = request.json
    event = data.pop('event')
    success, message = mediator.notify(event, data)
    return jsonify({"success": success, "message": message})

if __name__ == '__main__': app.run(debug=True)