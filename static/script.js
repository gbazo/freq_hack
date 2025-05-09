// Validação de entrada para aceitar apenas números
document.addEventListener('DOMContentLoaded', function() {
    const codigoInput = document.getElementById('codigo');
    
    if (codigoInput) {
        codigoInput.addEventListener('input', function(e) {
            // Remover caracteres não numéricos
            this.value = this.value.replace(/[^0-9]/g, '');
        });
        
        // Focar automaticamente no campo de entrada
        codigoInput.focus();
    }
});