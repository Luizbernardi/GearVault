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
