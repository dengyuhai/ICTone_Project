// Scroll to top functionality
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show/hide scroll to top button
window.addEventListener('scroll', function() {
    const scrollButton = document.querySelector('.scroll-to-top');
    if (!scrollButton) {
        return;
    }

    if (window.pageYOffset > 300) {
        scrollButton.classList.add('visible');
    } else {
        scrollButton.classList.remove('visible');
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('[data-results-carousel]');
    if (!carousel) {
        return;
    }

    const viewport = carousel.querySelector('[data-results-viewport]');
    const track = carousel.querySelector('[data-results-track]');
    const slides = Array.from(carousel.querySelectorAll('.item'));
    const prevButton = document.querySelector('[data-results-prev]');
    const nextButton = document.querySelector('[data-results-next]');
    const dotsContainer = document.querySelector('[data-results-dots]');

    if (!viewport || !track || !slides.length || !prevButton || !nextButton || !dotsContainer) {
        return;
    }

    let currentIndex = 0;
    let touchStartX = 0;
    let touchDeltaX = 0;

    const dots = slides.map(function(_, index) {
        const dot = document.createElement('button');
        dot.type = 'button';
        dot.className = 'results-carousel-dot';
        dot.setAttribute('aria-label', `Go to result slide ${index + 1}`);
        dot.addEventListener('click', function() {
            renderSlide(index);
        });
        dotsContainer.appendChild(dot);
        return dot;
    });

    function renderSlide(index) {
        currentIndex = (index + slides.length) % slides.length;
        track.style.transform = `translateX(-${currentIndex * 100}%)`;

        slides.forEach(function(slide, slideIndex) {
            const isActive = slideIndex === currentIndex;
            slide.setAttribute('aria-hidden', String(!isActive));
        });

        dots.forEach(function(dot, dotIndex) {
            dot.classList.toggle('is-active', dotIndex === currentIndex);
            dot.setAttribute('aria-current', String(dotIndex === currentIndex));
        });
    }

    prevButton.addEventListener('click', function() {
        renderSlide(currentIndex - 1);
    });

    nextButton.addEventListener('click', function() {
        renderSlide(currentIndex + 1);
    });

    carousel.addEventListener('keydown', function(event) {
        if (event.key === 'ArrowLeft') {
            event.preventDefault();
            renderSlide(currentIndex - 1);
        }

        if (event.key === 'ArrowRight') {
            event.preventDefault();
            renderSlide(currentIndex + 1);
        }
    });

    viewport.addEventListener('touchstart', function(event) {
        touchStartX = event.touches[0].clientX;
        touchDeltaX = 0;
    }, { passive: true });

    viewport.addEventListener('touchmove', function(event) {
        touchDeltaX = event.touches[0].clientX - touchStartX;
    }, { passive: true });

    viewport.addEventListener('touchend', function() {
        if (Math.abs(touchDeltaX) > 50) {
            renderSlide(currentIndex + (touchDeltaX < 0 ? 1 : -1));
        }
    });

    renderSlide(0);
});
