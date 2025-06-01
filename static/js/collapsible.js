export function setupCollapsibleMenus() {
    document.querySelectorAll('.collapsible').forEach(button => {
        const content = button.nextElementSibling;
        const chevron = button.querySelector('.bi');
        if (button.classList.contains('active')) {
            content.style.display = 'block';
            if (chevron) {
                chevron.classList.remove('bi-chevron-down');
                chevron.classList.add('bi-chevron-up');
            }
        }
        button.addEventListener('click', () => {
            button.classList.toggle('active');
            if (content.style.display === 'block') {
                content.style.display = 'none';
                if (chevron) {
                    chevron.classList.remove('bi-chevron-up');
                    chevron.classList.add('bi-chevron-down');
                }
            } else {
                content.style.display = 'block';
                if (chevron) {
                    chevron.classList.remove('bi-chevron-down');
                    chevron.classList.add('bi-chevron-up');
                }
            }
        });
    });
}