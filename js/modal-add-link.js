  (() => {
    const refs = {
      openModalBtn: document.querySelector('[add-link-open]'),
      closeModalBtn: document.querySelector('[add-link-close]'),
      modal: document.querySelector('[add-link]'),
    };
  
    refs.openModalBtn.addEventListener('click', toggleModal);
    refs.closeModalBtn.addEventListener('click', toggleModal);
  
    function toggleModal() {
      refs.modal.classList.toggle('is-hidden');
    }
  })();