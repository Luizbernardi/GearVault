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

            // Carregar itens da compra via AJAX
            loadCompraItens(compraId, estoqueId);
        });
    }

    // Função para carregar itens da compra
    function loadCompraItens(compraId, estoqueId) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/administrador/compras/${compraId}/detalhes-ajax/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.itens) {
                // Limpar container de itens
                const itensContainer = document.getElementById('edit-itens-compra');
                itensContainer.innerHTML = '';
                
                // Carregar locais do estoque primeiro
                loadEditLocaisAndPopulateItems(estoqueId, data.itens);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar itens da compra:', error);
        });
    }

    function loadEditLocaisAndPopulateItems(estoqueId, itens) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/usuario/estoques/${estoqueId}/locais/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.locais) {
                // Agora criar os itens com os locais disponíveis
                const itensContainer = document.getElementById('edit-itens-compra');
                
                itens.forEach((item, index) => {
                    const itemDiv = createEditItemRowFromExisting(item, data.locais, index === 0);
                    itensContainer.appendChild(itemDiv);
                });
                
                updateEditRemoveButtons();
            }
        })
        .catch(error => {
            console.error('Erro ao carregar locais:', error);
        });
    }

    function createEditItemRowFromExisting(item, locais, isFirst) {
        const div = document.createElement('div');
        div.className = 'item-compra row mb-3';
        
        // Buscar produtos do template
        const produtoOptions = Array.from(document.querySelectorAll('#edit-produto-template option')).map(opt => ({
            value: opt.value,
            text: opt.textContent
        }));
        
        // Criar select de produtos
        const produtoSelect = `
            <select class="form-select" name="produto_id[]" required>
                <option value="">Selecione um produto</option>
                ${produtoOptions.map(opt => 
                    `<option value="${opt.value}" ${opt.value == item.produto_id ? 'selected' : ''}>${opt.text}</option>`
                ).join('')}
            </select>
        `;
        
        // Criar select de locais
        const localSelect = `
            <select class="form-select edit-local-select" name="local_id[]" required>
                <option value="">Selecione um local</option>
                ${locais.map(local => 
                    `<option value="${local.id}" ${local.id == item.local_id ? 'selected' : ''}>${local.nome}</option>`
                ).join('')}
            </select>
        `;
        
        div.innerHTML = `
            <div class="col-md-3">
                <label class="form-label">Produto</label>
                ${produtoSelect}
            </div>
            <div class="col-md-3">
                <label class="form-label">Local</label>
                ${localSelect}
            </div>
            <div class="col-md-2">
                <label class="form-label">Quantidade</label>
                <input type="number" class="form-control" name="quantidade[]" value="${item.quantidade}" required min="1">
            </div>
            <div class="col-md-3">
                <label class="form-label">Valor Unitário (R$)</label>
                <input type="number" class="form-control" name="valor_unitario[]" value="${item.valor_unitario.toFixed(2)}" required min="0.01" step="0.01">
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="button" class="btn btn-danger edit-remove-item" style="display: ${isFirst ? 'none' : 'block'};">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        return div;
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

    // ===== PROCESSAR INVOICE AUTOMATICAMENTE =====
    const invoiceInput = document.getElementById('add-invoice');
    if (invoiceInput) {
        invoiceInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            // Verificar se é PDF
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                alert('Por favor, selecione um arquivo PDF.');
                invoiceInput.value = '';
                return;
            }
            
            // Mostrar loading
            showInvoiceProcessing();
            
            // Criar FormData e enviar para o servidor
            const formData = new FormData();
            formData.append('invoice', file);
            
            // Obter CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/administrador/compras/process-invoice/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                hideInvoiceProcessing();
                
                if (data.error) {
                    alert('Erro ao processar invoice: ' + data.error);
                    return;
                }
                
                if (data.warning) {
                    alert(data.warning);
                }
                
                if (data.items && data.items.length > 0) {
                    // Preencher itens automaticamente
                    populateItemsFromInvoice(data.items);
                    
                    // Mostrar mensagem de sucesso
                    showSuccessMessage(data.message || `${data.items.length} itens carregados da invoice`);
                }
                
                // Preencher informações da invoice se disponíveis
                if (data.invoice_info) {
                    populateInvoiceInfo(data.invoice_info);
                }
            })
            .catch(error => {
                hideInvoiceProcessing();
                console.error('Erro:', error);
                alert('Erro ao processar invoice. Por favor, tente novamente.');
            });
        });
    }

    // ===== PROCESSAR INVOICE NO MODAL DE EDIÇÃO =====
    const editInvoiceInput = document.getElementById('edit-invoice');
    if (editInvoiceInput) {
        editInvoiceInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            // Verificar se é PDF
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                alert('Por favor, selecione um arquivo PDF.');
                editInvoiceInput.value = '';
                return;
            }
            
            // Mostrar loading
            showEditInvoiceProcessing();
            
            // Criar FormData e enviar para o servidor
            const formData = new FormData();
            formData.append('invoice', file);
            
            // Obter CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch('/administrador/compras/process-invoice/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                hideEditInvoiceProcessing();
                
                if (data.error) {
                    alert('Erro ao processar invoice: ' + data.error);
                    return;
                }
                
                if (data.warning) {
                    alert(data.warning);
                }
                
                if (data.items && data.items.length > 0) {
                    // Preencher itens automaticamente
                    populateEditItemsFromInvoice(data.items);
                    
                    // Mostrar mensagem de sucesso
                    showEditSuccessMessage(data.message || `${data.items.length} itens carregados da invoice`);
                }
                
                // Preencher informações da invoice se disponíveis
                if (data.invoice_info) {
                    populateEditInvoiceInfo(data.invoice_info);
                }
            })
            .catch(error => {
                hideEditInvoiceProcessing();
                console.error('Erro:', error);
                alert('Erro ao processar invoice. Por favor, tente novamente.');
            });
        });
    }
    
    function showInvoiceProcessing() {
        const container = document.getElementById('itens-compra');
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'invoice-loading';
        loadingDiv.className = 'alert alert-info';
        loadingDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Processando...</span>
                </div>
                <span>Processando invoice e extraindo itens...</span>
            </div>
        `;
        container.parentNode.insertBefore(loadingDiv, container);
    }
    
    function hideInvoiceProcessing() {
        const loadingDiv = document.getElementById('invoice-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    function showEditInvoiceProcessing() {
        const container = document.getElementById('edit-itens-compra');
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'edit-invoice-loading';
        loadingDiv.className = 'alert alert-info';
        loadingDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Processando...</span>
                </div>
                <span>Processando invoice e extraindo itens...</span>
            </div>
        `;
        container.parentNode.insertBefore(loadingDiv, container);
    }
    
    function hideEditInvoiceProcessing() {
        const loadingDiv = document.getElementById('edit-invoice-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
    
    function showSuccessMessage(message) {
        const container = document.getElementById('itens-compra');
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.parentNode.insertBefore(successDiv, container);
        
        // Auto remove após 5 segundos
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }
    
    function populateItemsFromInvoice(items) {
        const itensContainer = document.getElementById('itens-compra');
        
        // Limpar itens existentes
        itensContainer.innerHTML = '';
        
        // Adicionar cada item
        items.forEach((item, index) => {
            const itemDiv = createItemRow(item, index === 0);
            itensContainer.appendChild(itemDiv);
        });
        
        updateRemoveButtons();
    }
    
    function createItemRow(item, isFirst) {
        const div = document.createElement('div');
        div.className = 'item-compra row mb-3';
        
        // Verifica se produto foi encontrado no banco
        const produtoOptions = Array.from(document.querySelectorAll('#add-produto-template option')).map(opt => ({
            value: opt.value,
            text: opt.textContent
        }));
        
        let produtoSelect = '';
        if (item.produto_id) {
            // Produto encontrado - pré-selecionar
            produtoSelect = `
                <select class="form-select" name="produto_id[]" required>
                    <option value="">Selecione um produto</option>
                    ${produtoOptions.map(opt => 
                        `<option value="${opt.value}" ${opt.value == item.produto_id ? 'selected' : ''}>${opt.text}</option>`
                    ).join('')}
                </select>
            `;
        } else {
            // Produto não encontrado - mostrar informação
            produtoSelect = `
                <select class="form-select" name="produto_id[]" required>
                    <option value="">Selecione um produto</option>
                    ${produtoOptions.map(opt => 
                        `<option value="${opt.value}">${opt.text}</option>`
                    ).join('')}
                </select>
            `;
        }
        
        div.innerHTML = `
            <div class="col-md-3">
                <label class="form-label">Produto</label>
                ${produtoSelect}
            </div>
            <div class="col-md-3">
                <label class="form-label">Local</label>
                <select class="form-select local-select" name="local_id[]" required>
                    <option value="">Selecione o estoque primeiro</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Quantidade</label>
                <input type="number" class="form-control" name="quantidade[]" value="${item.quantidade}" required min="1">
            </div>
            <div class="col-md-3">
                <label class="form-label">Valor Unitário (R$)</label>
                <input type="number" class="form-control" name="valor_unitario[]" value="${item.valor_unitario.toFixed(2)}" required min="0.01" step="0.01">
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="button" class="btn btn-danger remove-item" style="display: ${isFirst ? 'none' : 'block'};">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        return div;
    }
    
    function populateInvoiceInfo(info) {
        // Se tiver CNPJ, tentar identificar fornecedor
        if (info.fornecedor_cnpj) {
            const fornecedorSelect = document.getElementById('add-fornecedor');
            if (fornecedorSelect) {
                const options = fornecedorSelect.querySelectorAll('option');
                options.forEach(option => {
                    // Aqui você pode adicionar lógica para match de CNPJ
                    // Por enquanto, apenas mostra info
                });
            }
        }
        
       
    }

    // ===== FUNÇÕES PARA MODAL DE EDIÇÃO =====
    function populateEditItemsFromInvoice(items) {
        const itensContainer = document.getElementById('edit-itens-compra');
        
        // Limpar itens existentes
        itensContainer.innerHTML = '';
        
        // Adicionar cada item
        items.forEach((item, index) => {
            const itemDiv = createEditItemRow(item, index === 0);
            itensContainer.appendChild(itemDiv);
        });
        
        updateEditRemoveButtons();
    }

    function createEditItemRow(item, isFirst) {
        const div = document.createElement('div');
        div.className = 'item-compra row mb-3';
        
        // Verifica se produto foi encontrado no banco
        const produtoOptions = Array.from(document.querySelectorAll('#edit-produto-template option')).map(opt => ({
            value: opt.value,
            text: opt.textContent
        }));
        
        let produtoSelect = '';
        if (item.produto_id) {
            // Produto encontrado - pré-selecionar
            produtoSelect = `
                <select class="form-select" name="produto_id[]" required>
                    <option value="">Selecione um produto</option>
                    ${produtoOptions.map(opt => 
                        `<option value="${opt.value}" ${opt.value == item.produto_id ? 'selected' : ''}>${opt.text}</option>`
                    ).join('')}
                </select>
                <small class="text-success">Produto identificado (${Math.round(item.match_score * 100)}% match)</small>
            `;
        } else {
            // Produto não encontrado - mostrar informação
            produtoSelect = `
                <select class="form-select" name="produto_id[]" required>
                    <option value="">Selecione um produto</option>
                    ${produtoOptions.map(opt => 
                        `<option value="${opt.value}">${opt.text}</option>`
                    ).join('')}
                </select>
                <small class="text-warning">Produto "${item.descricao}" não encontrado - selecione manualmente</small>
            `;
        }
        
        div.innerHTML = `
            <div class="col-md-3">
                <label class="form-label">Produto</label>
                ${produtoSelect}
            </div>
            <div class="col-md-3">
                <label class="form-label">Local</label>
                <select class="form-select edit-local-select" name="local_id[]" required>
                    <option value="">Selecione o estoque primeiro</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Quantidade</label>
                <input type="number" class="form-control" name="quantidade[]" value="${item.quantidade}" required min="1">
            </div>
            <div class="col-md-3">
                <label class="form-label">Valor Unitário (R$)</label>
                <input type="number" class="form-control" name="valor_unitario[]" value="${item.valor_unitario.toFixed(2)}" required min="0.01" step="0.01">
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="button" class="btn btn-danger edit-remove-item" style="display: ${isFirst ? 'none' : 'block'};">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        `;
        
        return div;
    }

    function showEditSuccessMessage(message) {
        const container = document.getElementById('edit-itens-compra');
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        container.parentNode.insertBefore(successDiv, container);
        
        // Auto remove após 5 segundos
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }

    function populateEditInvoiceInfo(info) {
        if (info.numero_nf || info.data_emissao) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'alert alert-info mb-3';
            infoDiv.innerHTML = `
                <strong>Informações da Invoice:</strong><br>
                ${info.numero_nf ? `NF: ${info.numero_nf}<br>` : ''}
                ${info.data_emissao ? `Data: ${info.data_emissao}<br>` : ''}
                ${info.fornecedor_nome ? `Fornecedor: ${info.fornecedor_nome}<br>` : ''}
                ${info.fornecedor_cnpj ? `CNPJ: ${info.fornecedor_cnpj}` : ''}
            `;
            
            const modalBody = document.querySelector('#editarCompraModal .modal-body');
            const existingInfo = modalBody.querySelector('.alert-info');
            if (existingInfo) {
                existingInfo.remove();
            }
            modalBody.insertBefore(infoDiv, modalBody.firstChild);
        }
    }

    function updateEditRemoveButtons() {
        const items = document.querySelectorAll('#edit-itens-compra .item-compra');
        const removeButtons = document.querySelectorAll('.edit-remove-item');
        
        removeButtons.forEach((btn, index) => {
            if (items.length > 1) {
                btn.style.display = 'block';
                btn.onclick = function() {
                    if (items.length > 1) {
                        btn.closest('.item-compra').remove();
                        updateEditRemoveButtons();
                    }
                };
            } else {
                btn.style.display = 'none';
            }
        });
    }

    // Carregar locais quando o estoque for alterado no modal de edição
    const editEstoqueSelect = document.getElementById('edit-estoque');
    if (editEstoqueSelect) {
        editEstoqueSelect.addEventListener('change', function() {
            const estoqueId = this.value;
            updateEditLocaisForEstoque(estoqueId);
        });
    }

    function updateEditLocaisForEstoque(estoqueId) {
        if (!estoqueId) {
            document.querySelectorAll('.edit-local-select').forEach(select => {
                select.innerHTML = '<option value="">Selecione o estoque primeiro</option>';
            });
            return;
        }
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/usuario/estoques/${estoqueId}/locais/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.locais) {
                document.querySelectorAll('.edit-local-select').forEach(select => {
                    select.innerHTML = '<option value="">Selecione um local</option>';
                    data.locais.forEach(local => {
                        const option = document.createElement('option');
                        option.value = local.id;
                        option.textContent = local.nome;
                        select.appendChild(option);
                    });
                });
            }
        })
        .catch(error => {
            console.error('Erro ao carregar locais:', error);
        });
    }

    // Botão adicionar item no modal de edição
    const editAddItemBtn = document.getElementById('edit-add-item');
    if (editAddItemBtn) {
        editAddItemBtn.addEventListener('click', function() {
            const item = {
                codigo: '',
                descricao: '',
                quantidade: 1,
                valor_unitario: 0,
                produto_id: null
            };
            const itemDiv = createEditItemRow(item, false);
            document.getElementById('edit-itens-compra').appendChild(itemDiv);
            updateEditRemoveButtons();
            
            // Atualizar locais se já houver estoque selecionado
            const estoqueId = document.getElementById('edit-estoque').value;
            if (estoqueId) {
                updateEditLocaisForEstoque(estoqueId);
            }
        });
    }
    
    // Carregar locais quando o estoque for alterado
    const estoqueSelect = document.getElementById('add-estoque');
    if (estoqueSelect) {
        estoqueSelect.addEventListener('change', function() {
            const estoqueId = this.value;
            updateLocaisForEstoque(estoqueId);
        });
    }
    
    function updateLocaisForEstoque(estoqueId) {
        if (!estoqueId) {
            // Limpar todos os selects de local
            document.querySelectorAll('.local-select').forEach(select => {
                select.innerHTML = '<option value="">Selecione o estoque primeiro</option>';
            });
            return;
        }
        
        // Buscar locais via AJAX
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/usuario/estoques/${estoqueId}/locais/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.locais) {
                // Atualizar todos os selects de local
                document.querySelectorAll('.local-select').forEach(select => {
                    select.innerHTML = '<option value="">Selecione um local</option>';
                    data.locais.forEach(local => {
                        const option = document.createElement('option');
                        option.value = local.id;
                        option.textContent = local.nome;
                        select.appendChild(option);
                    });
                });
            }
        })
        .catch(error => {
            console.error('Erro ao carregar locais:', error);
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
