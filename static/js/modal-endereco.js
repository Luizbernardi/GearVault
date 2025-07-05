// Modal de Editar Endereço
document.addEventListener('DOMContentLoaded', function() {
    const editarEnderecoModal = document.getElementById('editarEnderecoModal');
    if (editarEnderecoModal) {
        editarEnderecoModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const enderecoId = button.getAttribute('data-endereco-id');
            const logradouro = button.getAttribute('data-logradouro');
            const numero = button.getAttribute('data-numero');
            const complemento = button.getAttribute('data-complemento');
            const bairro = button.getAttribute('data-bairro');
            const cidade = button.getAttribute('data-cidade');
            const estado = button.getAttribute('data-estado');
            const cep = button.getAttribute('data-cep');

            // Preencher os campos do modal
            document.getElementById('edit-endereco-id').value = enderecoId;
            document.getElementById('edit-logradouro').value = logradouro;
            document.getElementById('edit-numero').value = numero;
            document.getElementById('edit-complemento').value = complemento || '';
            document.getElementById('edit-bairro').value = bairro;
            document.getElementById('edit-cidade').value = cidade;
            document.getElementById('edit-estado').value = estado;
            document.getElementById('edit-cep').value = cep;
        });
    }

    // Modal de Excluir Endereço
    const excluirEnderecoModal = document.getElementById('excluirEnderecoModal');
    if (excluirEnderecoModal) {
        excluirEnderecoModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const enderecoId = button.getAttribute('data-endereco-id');
            const enderecoInfo = button.getAttribute('data-endereco-info');

            document.getElementById('delete-endereco-id').value = enderecoId;
            document.getElementById('delete-endereco-info').textContent = enderecoInfo;
        });
    }

    // Máscara para CEP
    const cepInputs = document.querySelectorAll('#add-cep, #edit-cep');
    cepInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 8) value = value.substring(0, 8);
            e.target.value = value;
        });
    });
});
