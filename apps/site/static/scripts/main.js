var SELECTOR = '[data="scroll-button"]'

function scrollToItem(item) {
    var diff=(item.offsetTop-window.scrollY)/8
    if (Math.abs(diff)>1) {
        window.scrollTo(0, (window.scrollY+diff))
        clearTimeout(window._TO)
        window._TO=setTimeout(scrollToItem, 30, item)
    } else {
        window.scrollTo(0, item.offsetTop)
    }
}

function addButtonAction() {
  var button = document.querySelector(SELECTOR);
  button.addEventListener('click', function(zdarzenie) {
    zdarzenie.preventDefault();
    scrollToItem(document.getElementById('faq-section'));
  });
}

addButtonAction();
