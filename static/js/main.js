document.addEventListener('DOMContentLoaded', () => {
    const canvasContainer = document.getElementById('canvas-container');
    const elementLayer = document.getElementById('element-layer');
    const drawingLayer = document.getElementById('drawing-layer');
    const toolBtns = document.querySelectorAll('.tool-btn');
    const undoBtn = document.getElementById('undo-btn');
    const statusBar = document.getElementById('status-bar');

    let state = { selectedTool: null, snapPoint: null, allVertices: [] };
    const SNAP_RADIUS = 10;

    const api = {
        getState: async () => (await fetch('/state')).json(),
        performAction: async (event, data = {}) => {
            const response = await fetch('/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ event, ...data }),
            });
            return response.json();
        }
    };

    function drawCanvas(data) {
        elementLayer.innerHTML = '';
        drawingLayer.innerHTML = '';
        state.allVertices = [];

        // Desenha elementos permanentes
        data.elements.forEach(el => {
            if (el.type === 'road' || el.type === 'water') {
                drawPath(drawingLayer, el.path, el.data, 10);
                el.path.forEach(p => { state.allVertices.push(p); drawVertex(drawingLayer, p, '#4b5563'); });
            } else {
                drawPointElement(elementLayer, el);
            }
        });

        // Desenha caminho temporário
        if (data.temp_path && data.temp_path.length > 0) {
            drawPath(drawingLayer, data.temp_path, '#0ea5e9', 5, '5,5');
            data.temp_path.forEach(p => drawVertex(drawingLayer, p, '#0ea5e9'));
        }
    }

    // --- Funções Auxiliares de Desenho SVG ---
    const createSvgElement = (tag, attrs) => {
        const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
        for (const key in attrs) el.setAttribute(key, attrs[key]);
        return el;
    };
    const drawPath = (layer, path, color, width, dash = '') => {
        if (path.length < 2) return;
        const points = path.map(p => `${p.x},${p.y}`).join(' ');
        layer.appendChild(createSvgElement('polyline', { points, stroke: color, 'stroke-width': width, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', fill: 'none', 'stroke-dasharray': dash }));
    };
    const drawVertex = (layer, p, color) => {
        layer.appendChild(createSvgElement('circle', { cx: p.x, cy: p.y, r: 4, fill: color }));
    };
    const drawPointElement = (layer, el) => {
        const div = document.createElement('div');
        div.className = 'element';
        div.style.left = `${el.x - el.width / 2}px`;
        div.style.top = `${el.y - el.height / 2}px`;
        div.style.width = `${el.width}px`;
        div.style.height = `${el.height}px`;
        div.innerHTML = `<img src="${el.data}" title="${el.name}">`;
        layer.appendChild(div);
    };

    function updateStatus(message, isError = false) {
        statusBar.textContent = message;
        statusBar.style.color = isError ? '#ef4444' : '#64748b';
    }

    function selectTool(type) {
        if (state.selectedTool && ELEMENT_TYPES[state.selectedTool].class === 'path') {
            api.performAction('finish_path', { type: state.selectedTool });
        }
        state.selectedTool = type;
        toolBtns.forEach(btn => btn.classList.toggle('selected', btn.dataset.type === type));
        const toolClass = ELEMENT_TYPES[type].class;
        updateStatus(toolClass === 'path' ? 'Clique para adicionar pontos, duplo clique para finalizar.' : 'Clique no mapa para colocar.');
        fetchAllStateAndDraw();
    }

    async function handleCanvasClick(e) {
        if (!state.selectedTool) return;
        
        const rect = canvasContainer.getBoundingClientRect();
        let x = Math.round(e.clientX - rect.left);
        let y = Math.round(e.clientY - rect.top);

        if (state.snapPoint) { x = state.snapPoint.x; y = state.snapPoint.y; }

        const toolClass = ELEMENT_TYPES[state.selectedTool].class;
        const event = toolClass === 'path' ? 'add_path_segment' : 'place_point_element';
        const data = toolClass === 'path' ? { type: state.selectedTool, point: { x, y } } : { type: state.selectedTool, x, y };

        const result = await api.performAction(event, data);
        updateStatus(result.message, !result.success);
        fetchAllStateAndDraw();
    }
    
    function handleMouseMove(e) {
        const rect = canvasContainer.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        let foundSnap = false;
        for (const vertex of state.allVertices) {
            const dist = Math.hypot(vertex.x - mouseX, vertex.y - mouseY);
            if (dist < SNAP_RADIUS) {
                state.snapPoint = vertex;
                foundSnap = true;
                break;
            }
        }
        if (!foundSnap) state.snapPoint = null;
        updateSnapIndicator();
    }

    function updateSnapIndicator() {
        let indicator = document.getElementById('snap-indicator');
        if (!indicator) {
            indicator = createSvgElement('circle', { id: 'snap-indicator', r: SNAP_RADIUS, fill: 'rgba(59, 130, 246, 0.5)', 'pointer-events': 'none' });
            drawingLayer.appendChild(indicator);
        }
        if (state.snapPoint) {
            indicator.setAttribute('cx', state.snapPoint.x);
            indicator.setAttribute('cy', state.snapPoint.y);
            indicator.style.display = 'block';
        } else {
            indicator.style.display = 'none';
        }
    }

    async function finishDrawing() {
        if (state.selectedTool && ELEMENT_TYPES[state.selectedTool].class === 'path') {
            await api.performAction('finish_path', { type: state.selectedTool });
            fetchAllStateAndDraw();
        }
    }

    async function fetchAllStateAndDraw() {
        const data = await api.getState();
        drawCanvas(data);
    }
    
    // --- Inicialização ---
    const ELEMENT_TYPES = {
        "tree": { class: 'point' }, "building": { class: 'point' },
        "road": { class: 'path' }, "water": { class: 'path' }
    };
    toolBtns.forEach(btn => btn.addEventListener('click', () => selectTool(btn.dataset.type)));
    canvasContainer.addEventListener('click', handleCanvasClick);
    canvasContainer.addEventListener('mousemove', handleMouseMove);
    canvasContainer.addEventListener('dblclick', finishDrawing);
    undoBtn.addEventListener('click', async () => {
        await api.performAction('undo');
        fetchAllStateAndDraw();
    });

    fetchAllStateAndDraw();
});

