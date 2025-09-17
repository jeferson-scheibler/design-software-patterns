document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('canvas');
    const toolBtns = document.querySelectorAll('.tool-btn');
    const undoBtn = document.getElementById('undo-btn');
    const statusBar = document.getElementById('status-bar');

    let selectedElementType = null;

    // --- Funções de Comunicação com a API ---

    const api = {
        getState: async () => (await fetch('/state')).json(),
        placeElement: async (type, x, y) => {
            const response = await fetch('/place', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, x, y }),
            });
            return response.json();
        },
        undo: async () => (await fetch('/undo', { method: 'POST' })).json(),
    };

    // --- Funções da Interface ---

    function drawCanvas(elements) {
        canvas.innerHTML = ''; // Limpa o canvas
        elements.forEach(el => {
            const div = document.createElement('div');
            div.className = 'element';
            // Centraliza o elemento no ponto de clique
            div.style.left = `${el.x - el.width / 2}px`;
            div.style.top = `${el.y - el.height / 2}px`;
            div.style.width = `${el.width}px`;
            div.style.height = `${el.height}px`;
            div.innerHTML = `<img src="${el.image}" alt="${el.name}" title="${el.name} (${el.x}, ${el.y})">`;
            canvas.appendChild(div);
        });
    }

    function updateStatus(message, isError = false) {
        statusBar.textContent = message;
        statusBar.style.color = isError ? '#ef4444' : '#64748b';
        // Limpa a mensagem após 3 segundos
        setTimeout(() => {
            if (statusBar.textContent === message) statusBar.textContent = '';
        }, 3000);
    }

    function selectTool(type) {
        selectedElementType = type;
        toolBtns.forEach(btn => {
            btn.classList.toggle('selected', btn.dataset.type === type);
        });
        updateStatus(`Ferramenta selecionada: ${type}`);
    }

    // --- Lógica de Eventos ---

    async function handleCanvasClick(e) {
        if (!selectedElementType) {
            updateStatus('Por favor, selecione uma ferramenta na barra lateral!', true);
            return;
        }
        const rect = canvas.getBoundingClientRect();
        const x = Math.round(e.clientX - rect.left);
        const y = Math.round(e.clientY - rect.top);
        
        const result = await api.placeElement(selectedElementType, x, y);
        updateStatus(result.message, !result.success);

        if (result.success) {
            const elements = await api.getState();
            drawCanvas(elements);
        }
    }

    async function handleUndoClick() {
        const result = await api.undo();
        updateStatus(result.message);
        const elements = await api.getState();
        drawCanvas(elements);
    }

    // --- Inicialização ---

    toolBtns.forEach(btn => btn.addEventListener('click', () => selectTool(btn.dataset.type)));
    canvas.addEventListener('click', handleCanvasClick);
    undoBtn.addEventListener('click', handleUndoClick);

    async function init() {
        const elements = await api.getState();
        drawCanvas(elements);
        updateStatus("Bem-vindo ao Planeador Urbano! Selecione uma ferramenta e clique no mapa.");
    }

    init();
});

