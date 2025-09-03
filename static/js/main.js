document.addEventListener('DOMContentLoaded', () => {

    // Helper para mostrar logs na tela
    function log(elementId, data) {
        const logEl = document.getElementById(elementId);
        logEl.textContent = JSON.stringify(data, null, 2);
    }
    
    // --- Lógica do Singleton ---
    const singletonBtn = document.getElementById('singleton-btn');
    singletonBtn.addEventListener('click', () => {
        fetch('/singleton')
            .then(response => response.json())
            .then(data => {
                log('singleton-log', data);
            })
            .catch(error => console.error('Erro no Singleton:', error));
    });

    // --- Lógica do Factory Method ---
    const factoryBtns = document.querySelectorAll('.factory-btn');
    factoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const exportType = btn.dataset.type;
            fetch(`/factory/${exportType}`)
                .then(response => response.json())
                .then(data => {
                    log('factory-log', data);
                })
                .catch(error => console.error('Erro no Factory:', error));
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

        // 1. Envia a nova notícia para o backend publicar
        fetch('/observer/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title: newsTitle }),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message); // Loga a confirmação no console
            // 2. Após publicar, busca o novo status dos observers
            updateObserverStatus();
            observerInput.value = '';
        })
        .catch(error => console.error('Erro no Observer:', error));
    });

    // Inicia o status dos observers quando a página carrega
    updateObserverStatus();
});