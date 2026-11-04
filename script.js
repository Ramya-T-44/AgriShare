document.addEventListener('DOMContentLoaded', function () {
    // ========== USER DROPDOWN MENU ==========
    const dropdownBtn = document.getElementById('userDropdownBtn');
    const dropdownMenu = document.getElementById('userDropdownMenu');
    const dropdown = dropdownBtn ? dropdownBtn.closest('.dropdown') : null;

    if (dropdownBtn && dropdownMenu && dropdown) {
        dropdownBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            dropdown.classList.toggle('open');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('open');
            }
        });

        // Close dropdown with Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                dropdown.classList.remove('open');
            }
        });

        // Close dropdown when an item is clicked
        dropdownMenu.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', function () {
                dropdown.classList.remove('open');
            });
        });
    }

    // ========== BOOKING MODAL ==========
    const modal = document.getElementById('bookingModal');
    const closeModalBtn = document.getElementById('closeModal');
    const cancelModalBtn = document.getElementById('cancelModal');
    const bookButtons = document.querySelectorAll('.btn-book');

    if (modal) {
        // 1. Open Modal when clicking "Book Equipment"
        bookButtons.forEach(button => {
            button.addEventListener('click', function () {
                const equipmentId = this.getAttribute('data-id');
                const title = this.getAttribute('data-title');
                const rate = this.getAttribute('data-rate');

                // Populate Modal Form Fields
                document.getElementById('modalEquipmentId').value = equipmentId;
                document.getElementById('modalEquipmentTitle').textContent = 'Book ' + title;
                document.getElementById('modalRateDisplay').textContent = rate;

                // Show Modal Overlay with animation
                modal.style.display = 'flex';
                document.body.style.overflow = 'hidden'; // prevent background scroll
            });
        });

        // 2. Close Modal Function
        function hideModal() {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }

        // Close listeners
        if (closeModalBtn) closeModalBtn.addEventListener('click', hideModal);
        if (cancelModalBtn) cancelModalBtn.addEventListener('click', hideModal);

        // Close when clicking outside the modal box
        window.addEventListener('click', function (event) {
            if (event.target === modal) {
                hideModal();
            }
        });

        // Close modal with Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && modal.style.display === 'flex') {
                hideModal();
            }
        });
    }

    // ========== DELETE CONFIRMATION ==========
    window.confirmDelete = function (title) {
        return confirm(`Are you sure you want to remove "${title}" from the marketplace?`);
    };

    // ========== SMOOTH SCROLL FOR NAV LINKS ==========
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});

