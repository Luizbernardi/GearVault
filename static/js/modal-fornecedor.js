// js/modal-fornecedor.js

document.addEventListener('DOMContentLoaded', function () {
  // Funcionalidade para expandir o modal de cadastro com campos de novo endereço
  const btnNovoEnderecoAdd = document.getElementById('btn-novo-endereco-add');
  const camposNovoEnderecoAdd = document.getElementById('campos-novo-endereco-add');
  const selectEnderecoExistenteAdd = document.getElementById('add-endereco-existente');

  if (btnNovoEnderecoAdd && camposNovoEnderecoAdd) {
    btnNovoEnderecoAdd.addEventListener('click', function() {
      if (camposNovoEnderecoAdd.style.display === 'none') {
        camposNovoEnderecoAdd.style.display = 'block';
        btnNovoEnderecoAdd.innerHTML = '<i class="bi bi-dash"></i> Cancelar';
        btnNovoEnderecoAdd.classList.remove('btn-outline-primary');
        btnNovoEnderecoAdd.classList.add('btn-outline-secondary');
        selectEnderecoExistenteAdd.value = '';
        selectEnderecoExistenteAdd.disabled = true;
        
        // Tornar campos obrigatórios
        document.getElementById('add-logradouro').required = true;
        document.getElementById('add-numero').required = true;
        document.getElementById('add-bairro').required = true;
        document.getElementById('add-cidade').required = true;
        document.getElementById('add-estado').required = true;
        document.getElementById('add-cep').required = true;
      } else {
        camposNovoEnderecoAdd.style.display = 'none';
        btnNovoEnderecoAdd.innerHTML = '<i class="bi bi-plus"></i> Novo';
        btnNovoEnderecoAdd.classList.remove('btn-outline-secondary');
        btnNovoEnderecoAdd.classList.add('btn-outline-primary');
        selectEnderecoExistenteAdd.disabled = false;
        
        // Remover obrigatoriedade dos campos
        document.getElementById('add-logradouro').required = false;
        document.getElementById('add-numero').required = false;
        document.getElementById('add-bairro').required = false;
        document.getElementById('add-cidade').required = false;
        document.getElementById('add-estado').required = false;
        document.getElementById('add-cep').required = false;
        
        // Limpar campos
        document.getElementById('add-logradouro').value = '';
        document.getElementById('add-numero').value = '';
        document.getElementById('add-bairro').value = '';
        document.getElementById('add-complemento').value = '';
        document.getElementById('add-cidade').value = '';
        document.getElementById('add-estado').value = '';
        document.getElementById('add-cep').value = '';
      }
    });
  }

  // Funcionalidade para modal de edição
  const btnEditarEnderecoEdit = document.getElementById('btn-editar-endereco-edit');
  const camposEditarEnderecoEdit = document.getElementById('campos-editar-endereco-edit');
  const selectEnderecoExistenteEdit = document.getElementById('edit-endereco-existente');

  if (btnEditarEnderecoEdit && selectEnderecoExistenteEdit) {
    // Listener para mudança no select de endereço existente
    selectEnderecoExistenteEdit.addEventListener('change', function() {
      if (this.value) {
        // Buscar dados do endereço selecionado via AJAX ou usar data attributes
        // Por simplicidade, vamos só mostrar/esconder os campos
        camposEditarEnderecoEdit.style.display = 'block';
        btnEditarEnderecoEdit.style.display = 'inline-block';
      } else {
        camposEditarEnderecoEdit.style.display = 'none';
      }
    });
  }

  // Modal de edição de fornecedor
  var editarFornecedorModal = document.getElementById('editarFornecedorModal');
  if (editarFornecedorModal) {
    editarFornecedorModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('edit-fornecedor-id').value = button.getAttribute('data-fornecedor-id');
      document.getElementById('edit-nome').value = button.getAttribute('data-nome');
      document.getElementById('edit-cnpj').value = button.getAttribute('data-cnpj');
      document.getElementById('edit-email').value = button.getAttribute('data-email');
      document.getElementById('edit-telefone').value = button.getAttribute('data-telefone');
      
      // Preencher campos de endereço se existirem
      const logradouro = button.getAttribute('data-logradouro');
      const numero = button.getAttribute('data-numero');
      const bairro = button.getAttribute('data-bairro');
      const complemento = button.getAttribute('data-complemento');
      const cidade = button.getAttribute('data-cidade');
      const estado = button.getAttribute('data-estado');
      const cep = button.getAttribute('data-cep');

      if (logradouro) {
        document.getElementById('edit-logradouro').value = logradouro || '';
        document.getElementById('edit-numero').value = numero || '';
        document.getElementById('edit-bairro').value = bairro || '';
        document.getElementById('edit-complemento').value = complemento || '';
        document.getElementById('edit-cidade').value = cidade || '';
        document.getElementById('edit-estado').value = estado || '';
        document.getElementById('edit-cep').value = cep || '';
        
        // Mostrar campos de endereço
        camposEditarEnderecoEdit.style.display = 'block';
      }
    });
  }
  
  // Modal de exclusão de fornecedor
  var excluirFornecedorModal = document.getElementById('excluirFornecedorModal');
  if (excluirFornecedorModal) {
    excluirFornecedorModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget;
      document.getElementById('delete-fornecedor-id').value = button.getAttribute('data-fornecedor-id');
      document.getElementById('delete-fornecedor-nome').textContent = button.getAttribute('data-nome');
    });
  }
});
