document.addEventListener('DOMContentLoaded', () => {

    // Helper para mostrar logs na tela
    function log(elementId, data) {
        const logEl = document.getElementById(elementId);
        logEl.textContent = JSON.stringify(data, null, 2); // Formata o JSON bonitinho
    }
    
    // --- Lógica do Builder ---
    const builderBtns = document.querySelectorAll('.builder-btn');
    builderBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const computerType = btn.dataset.type;
            log('builder-log', { status: `A montar PC ${computerType}...` });
            fetch(`/builder/${computerType}`)
                .then(response => response.json())
                .then(data => {
                    log('builder-log', data);
                })
                .catch(error => console.error('Erro no Builder:', error));
        });
    });

    // --- Lógica do Prototype ---
    const prototypeBtns = document.querySelectorAll('.prototype-btn');
    prototypeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const characterType = btn.dataset.type;
            log('prototype-log', { status: `A clonar ${characterType}...` });
            fetch(`/prototype/${characterType}`)
                .then(response => response.json())
                .then(data => {
                    log('prototype-log', data);
                })
                .catch(error => console.error('Erro no Prototype:', error));
        });
    });

    // --- Lógica do Observer ---
    const observerBtn = document.getElementById('observer-btn');
    const observerInput = document.getElementById('observer-input');
    const channelA_span = document.querySelector('#observer-1 span');
    const channelB_span = document.querySelector('#observer-2 span');

    // Função para atualizar a UI dos observers
    function updateObserverStatus() {
        fetch('/observer/status')
            .then(response => response.json())
            .then(data => {
                channelA_span.textContent = data.channel_A;
                channelB_span.textContent = data.channel_B;
            });
    }

    observerBtn.addEventListener('click', () => {
        const newsTitle = observerInput.value.trim();
        if (!newsTitle) {
            alert('Por favor, digite um título para a notícia.');
            return;
        }

        fetch('/observer/publish', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newsTitle }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            updateObserverStatus();
            observerInput.value = '';
        })
        .catch(error => console.error('Erro no Observer:', error));
    });

    // Inicia o status dos observers quando a página carrega
    updateObserverStatus();
});