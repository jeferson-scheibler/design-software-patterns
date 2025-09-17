document.addEventListener('DOMContentLoaded', () => {
    // --- Referências aos Elementos do DOM ---
    const canvasContainer = document.getElementById('canvas-container');
    const elementLayer = document.getElementById('element-layer');
    const drawingLayer = document.getElementById('drawing-layer');
    const toolBtns = document.querySelectorAll('.tool-btn');
    const undoBtn = document.getElementById('undo-btn');
    const statusBar = document.getElementById('status-bar');

    // --- Estado da Aplicação Frontend ---
    let selectedElementType = null;
    let isDrawingRoad = false;
    let currentRoadPath = [];

    // --- Funções de Comunicação com a API (Backend) ---
    const api = {
        getState: async () => (await fetch('/state')).json(),
        placeElement: async (data) => {
            const response = await fetch('/place', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            return response.json();
        },
        undo: async () => (await fetch('/undo', { method: 'POST' })).json(),
    };

    // --- Funções de Renderização (Desenho na Tela) ---
    function drawCanvas(elements) {
        elementLayer.innerHTML = '';
        drawingLayer.innerHTML = '';

        elements.forEach(el => {
            // Lógica para desenhar RUAS (linhas no SVG)
            if (el.type === 'road') {
                const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
                const points = el.path.map(p => `${p.x},${p.y}`).join(' ');
                polyline.setAttribute('points', points);
                polyline.setAttribute('stroke', el.data); // Cor da rua
                polyline.setAttribute('stroke-width', '10');
                polyline.setAttribute('stroke-linecap', 'round');
                polyline.setAttribute('stroke-linejoin', 'round');
                polyline.setAttribute('fill', 'none');
                drawingLayer.appendChild(polyline);
            } 
            // Lógica para desenhar ELEMENTOS (imagens em divs)
            else {
                const div = document.createElement('div');
                div.className = 'element';
                div.style.left = `${el.x - el.width / 2}px`;
                div.style.top = `${el.y - el.height / 2}px`;
                div.style.width = `${el.width}px`;
                div.style.height = `${el.height}px`;
                div.innerHTML = `<img src="${el.data}" alt="${el.name}" title="${el.name}">`;
                elementLayer.appendChild(div);
            }
        });
    }

    function drawTemporaryRoad() {
        // Desenha a linha enquanto o utilizador clica nos pontos
        drawingLayer.innerHTML = ''; // Limpa linhas temporárias antigas
        if (currentRoadPath.length > 1) {
            const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
            const points = currentRoadPath.map(p => `${p.x},${p.y}`).join(' ');
            polyline.setAttribute('points', points);
            polyline.setAttribute('stroke', '#0ea5e9'); // Cor azul temporária
            polyline.setAttribute('stroke-width', '5');
            polyline.setAttribute('stroke-dasharray', '5,5'); // Linha tracejada
            polyline.setAttribute('fill', 'none');
            drawingLayer.appendChild(polyline);
        }
    }

    // --- Funções de Controlo e Lógica de Eventos ---
    function updateStatus(message, isError = false) {
        statusBar.textContent = message;
        statusBar.style.color = isError ? '#ef4444' : '#64748b';
    }

    async function finishDrawing() {
        if (!isDrawingRoad || currentRoadPath.length < 2) {
            resetDrawingState();
            return;
        }
        const result = await api.placeElement({ type: 'road', path: currentRoadPath });
        updateStatus(result.message, !result.success);
        resetDrawingState();
        fetchAllStateAndDraw();
    }

    function resetDrawingState() {
        isDrawingRoad = false;
        currentRoadPath = [];
        drawingLayer.innerHTML = '';
    }

    function selectTool(type) {
        finishDrawing(); // Finaliza qualquer desenho pendente ao trocar de ferramenta
        selectedElementType = type;
        isDrawingRoad = (type === 'road');
        
        toolBtns.forEach(btn => btn.classList.toggle('selected', btn.dataset.type === type));
        
        if (isDrawingRoad) {
            updateStatus('Modo de desenho de rua: clique para adicionar pontos, duplo clique para finalizar.');
        } else {
            updateStatus(`Ferramenta selecionada: ${type}. Clique no mapa para colocar.`);
        }
    }

    async function handleCanvasClick(e) {
        if (!selectedElementType) return;

        const rect = canvasContainer.getBoundingClientRect();
        const x = Math.round(e.clientX - rect.left);
        const y = Math.round(e.clientY - rect.top);

        if (isDrawingRoad) {
            currentRoadPath.push({ x, y });
            drawTemporaryRoad();
        } else {
            const result = await api.placeElement({ type: selectedElementType, x, y });
            updateStatus(result.message, !result.success);
            fetchAllStateAndDraw();
        }
    }

    async function handleUndoClick() {
        resetDrawingState();
        const result = await api.undo();
        updateStatus(result.message);
        fetchAllStateAndDraw();
    }

    async function fetchAllStateAndDraw() {
        const elements = await api.getState();
        drawCanvas(elements);
    }
    
    // --- Inicialização ---
    toolBtns.forEach(btn => btn.addEventListener('click', () => selectTool(btn.dataset.type)));
    canvasContainer.addEventListener('click', handleCanvasClick);
    canvasContainer.addEventListener('dblclick', finishDrawing);
    undoBtn.addEventListener('click', handleUndoClick);

    fetchAllStateAndDraw();
});

