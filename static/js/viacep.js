// Integração com API ViaCEP
document.addEventListener('DOMContentLoaded', function() {
    
    // Função para limpar campos de endereço
    function limparCamposEndereco(prefixo) {
        document.getElementById(prefixo + '-logradouro').value = '';
        document.getElementById(prefixo + '-bairro').value = '';
        document.getElementById(prefixo + '-cidade').value = '';
        document.getElementById(prefixo + '-estado').value = '';
    }
    
    // Função para preencher campos de endereço
    function preencherCamposEndereco(prefixo, dados) {
        const campos = [
            { id: prefixo + '-logradouro', valor: dados.logradouro },
            { id: prefixo + '-bairro', valor: dados.bairro },
            { id: prefixo + '-cidade', valor: dados.localidade },
            { id: prefixo + '-estado', valor: dados.uf }
        ];
        
        campos.forEach(campo => {
            const elemento = document.getElementById(campo.id);
            if (elemento && campo.valor) {
                elemento.value = campo.valor;
                
                // Adiciona animação visual
                elemento.classList.add('campo-preenchido');
                setTimeout(() => {
                    elemento.classList.remove('campo-preenchido');
                }, 2000);
            }
        });
    }
    
    // Função para mostrar mensagem de erro
    function mostrarErro(prefixo, mensagem) {
        const cepField = document.getElementById(prefixo + '-cep');
        
        // Remove classe de erro anterior
        cepField.classList.remove('is-invalid');
        
        // Remove feedback anterior
        const feedbackAnterior = cepField.parentNode.querySelector('.invalid-feedback');
        if (feedbackAnterior) {
            feedbackAnterior.remove();
        }
        
        // Adiciona classe de erro
        cepField.classList.add('is-invalid');
        
        // Cria elemento de feedback
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        feedback.textContent = mensagem;
        
        // Insere o feedback após o campo
        cepField.parentNode.appendChild(feedback);
        
        // Remove o erro após 3 segundos
        setTimeout(() => {
            cepField.classList.remove('is-invalid');
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 3000);
    }
    
    // Função para mostrar sucesso
    function mostrarSucesso(prefixo) {
        const cepField = document.getElementById(prefixo + '-cep');
        
        // Remove classes anteriores
        cepField.classList.remove('is-invalid', 'is-valid');
        
        // Remove feedback anterior
        const feedbackAnterior = cepField.parentNode.querySelector('.invalid-feedback, .valid-feedback');
        if (feedbackAnterior) {
            feedbackAnterior.remove();
        }
        
        // Adiciona classe de sucesso
        cepField.classList.add('is-valid');
        
        // Remove a classe de sucesso após 2 segundos
        setTimeout(() => {
            cepField.classList.remove('is-valid');
        }, 2000);
    }
    
    // Função para validar CEP
    function validarCEP(cep) {
        const cepRegex = /^[0-9]{8}$/;
        return cepRegex.test(cep.replace(/\D/g, ''));
    }
    
    // Função para formatar CEP
    function formatarCEP(cep) {
        cep = cep.replace(/\D/g, '');
        if (cep.length === 8) {
            return cep.replace(/^(\d{5})(\d{3})$/, '$1-$2');
        }
        return cep;
    }
    
    // Função para buscar CEP
    function buscarCEP(cep, prefixo) {
        // Remove formatação do CEP
        const cepLimpo = cep.replace(/\D/g, '');
        
        // Valida CEP
        if (!validarCEP(cepLimpo)) {
            mostrarErro(prefixo, 'CEP inválido. Digite apenas números (8 dígitos).');
            return;
        }
        
        // Mostra loading
        const cepField = document.getElementById(prefixo + '-cep');
        const valorOriginal = cepField.value;
        cepField.value = 'Buscando...';
        cepField.disabled = true;
        
        // Faz a requisição
        fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
            .then(response => response.json())
            .then(data => {
                // Restaura o campo CEP
                cepField.disabled = false;
                cepField.value = formatarCEP(cepLimpo);
                
                if (data.erro) {
                    mostrarErro(prefixo, 'CEP não encontrado.');
                    limparCamposEndereco(prefixo);
                } else {
                    preencherCamposEndereco(prefixo, data);
                    mostrarSucesso(prefixo);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar CEP:', error);
                cepField.disabled = false;
                cepField.value = valorOriginal;
                mostrarErro(prefixo, 'Erro ao buscar CEP. Verifique sua conexão.');
            });
    }
    
    // Adiciona formatação automática de CEP e eventos
    function adicionarFormatacaoCEP(prefixo) {
        const cepField = document.getElementById(prefixo + '-cep');
        const btnBuscar = document.getElementById('btn-buscar-cep-' + prefixo);
        
        if (cepField) {
            // Formatação em tempo real
            cepField.addEventListener('input', function(e) {
                let valor = e.target.value.replace(/\D/g, '');
                if (valor.length <= 8) {
                    if (valor.length > 5) {
                        valor = valor.replace(/^(\d{5})(\d{1,3})$/, '$1-$2');
                    }
                    e.target.value = valor;
                }
            });
            
            // Busca CEP quando o campo perde o foco
            cepField.addEventListener('blur', function(e) {
                const cep = e.target.value.replace(/\D/g, '');
                if (cep.length === 8) {
                    buscarCEP(cep, prefixo);
                }
            });
            
            // Busca CEP quando Enter é pressionado
            cepField.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const cep = e.target.value.replace(/\D/g, '');
                    if (cep.length === 8) {
                        buscarCEP(cep, prefixo);
                    }
                }
            });
        }
        
        // Adiciona evento ao botão de busca manual
        if (btnBuscar) {
            btnBuscar.addEventListener('click', function() {
                const cep = cepField.value.replace(/\D/g, '');
                if (cep.length === 8) {
                    buscarCEP(cep, prefixo);
                } else {
                    mostrarErro(prefixo, 'Digite um CEP válido com 8 dígitos.');
                }
            });
        }
    }
    
    // Inicializa para os modais de adicionar e editar
    adicionarFormatacaoCEP('add');
    adicionarFormatacaoCEP('edit');
    
    // Reinicializa quando os modais são abertos
    document.getElementById('adicionarFornecedorModal').addEventListener('shown.bs.modal', function() {
        adicionarFormatacaoCEP('add');
    });
    
    document.getElementById('editarFornecedorModal').addEventListener('shown.bs.modal', function() {
        adicionarFormatacaoCEP('edit');
    });
});
