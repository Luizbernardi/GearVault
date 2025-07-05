// Modal de Editar Local
document.addEventListener('DOMContentLoaded', function() {
    const editarLocalModal = document.getElementById('editarLocalModal');
    if (editarLocalModal) {
        editarLocalModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const localId = button.getAttribute('data-local-id');
            const nome = button.getAttribute('data-nome');
            const descricao = button.getAttribute('data-descricao');
            const estoqueId = button.getAttribute('data-estoque-id');

            // Preencher os campos do modal
            document.getElementById('edit-local-id').value = localId;
            document.getElementById('edit-nome').value = nome;
            document.getElementById('edit-descricao').value = descricao || '';
            document.getElementById('edit-estoque').value = estoqueId;
        });
    }

    // Modal de Excluir Local
    const excluirLocalModal = document.getElementById('excluirLocalModal');
    if (excluirLocalModal) {
        excluirLocalModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const localId = button.getAttribute('data-local-id');
            const nome = button.getAttribute('data-nome');

            document.getElementById('delete-local-id').value = localId;
            document.getElementById('delete-local-nome').textContent = nome;
        });
    }
});
