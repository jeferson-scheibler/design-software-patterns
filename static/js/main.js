document.addEventListener('DOMContentLoaded', () => {

    // Helper para mostrar logs na tela
    function log(elementId, data) {
        const logEl = document.getElementById(elementId);
        logEl.textContent = JSON.stringify(data, null, 2); // Formata o JSON bonitinho
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

    // --- Lógica do Factory Method (CORRIGIDA) ---
    const factoryBtns = document.querySelectorAll('.factory-btn');
    factoryBtns.forEach(btn => {
        btn.addEventListener('click', () => { // Alteração: Removido o 'event' que não era necessário aqui
            const exportType = btn.dataset.type;
            const originalText = btn.innerHTML;

            // Feedback visual para o utilizador
            btn.innerHTML = 'Gerando...';
            btn.disabled = true;

            fetch(`/factory/${exportType}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro na rede ao gerar o ficheiro.');
                    }
                    const filename = `relatorio.${exportType}`;
                    return response.blob().then(blob => ({ blob, filename }));
                })
                .then(({ blob, filename }) => {
                    // Cria um link temporário para o ficheiro em memória
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = filename;
                    
                    document.body.appendChild(a);
                    a.click(); // Simula o clique no link para iniciar o download
                    
                    // Limpa o link e o URL temporário
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                })
                .catch(error => {
                    console.error('Erro no Factory:', error);
                    alert('Não foi possível gerar o ficheiro.');
                })
                .finally(() => {
                    // Restaura o botão ao seu estado original
                    // Alteração aqui: Usamos 'btn' que é a referência correta e estável
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                });
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