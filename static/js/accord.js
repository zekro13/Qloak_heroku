document.querySelectorAll('#accordian_button').forEach(button => {
    button.addEventListener('click', () => {
        const accodionContent = button.nextElementSibling;

        button.classList.toggle('accordian_button--active');

        if (button.classList.contains('accordian__button--active')) {
            accordionContent.style.maxHeight = accodionContent.scrollHeight + 'px';
        } else {
            accordionContent.style.maxHeight = 0;
        }
    });
}) ;