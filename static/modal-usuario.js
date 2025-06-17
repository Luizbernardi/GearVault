// modal-usuario.js

document.addEventListener('DOMContentLoaded', function () {
  var editarUsuarioModal = document.getElementById('editarUsuarioModal');
  if (editarUsuarioModal) {
    editarUsuarioModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('edit-user-id').value = button.getAttribute('data-user-id');
      document.getElementById('edit-username').value = button.getAttribute('data-username');
      document.getElementById('edit-email').value = button.getAttribute('data-email');
      document.getElementById('edit-role').value = button.getAttribute('data-role');
    });
  }
  var excluirUsuarioModal = document.getElementById('excluirUsuarioModal');
  if (excluirUsuarioModal) {
    excluirUsuarioModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('delete-user-id').value = button.getAttribute('data-user-id');
      document.getElementById('delete-username').textContent = button.getAttribute('data-username');
    });
  }
});
