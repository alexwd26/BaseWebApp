document.addEventListener('DOMContentLoaded', function() {
    const bannerContainer = document.querySelector('.banner-container');
    const promotionalTitle = document.querySelector('.promotional-title');
    const promotionalText = document.querySelector('.promotional-text');
    // const promoImage = document.querySelector('.promo-image img'); // No longer directly used
    let promotions = [];
    let currentIndex = 0;
    const ROTATION_INTERVAL = 5000;
    const CACHE_KEY = 'promotionsData';
    const CACHE_EXPIRATION_TIME = 300000;

    async function fetchPromotions() {
        try {
            bannerContainer.classList.add('loading');

            const cachedData = localStorage.getItem(CACHE_KEY);
            const cachedTime = localStorage.getItem(`${CACHE_KEY}_timestamp`);

            if (cachedData && cachedTime && (Date.now() - parseInt(cachedTime, 10)) < CACHE_EXPIRATION_TIME) {
                promotions = JSON.parse(cachedData).filter(promo => promo.active);
                showCurrentPromotion();
                bannerContainer.classList.remove('loading');
                bannerContainer.classList.remove('error');
                fetchFreshPromotions();
                return;
            }

            await fetchFreshPromotions();

        } catch (error) {
            console.error('Error fetching promotions:', error);
            bannerContainer.classList.remove('loading');
            bannerContainer.classList.add('error');
            promotionalTitle.textContent = '';
            promotionalText.textContent = 'Ofertas Especiais 🔥';
            // if (promoImage) promoImage.style.display = 'none'; // No longer needed
            promotions = [];
        }
    }

    async function fetchFreshPromotions() {
        try {
            const response = await fetch('http://15.228.148.198:8000/api/promos/promocoes');

            if (!response.ok) {
                throw new Error('Failed to fetch promotions');
            }

            const data = await response.json();

            if (data && data.length > 0) {
                promotions = data.filter(promo => promo.active);
                showCurrentPromotion();
                localStorage.setItem(CACHE_KEY, JSON.stringify(promotions));
                localStorage.setItem(`${CACHE_KEY}_timestamp`, Date.now());
            }

            bannerContainer.classList.remove('loading');
            bannerContainer.classList.remove('error');
        } catch (error) {
            console.error('Error fetching fresh promotions for cache:', error);
            if (promotions.length === 0) {
                bannerContainer.classList.remove('loading');
                bannerContainer.classList.add('error');
                promotionalTitle.textContent = '';
                promotionalText.textContent = 'Ofertas Especiais 🔥';
                // if (promoImage) promoImage.style.display = 'none'; // No longer needed
            }
        }
    }

    function showCurrentPromotion() {
        if (promotions.length === 0) {
            promotionalTitle.textContent = '';
            promotionalText.textContent = 'Ofertas Especiais 🔥';
            bannerContainer.style.backgroundImage = ''; // Clear background image
            return;
        }

        const currentPromo = promotions[currentIndex];

        promotionalTitle.classList.add('fade-out');
        promotionalText.classList.add('fade-out');
        bannerContainer.classList.add('fade-out'); // Fade out the whole container for smoother background change

        setTimeout(() => {
            promotionalTitle.textContent = currentPromo.title || '';
            promotionalText.textContent = currentPromo.description || 'Ofertas Especiais 🔥';

            if (currentPromo.image && currentPromo.image !== 'string') {
                bannerContainer.style.backgroundImage = `url('http://15.228.148.198:8000/api/images/images/${currentPromo.image}')`;
            } else {
                bannerContainer.style.backgroundImage = ''; // Clear background if no image
            }

            promotionalTitle.classList.remove('fade-out');
            promotionalTitle.classList.add('fade-in');
            promotionalText.classList.remove('fade-out');
            promotionalText.classList.add('fade-in');
            bannerContainer.classList.remove('fade-out');
            bannerContainer.classList.add('fade-in');
        }, 500);
    }

    function rotatePromotions() {
        if (promotions.length <= 1) return;

        currentIndex = (currentIndex + 1) % promotions.length;
        showCurrentPromotion();
    }

    // if (promoImage) { // No longer needed
    //     promoImage.addEventListener('error', () => {
    //         promoImage.style.display = 'none';
    //     });
    // }

    fetchPromotions();
    setInterval(rotatePromotions, ROTATION_INTERVAL);
    setInterval(fetchFreshPromotions, 300000);
});