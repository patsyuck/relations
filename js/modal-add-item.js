  (() => {
    const refs = {
      openModalBtn: document.querySelector('[add-item-open]'),
      closeModalBtn: document.querySelector('[add-item-close]'),
      modal: document.querySelector('[add-item]'),
    };
  
    refs.openModalBtn.addEventListener('click', toggleModal);
    refs.closeModalBtn.addEventListener('click', toggleModal);
  
    function toggleModal() {
      refs.modal.classList.toggle('is-hidden');
    }
  })();