// Modal de Excluir Comprador
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
});
