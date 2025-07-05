// Modal de Editar Compra
document.addEventListener('DOMContentLoaded', function() {
    const editarCompraModal = document.getElementById('editarCompraModal');
    if (editarCompraModal) {
        editarCompraModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const compraId = button.getAttribute('data-compra-id');
            const estoqueId = button.getAttribute('data-estoque-id');
            const fornecedorId = button.getAttribute('data-fornecedor-id');
            const compradorId = button.getAttribute('data-comprador-id');

            // Preencher os campos do modal
            document.getElementById('edit-compra-id').value = compraId;
            document.getElementById('edit-estoque').value = estoqueId;
            document.getElementById('edit-fornecedor').value = fornecedorId;
            document.getElementById('edit-comprador').value = compradorId;
        });
    }

    // Modal de Excluir Compra
    const excluirCompraModal = document.getElementById('excluirCompraModal');
    if (excluirCompraModal) {
        excluirCompraModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const compraId = button.getAttribute('data-compra-id');
            const compraInfo = button.getAttribute('data-compra-info');

            document.getElementById('delete-compra-id').value = compraId;
            document.getElementById('delete-compra-info').textContent = compraInfo;
        });
    }

    // Modal de Detalhes da Compra
    const detalhesCompraModal = document.getElementById('detalhesCompraModal');
    if (detalhesCompraModal) {
        detalhesCompraModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const compraId = button.getAttribute('data-compra-id');
            
            const content = document.getElementById('detalhes-compra-content');
            content.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <p class="mt-2">Carregando detalhes da compra #${compraId}...</p>
                </div>
            `;
            
            // Fazer requisição AJAX para buscar os detalhes
            fetch(`/administrador/compras/${compraId}/detalhes/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const compra = data.compra;
                        let itensHtml = '';
                        
                        compra.itens.forEach(item => {
                            itensHtml += `
                                <tr>
                                    <td>${item.produto_nome}</td>
                                    <td>${item.produto_codigo}</td>
                                    <td>${item.local_nome}</td>
                                    <td class="text-center">${item.quantidade}</td>
                                    <td class="text-end">R$ ${item.valor_unitario.toFixed(2)}</td>
                                    <td class="text-end">R$ ${item.subtotal.toFixed(2)}</td>
                                </tr>
                            `;
                        });
                        
                        content.innerHTML = `
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-primary">Informações da Compra</h6>
                                    <table class="table table-borderless table-sm">
                                        <tr>
                                            <td><strong>ID:</strong></td>
                                            <td>#${compra.id}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Data:</strong></td>
                                            <td>${compra.data}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Estoque:</strong></td>
                                            <td>${compra.estoque}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Total de Itens:</strong></td>
                                            <td>${compra.total_itens}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Valor Total:</strong></td>
                                            <td class="text-success"><strong>R$ ${compra.valor_total.toFixed(2)}</strong></td>
                                        </tr>
                                        ${compra.invoice_url ? `
                                        <tr>
                                            <td><strong>Invoice:</strong></td>
                                            <td><a href="${compra.invoice_url}" target="_blank" class="btn btn-sm btn-outline-primary">
                                                <i class="bi bi-file-pdf"></i> Visualizar PDF
                                            </a></td>
                                        </tr>
                                        ` : ''}
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-primary">Fornecedor</h6>
                                    <table class="table table-borderless table-sm">
                                        <tr>
                                            <td><strong>Nome:</strong></td>
                                            <td>${compra.fornecedor.nome}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>CNPJ:</strong></td>
                                            <td>${compra.fornecedor.cnpj}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Email:</strong></td>
                                            <td>${compra.fornecedor.email}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Telefone:</strong></td>
                                            <td>${compra.fornecedor.telefone}</td>
                                        </tr>
                                    </table>
                                    
                                    <h6 class="text-primary mt-4">Comprador</h6>
                                    <table class="table table-borderless table-sm">
                                        <tr>
                                            <td><strong>Nome:</strong></td>
                                            <td>${compra.comprador.nome}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Email:</strong></td>
                                            <td>${compra.comprador.email}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            
                            <hr class="my-4">
                            
                            <h6 class="text-primary mb-3">Itens da Compra</h6>
                            <div class="table-responsive">
                                <table class="table table-striped table-hover">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Produto</th>
                                            <th>Código</th>
                                            <th>Local</th>
                                            <th class="text-center">Quantidade</th>
                                            <th class="text-end">Valor Unit.</th>
                                            <th class="text-end">Subtotal</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${itensHtml}
                                    </tbody>
                                    <tfoot class="table-dark">
                                        <tr>
                                            <th colspan="5" class="text-end">Total Geral:</th>
                                            <th class="text-end">R$ ${compra.valor_total.toFixed(2)}</th>
                                        </tr>
                                    </tfoot>
                                </table>
                            </div>
                        `;
                    } else {
                        content.innerHTML = `
                            <div class="alert alert-danger" role="alert">
                                <h6 class="alert-heading">Erro ao carregar detalhes</h6>
                                <p class="mb-0">${data.error}</p>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    content.innerHTML = `
                        <div class="alert alert-danger" role="alert">
                            <h6 class="alert-heading">Erro de conexão</h6>
                            <p class="mb-0">Não foi possível carregar os detalhes da compra. Tente novamente.</p>
                        </div>
                    `;
                });
        });
    }

    // Adicionar/Remover itens na compra
    const addItemBtn = document.getElementById('add-item');
    if (addItemBtn) {
        addItemBtn.addEventListener('click', function() {
            const itensContainer = document.getElementById('itens-compra');
            const firstItem = itensContainer.querySelector('.item-compra');
            const newItem = firstItem.cloneNode(true);
            
            // Limpar valores dos campos clonados
            const inputs = newItem.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'number') {
                    input.value = '';
                } else {
                    input.selectedIndex = 0;
                }
            });
            
            // Mostrar botão de remover
            const removeBtn = newItem.querySelector('.remove-item');
            removeBtn.style.display = 'block';
            
            itensContainer.appendChild(newItem);
            updateRemoveButtons();
        });
    }

    // Função para atualizar botões de remover
    function updateRemoveButtons() {
        const items = document.querySelectorAll('.item-compra');
        const removeButtons = document.querySelectorAll('.remove-item');
        
        removeButtons.forEach((btn, index) => {
            if (items.length > 1) {
                btn.style.display = 'block';
                btn.onclick = function() {
                    if (items.length > 1) {
                        btn.closest('.item-compra').remove();
                        updateRemoveButtons();
                    }
                };
            } else {
                btn.style.display = 'none';
            }
        });
    }

    // Inicializar botões de remover
    updateRemoveButtons();

    // Event delegation para botões de remover que serão criados dinamicamente
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-item') || e.target.closest('.remove-item')) {
            const items = document.querySelectorAll('.item-compra');
            if (items.length > 1) {
                const item = e.target.closest('.item-compra');
                if (item) {
                    item.remove();
                    updateRemoveButtons();
                }
            }
        }
    });
});
