// modal-fornecedor.js

document.addEventListener('DOMContentLoaded', function () {
  var editarFornecedorModal = document.getElementById('editarFornecedorModal');
  if (editarFornecedorModal) {
    editarFornecedorModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('edit-fornecedor-id').value = button.getAttribute('data-fornecedor-id');
      document.getElementById('edit-nome').value = button.getAttribute('data-nome');
      document.getElementById('edit-cnpj').value = button.getAttribute('data-cnpj');
      document.getElementById('edit-email').value = button.getAttribute('data-email');
      document.getElementById('edit-telefone').value = button.getAttribute('data-telefone');
      document.getElementById('edit-endereco').value = button.getAttribute('data-endereco');
    });
  }
  var excluirFornecedorModal = document.getElementById('excluirFornecedorModal');
  if (excluirFornecedorModal) {
    excluirFornecedorModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('delete-fornecedor-id').value = button.getAttribute('data-fornecedor-id');
      document.getElementById('delete-fornecedor-nome').textContent = button.getAttribute('data-nome');
    });
  }
});
