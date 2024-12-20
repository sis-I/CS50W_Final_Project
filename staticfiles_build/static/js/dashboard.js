document.addEventListener('DOMContentLoaded', () => {
    const sub_header = document.querySelector('.sub-header');
    scrollHorizontal(sub_header);

    window.onresize = () => {
        scrollHorizontal(sub_header);
    }

});


function scrollHorizontal(sub_header) {
    const x_scroll = sub_header.querySelector('.scroll-x');
    const scroll_btns = document.querySelectorAll('.scroll-btn');

    let is_first_elem = document.querySelector('.selected') === x_scroll.children[0];

    if (is_first_elem) localStorage.removeItem('scrollLeft');

    // Get stored scroll position and scroll horizontal when window reloads
    let scrollX = parseInt(localStorage.getItem('scrollLeft'));

    if (scrollX) {
        x_scroll.scrollTo({
            left: scrollX,
            behavior: "smooth",
        });

        localStorage.clear();
    }

    // Before the window loads, store scroll position
    window.onbeforeunload = function () {
        localStorage.setItem('scrollLeft', x_scroll.scrollLeft);
    }

    // Loop on right and left buttons
    scroll_btns.forEach(btn => {
        if ((sub_header.scrollWidth - x_scroll.scrollWidth) < 15 && btn.classList.contains('right')) {
            btn.style.visibility = 'visible';
        } else if (scrollX > 0 && btn.classList.contains('left')) {
            btn.style.visibility = 'visible';
        } else {
            btn.style.visibility = 'hidden';
        }

        // Scroll to the Left or Right
        btn.addEventListener('click', (e) => {
            const left = document.querySelector('.scroll-btn.left');
            const right = document.querySelector('.scroll-btn.right');

            // If clicked button is left
            if (btn.classList.contains('left')) {
                x_scroll.scrollBy(-75, 0);

                if (right.style.visibility !== 'visible') {
                    right.style.visibility = 'visible';
                }

                if (x_scroll.scrollLeft == 0) {
                    btn.style.visibility = 'hidden';
                }
            } else {// If clicked button is right
                x_scroll.scrollBy(75, 0);

                if (left.style.visibility !== 'visible') {
                    left.style.visibility = 'visible';
                }

                if ((x_scroll.scrollWidth - sub_header.scrollWidth) + 15 <= x_scroll.scrollLeft) {
                    btn.style.visibility = 'hidden';
                }
            }
        });

    });

}
