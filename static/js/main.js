/* ============================================
   EAGLE - Sistema de Gestão Fiscal
   JavaScript Principal
   ============================================ */

// Elementos globais
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const toggleBtn = document.getElementById('toggleSidebar');
const toggleIcon = document.getElementById('toggleIcon');
const mobileOverlay = document.getElementById('mobileOverlay');

let isCollapsed = false;
let isMobile = window.innerWidth <= 768;

/* ============================================
   SIDEBAR TOGGLE
   ============================================ */
function toggleSidebar() {
    if (isMobile) {
        sidebar.classList.toggle('show');
        mobileOverlay.classList.toggle('show');
    } else {
        isCollapsed = !isCollapsed;
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
        toggleIcon.className = isCollapsed ? 'bi bi-chevron-right' : 'bi bi-chevron-left';
        
        // Fecha todos os dropdowns quando colapsa
        if (isCollapsed) {
            document.querySelectorAll('.submenu.show').forEach(submenu => {
                submenu.classList.remove('show');
            });
            document.querySelectorAll('.menu-arrow.rotated').forEach(arrow => {
                arrow.classList.remove('rotated');
            });
        }
    }
}

if (toggleBtn) {
    toggleBtn.addEventListener('click', toggleSidebar);
}

if (mobileOverlay) {
    mobileOverlay.addEventListener('click', toggleSidebar);
}

/* ============================================
   DROPDOWN MENU
   ============================================ */
document.querySelectorAll('[data-toggle]').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (isCollapsed && !isMobile) return;
        
        const target = this.getAttribute('data-toggle');
        const submenu = document.getElementById(target + '-submenu');
        const arrow = this.querySelector('.menu-arrow');
        
        // Fecha outros dropdowns
        document.querySelectorAll('.submenu.show').forEach(otherSubmenu => {
            if (otherSubmenu !== submenu) {
                otherSubmenu.classList.remove('show');
            }
        });
        
        document.querySelectorAll('.menu-arrow.rotated').forEach(otherArrow => {
            if (otherArrow !== arrow) {
                otherArrow.classList.remove('rotated');
            }
        });
        
        // Toggle do dropdown atual
        submenu.classList.toggle('show');
        if (arrow) {
            arrow.classList.toggle('rotated');
        }
        
        // Define estado ativo
        document.querySelectorAll('.menu-link.active').forEach(activeLink => {
            if (activeLink.hasAttribute('data-toggle')) {
                activeLink.classList.remove('active');
            }
        });
        this.classList.add('active');
    });
});

/* ============================================
   USER MENU
   ============================================ */
const userProfile = document.getElementById('userProfile');
const userMenu = document.getElementById('userMenu');

if (userProfile && userMenu) {
    userProfile.addEventListener('click', function(e) {
        e.stopPropagation();
        userMenu.classList.toggle('show');
    });

    // Fecha menu de usuário ao clicar fora
    document.addEventListener('click', function() {
        userMenu.classList.remove('show');
    });
}

/* ============================================
   PASSWORD TOGGLE
   ============================================ */
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById(fieldId + '_icon');
    
    if (field && icon) {
        if (field.type === 'password') {
            field.type = 'text';
            icon.className = 'bi bi-eye-slash';
        } else {
            field.type = 'password';
            icon.className = 'bi bi-eye';
        }
    }
}

/* ============================================
   FORM VALIDATION - PROFILE
   ============================================ */
const profileForm = document.getElementById('profileForm');
if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
        const newPassword = document.getElementById('new_password')?.value;
        const confirmPassword = document.getElementById('confirm_password')?.value;
        
        // Valida senha apenas se o usuário está tentando alterá-la
        if (newPassword || confirmPassword) {
            if (newPassword !== confirmPassword) {
                e.preventDefault();
                alert('A nova senha e a confirmação não coincidem.');
                return;
            }
            
            if (newPassword.length < 4) {
                e.preventDefault();
                alert('A nova senha deve ter pelo menos 4 caracteres.');
                return;
            }
        }
    });
}

/* ============================================
   WINDOW RESIZE
   ============================================ */
window.addEventListener('resize', function() {
    const wasMobile = isMobile;
    isMobile = window.innerWidth <= 768;
    
    if (wasMobile && !isMobile) {
        // Mudando de mobile para desktop
        sidebar.classList.remove('show');
        mobileOverlay.classList.remove('show');
    } else if (!wasMobile && isMobile) {
        // Mudando de desktop para mobile
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
        isCollapsed = false;
        if (toggleIcon) {
            toggleIcon.className = 'bi bi-chevron-left';
        }
    }
});

/* ============================================
   CSRF TOKEN
   ============================================ */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/* ============================================
   TOAST NOTIFICATIONS
   ============================================ */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast show align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi bi-${getToastIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-hide após 5 segundos
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/* ============================================
   INICIALIZAÇÃO
   ============================================ */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide toasts existentes
    document.querySelectorAll('.toast.show').forEach(toast => {
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    });
    
    // Abre submenu do item ativo
    const currentPath = window.location.pathname;
    document.querySelectorAll('.submenu-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            const submenu = link.closest('.submenu');
            if (submenu) {
                submenu.classList.add('show');
                const menuLink = submenu.previousElementSibling;
                if (menuLink) {
                    menuLink.classList.add('active');
                    const arrow = menuLink.querySelector('.menu-arrow');
                    if (arrow) {
                        arrow.classList.add('rotated');
                    }
                }
            }
        }
    });
});

/* ============================================
   UTILITÁRIOS
   ============================================ */
// Formatar CNPJ
function formatCNPJ(cnpj) {
    cnpj = cnpj.replace(/\D/g, '');
    return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
}

// Formatar CPF
function formatCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    return cpf.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4');
}

// Formatar moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Formatar data
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}
