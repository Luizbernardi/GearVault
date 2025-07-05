// js/modal-produto.js
// Preenche os campos dos modais de edição e exclusão de produto com os dados do botão clicado

document.addEventListener('DOMContentLoaded', function() {
  // Modal Editar Produto
  var editarModal = document.getElementById('editarProdutoModal');
  if (editarModal) {
    editarModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('edit-produto-id').value = button.getAttribute('data-produto-id');
      document.getElementById('edit-nome').value = button.getAttribute('data-nome');
      document.getElementById('edit-codigo').value = button.getAttribute('data-codigo');
      document.getElementById('edit-categoria').value = button.getAttribute('data-categoria') || '';
      document.getElementById('edit-descricao').value = button.getAttribute('data-descricao') || '';
      document.getElementById('edit-fornecedor').value = button.getAttribute('data-fornecedor-id') || '';
      // Não preenche imagem, pois não é possível por segurança
    });
  }
  // Modal Excluir Produto
  var excluirModal = document.getElementById('excluirProdutoModal');
  if (excluirModal) {
    excluirModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('delete-produto-id').value = button.getAttribute('data-produto-id');
      document.getElementById('delete-produto-nome').textContent = button.getAttribute('data-nome');
    });
  }
});
