// Modal de Excluir Comprador e Visualizar Compras
document.addEventListener('DOMContentLoaded', function() {
    const excluirCompradorModal = document.getElementById('excluirCompradorModal');
    if (excluirCompradorModal) {
        excluirCompradorModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const compradorId = button.getAttribute('data-comprador-id');
            const username = button.getAttribute('data-username');

            document.getElementById('delete-comprador-id').value = compradorId;
            document.getElementById('delete-comprador-username').textContent = username;
        });
    }

    // Modal de Visualizar Compras
    const visualizarComprasModal = document.getElementById('visualizarComprasModal');
    let comprasData = [];
    let estoquesData = [];
    
    if (visualizarComprasModal) {
        visualizarComprasModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const compradorId = button.getAttribute('data-comprador-id');
            const compradorNome = button.getAttribute('data-comprador-nome');

            console.log('Modal aberto para comprador ID:', compradorId, 'Nome:', compradorNome);
            
            document.getElementById('modal-comprador-nome').textContent = compradorNome;
            carregarComprasComprador(compradorId);
        });
    }

    // Função para carregar compras do comprador
    function carregarComprasComprador(compradorId) {
        console.log('Carregando compras para comprador ID:', compradorId);
        
        const loadingDiv = document.getElementById('loading-compras');
        const tabelaContainer = document.getElementById('tabela-compras-container');
        const noCompras = document.getElementById('no-compras');

        // Mostrar loading
        loadingDiv.style.display = 'block';
        tabelaContainer.style.display = 'none';
        noCompras.style.display = 'none';

        // Fazer requisição AJAX para buscar compras
        fetch(`/administrador/compradores/${compradorId}/compras/`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            }
        })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Dados recebidos:', data);
                if (data.success) {
                    comprasData = data.compras || [];
                    estoquesData = data.estoques || [];
                    
                    console.log('Compras encontradas:', comprasData.length);
                    
                    // Preencher filtro de estoques
                    preencherFiltroEstoques();
                    
                    // Mostrar compras
                    exibirCompras(comprasData);
                    
                    // Esconder loading
                    loadingDiv.style.display = 'none';
                    
                    if (comprasData.length > 0) {
                        tabelaContainer.style.display = 'block';
                    } else {
                        noCompras.style.display = 'block';
                    }
                } else {
                    console.error('Erro retornado pela API:', data.error);
                    loadingDiv.style.display = 'none';
                    noCompras.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Erro ao carregar compras:', error);
                loadingDiv.style.display = 'none';
                noCompras.style.display = 'block';
            });
    }

    // Função para preencher filtro de estoques
    function preencherFiltroEstoques() {
        const filtroEstoque = document.getElementById('filtro-estoque');
        filtroEstoque.innerHTML = '<option value="">Todos os estoques</option>';
        
        estoquesData.forEach(estoque => {
            const option = document.createElement('option');
            option.value = estoque.id;
            option.textContent = estoque.nome;
            filtroEstoque.appendChild(option);
        });
    }

    // Função para exibir compras na tabela
    function exibirCompras(compras) {
        const tbody = document.getElementById('tbody-compras');
        tbody.innerHTML = '';

        compras.forEach(compra => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>#${compra.id}</td>
                <td>${formatarData(compra.data)}</td>
                <td>${compra.fornecedor}</td>
                <td>${compra.estoque}</td>
                <td>R$ ${parseFloat(compra.valor_total).toFixed(2).replace('.', ',')}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="verDetalhesCompra(${compra.id})">
                        <i class="bi bi-eye"></i> Ver Detalhes
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    // Função para filtrar compras
    function filtrarCompras() {
        const filtroTexto = document.getElementById('filtro-compra').value.toLowerCase();
        const filtroEstoque = document.getElementById('filtro-estoque').value;

        const comprasFiltradas = comprasData.filter(compra => {
            const matchTexto = !filtroTexto || 
                compra.id.toString().includes(filtroTexto) ||
                compra.fornecedor.toLowerCase().includes(filtroTexto) ||
                compra.data.includes(filtroTexto);
            
            const matchEstoque = !filtroEstoque || compra.estoque_id.toString() === filtroEstoque;

            return matchTexto && matchEstoque;
        });

        exibirCompras(comprasFiltradas);
    }

    // Event listeners para filtros
    document.getElementById('filtro-compra').addEventListener('input', filtrarCompras);
    document.getElementById('filtro-estoque').addEventListener('change', filtrarCompras);
    
    // Limpar filtros
    document.getElementById('limpar-filtros').addEventListener('click', function() {
        document.getElementById('filtro-compra').value = '';
        document.getElementById('filtro-estoque').value = '';
        exibirCompras(comprasData);
    });

    // Função para formatar data
    function formatarData(dataString) {
        const data = new Date(dataString);
        return data.toLocaleDateString('pt-BR');
    }
});

// Função global para ver detalhes da compra
function verDetalhesCompra(compraId) {
    window.location.href = `/administrador/compras/${compraId}/`;
}
