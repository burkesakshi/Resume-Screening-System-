/**
 * ✅ PROFESSIONAL VALIDATION for Resume Screening Form
 * Matches your Flask app.py validation EXACTLY
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔥 Resume Screening Validation Loaded!');
    
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const strengthBar = document.getElementById('strengthBar');
    
    if (!form) {
        console.warn('❌ Form not found!');
        return;
    }
    
    const inputs = form.querySelectorAll('input[required]');
    
    // 🔄 Real-time validation on ALL inputs
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', debounce(validateField, 400));
    });
    
    // 🔐 Password strength meter
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', updatePasswordStrength);
    }
    
    // 📤 Form submission validation
    form.addEventListener('submit', function(e) {
        if (!isFormValid()) {
            e.preventDefault();
            showTempAlert('⚠️ Please fix all errors above!', 'error');
            return false;
        }
    });
    
    // 🎨 Initial state
    updateSubmitButton();
    
    // ================================
    // 🧹 VALIDATION FUNCTIONS
    // ================================
    
    function validateField(event) {
        const field = event.target;
        const value = field.value.trim();
        const fieldGroup = field.closest('.form-group');
        const helpText = fieldGroup?.querySelector('small');
        
        // Reset previous states
        field.classList.remove('valid', 'invalid');
        if (fieldGroup) fieldGroup.classList.remove('invalid');
        
        let isValid = true;
        let errorMsg = '';
        
        // 📝 Field-specific validation (MATCHES YOUR PYTHON validate_registration)
        switch(field.id) {
            case 'name':
                if (value.length < 2 || value.length > 50) {
                    isValid = false;
                    errorMsg = '2-50 characters required';
                } else if (!/^[a-zA-Z\s]+$/.test(value)) {
                    isValid = false;
                    errorMsg = 'Letters and spaces only';
                }
                break;
                
            case 'email':
                const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                isValid = emailRegex.test(value);
                errorMsg = 'Valid email format required';
                break;
                
            case 'phone':
                const phoneDigits = value.replace(/\D/g, '');
                isValid = phoneDigits.length === 10;
                errorMsg = 'Exactly 10 digits required';
                break;
                
            case 'age':
                const age = parseInt(value);
                isValid = age >= 18 && age <= 65 && !isNaN(age);
                errorMsg = 'Must be 18-65 years';
                break;
                
            case 'education':
                isValid = value.length >= 2 && value.length <= 100;
                errorMsg = '2-100 characters required';
                break;
                
            case 'password':
                const hasUpper = /[A-Z]/.test(value);
                const hasDigit = /\d/.test(value);
                const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
                isValid = value.length >= 8 && hasUpper && hasDigit && hasSpecial;
                errorMsg = '8+ chars: 1 Upper, 1 Number, 1 Special';
                break;
        }
        
        // 🎨 Visual feedback
        if (isValid) {
            field.classList.add('valid');
            if (helpText) helpText.style.color = '#666';
        } else {
            field.classList.add('invalid');
            if (fieldGroup) fieldGroup.classList.add('invalid');
            if (helpText) {
                helpText.textContent = errorMsg;
                helpText.style.color = '#e74c3c';
            }
        }
        
        updateSubmitButton();
    }
    
    // 🔐 Password strength visualization
    function updatePasswordStrength(event) {
        const value = event.target.value;
        let score = 0;
        
        if (value.length >= 8) score++;
        if (/[A-Z]/.test(value)) score++;
        if (/\d/.test(value)) score++;
        if (/[^A-Za-z0-9]/.test(value)) score++;
        
        // Update strength bar
        let fill = strengthBar.querySelector('.strength-fill');
        if (!fill) {
            fill = document.createElement('div');
            fill.className = 'strength-fill';
            strengthBar.appendChild(fill);
        }
        
        fill.className = 'strength-fill';
        if (score <= 1) {
            fill.classList.add('strength-weak');
            fill.style.width = '33%';
        } else if (score <= 2) {
            fill.classList.add('strength-fair');
            fill.style.width = '66%';
        } else {
            fill.classList.add('strength-strong');
            fill.style.width = '100%';
        }
    }
    
    // ✅ Form validity check
    function isFormValid() {
        return Array.from(inputs).every(input => {
            const value = input.value.trim();
            return input.classList.contains('valid') || 
                   (value && !input.classList.contains('invalid'));
        });
    }
    
    // 🔘 Submit button control
    function updateSubmitButton() {
        const valid = isFormValid();
        submitBtn.disabled = !valid;
        submitBtn.style.opacity = valid ? '1' : '0.6';
        submitBtn.style.cursor = valid ? 'pointer' : 'not-allowed';
    }
    
    // ⏱️ Debounce for performance
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    // 🔔 Temporary alerts
    function showTempAlert(message, type = 'info') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i> ${message}`;
        alert.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 9999;
            padding: 15px 20px; border-radius: 10px; max-width: 350px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-weight: 500;
        `;
        document.body.appendChild(alert);
        
        setTimeout(() => {
            alert.style.transition = 'all 0.3s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(100%)';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    }
});

// 🌈 Auto-inject CSS for validation states
(function() {
    const css = `
        /* VALIDATION STYLES */
        input.valid {
            border-color: #27ae60 !important;
            background: linear-gradient(90deg, #f0fff4 0%, #e8f5e8 100%) !important;
            box-shadow: 0 0 0 3px rgba(39, 174, 96, 0.1) !important;
        }
        input.invalid {
            border-color: #e74c3c !important;
            background: linear-gradient(90deg, #fdf2f2 0%, #fce8e8 100%) !important;
            box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1) !important;
        }
        .form-group.invalid label {
            color: #e74c3c !important;
        }
        .form-group.invalid small {
            color: #e74c3c !important;
        }
        small {
            color: #666;
            font-size: 0.85rem;
            margin-top: 5px;
            display: block;
            transition: color 0.3s;
        }
        .password-strength {
            height: 6px;
            background: #e1e8ed;
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }
        .strength-fill {
            height: 100%;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .strength-weak { background: linear-gradient(90deg, #e74c3c, #c0392b); }
        .strength-fair { background: linear-gradient(90deg, #f39c12, #e67e22); }
        .strength-strong { background: linear-gradient(90deg, #27ae60, #229954); }
        
        /* Submit button states */
        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        .submit-btn:not(:disabled):hover {
            transform: translateY(-2px);
        }
        
        /* Responsive */
        @media (max-width: 480px) {
            .container { margin: 10px; border-radius: 15px; }
        }
    `;
    
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
})();