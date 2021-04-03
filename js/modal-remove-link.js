  (() => {
    const refs = {
      openModalBtn: document.querySelector('[remove-link-open]'),
      closeModalBtn: document.querySelector('[remove-link-close]'),
      modal: document.querySelector('[remove-link]'),
    };
  
    refs.openModalBtn.addEventListener('click', toggleModal);
    refs.closeModalBtn.addEventListener('click', toggleModal);
  
    function toggleModal() {
      refs.modal.classList.toggle('is-hidden');
    }
  })();