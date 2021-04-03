  (() => {
    const refs = {
      openModalBtn: document.querySelector('[change-link-open]'),
      closeModalBtn: document.querySelector('[change-link-close]'),
      modal: document.querySelector('[change-link]'),
    };
  
    refs.openModalBtn.addEventListener('click', toggleModal);
    refs.closeModalBtn.addEventListener('click', toggleModal);
  
    function toggleModal() {
      refs.modal.classList.toggle('is-hidden');
    }
  })();