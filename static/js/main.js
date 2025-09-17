document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('canvas');
    const toolBtns = document.querySelectorAll('.tool-btn');
    const undoBtn = document.getElementById('undo-btn');
    const statusBar = document.getElementById('status-bar');

    let selectedElementType = null;

    // --- Funções de Comunicação com a API ---

    async function fetchStateAndDraw() {
        const response = await fetch('/state');
        const elements = await response.json();
        drawCanvas(elements);
    }

    async function placeElement(type, x, y) {
        const response = await fetch('/place', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, x, y }),
        });
        const result = await response.json();
        updateStatus(result.message, !result.success);
        if (result.success) {
            fetchStateAndDraw();
        }
    }

    async function undoLastAction() {
        const response = await fetch('/undo', { method: 'POST' });
        const result = await response.json();
        updateStatus(result.message);
        fetchStateAndDraw();
    }

    // --- Funções da Interface ---

    function drawCanvas(elements) {
        canvas.innerHTML = ''; // Limpa o canvas
        elements.forEach(el => {
            const div = document.createElement('div');
            div.className = 'element';
            div.style.left = `${el.x - 24}px`; // Centraliza a imagem
            div.style.top = `${el.y - 24}px`;
            div.innerHTML = `<img src="${el.image}" alt="${el.name}" title="${el.name}">`;
            canvas.appendChild(div);
        });
    }

    function updateStatus(message, isError = false) {
        statusBar.textContent = message;
        statusBar.style.color = isError ? '#ef4444' : '#64748b';
        setTimeout(() => statusBar.textContent = '', 3000);
    }

    function selectTool(type) {
        selectedElementType = type;
        toolBtns.forEach(btn => {
            btn.classList.toggle('bg-sky-200', btn.dataset.type === type);
            btn.classList.toggle('border-sky-500', btn.dataset.type === type);
        });
        updateStatus(`Ferramenta selecionada: ${type}`);
    }

    // --- Event Listeners ---

    toolBtns.forEach(btn => {
        btn.addEventListener('click', () => selectTool(btn.dataset.type));
    });

    canvas.addEventListener('click', (e) => {
        if (!selectedElementType) {
            updateStatus('Selecione uma ferramenta primeiro!', true);
            return;
        }
        const rect = canvas.getBoundingClientRect();
        const x = Math.round(e.clientX - rect.left);
        const y = Math.round(e.clientY - rect.top);
        placeElement(selectedElementType, x, y);
    });

    undoBtn.addEventListener('click', undoLastAction);

    // --- Inicialização ---
    fetchStateAndDraw();
    updateStatus("Bem-vindo ao Planeador Urbano!");
});

