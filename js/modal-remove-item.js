  (() => {
    const refs = {
      openModalBtn: document.querySelector('[remove-item-open]'),
      closeModalBtn: document.querySelector('[remove-item-close]'),
      modal: document.querySelector('[remove-item]'),
    };
  
    refs.openModalBtn.addEventListener('click', toggleModal);
    refs.closeModalBtn.addEventListener('click', toggleModal);
  
    function toggleModal() {
      refs.modal.classList.toggle('is-hidden');
    }
  })();