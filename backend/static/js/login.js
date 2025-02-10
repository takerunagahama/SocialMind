document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');

    loginForm.addEventListener('submit', function(e) {
        let isValid = true;

        if (!usernameInput.value.trim()) {
            showError(usernameInput, 'ユーザー名を入力してください');
            isValid = false;
        } else {
            clearError(usernameInput);
        }

        if (!passwordInput.value.trim()) {
            showError(passwordInput, 'パスワードを入力してください');
            isValid = false;
        } else {
            clearError(passwordInput);
        }

        if (!isValid) {
            e.preventDefault();
        }
    });

    function showError(input, message) {
        const formGroup = input.closest('.form-group');
        let errorElement = formGroup.querySelector('.error');
        
        if (!errorElement) {
            errorElement = document.createElement('p');
            errorElement.className = 'error';
            formGroup.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        input.classList.add('input-error');
    }

    function clearError(input) {
        const formGroup = input.closest('.form-group');
        const errorElement = formGroup.querySelector('.error');
        
        if (errorElement) {
            errorElement.remove();
        }
        
        input.classList.remove('input-error');
    }
});