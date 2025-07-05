// Modal de Editar Estoque
document.addEventListener('DOMContentLoaded', function() {
    const editarEstoqueModal = document.getElementById('editarEstoqueModal');
    if (editarEstoqueModal) {
        editarEstoqueModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const estoqueId = button.getAttribute('data-estoque-id');
            const nome = button.getAttribute('data-nome');
            const descricao = button.getAttribute('data-descricao');

            // Preencher os campos do modal
            document.getElementById('edit-estoque-id').value = estoqueId;
            document.getElementById('edit-nome').value = nome;
            document.getElementById('edit-descricao').value = descricao || '';
        });
    }

    // Modal de Excluir Estoque
    const excluirEstoqueModal = document.getElementById('excluirEstoqueModal');
    if (excluirEstoqueModal) {
        excluirEstoqueModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const estoqueId = button.getAttribute('data-estoque-id');
            const nome = button.getAttribute('data-nome');

            document.getElementById('delete-estoque-id').value = estoqueId;
            document.getElementById('delete-estoque-nome').textContent = nome;
        });
    }
});
