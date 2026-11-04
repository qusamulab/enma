
document.querySelectorAll('.section-header').forEach(h => {
  h.addEventListener('click', () => {
    h.nextElementSibling.classList.toggle('open');
  });
});
document.querySelectorAll('.section-body[data-open="1"]').forEach(b => b.classList.add('open'));
