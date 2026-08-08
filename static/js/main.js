document.addEventListener('DOMContentLoaded', () => {

    const recommendationForm = document.getElementById('recommendationForm');
    const recommendationsDiv = document.getElementById('recommendations');
    const catalogTitle = document.getElementById('catalogTitle');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const pageIndicator = document.getElementById('pageIndicator');

    // Estado global de paginación
    let currentPage = 1;
    const moviesPerPage = 12;
    let allCurrentMovies = [];

    // 1. Cargar el carrete e inicializar el catálogo
    loadFeaturedStrip();
    loadCatalog();

    // Eventos
    if (recommendationForm) {
        recommendationForm.addEventListener('submit', event => {
            event.preventDefault();
            searchMovies();
        });
    }

    if (prevPageBtn) {
        prevPageBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderPaginatedCatalog();
            }
        });
    }

    if (nextPageBtn) {
        nextPageBtn.addEventListener('click', () => {
            if ((currentPage * moviesPerPage) < allCurrentMovies.length) {
                currentPage++;
                renderPaginatedCatalog();
            }
        });
    }

    // Carrete horizontal
    async function loadFeaturedStrip(excludeIds = []) {
        try {
            const excludeParam = excludeIds.length > 0 ? `?exclude=${excludeIds.join(',')}` : '';
            const response = await fetch(`/featured${excludeParam}`);

            if (!response.ok) throw new Error("Error fetching featured movies");

            const featuredMovies = await response.json();
            renderFilmStrip(featuredMovies);
        } catch (error) {
            console.error("Error al cargar el carrete dinámico:", error);
        }
    }

    function renderFilmStrip(movies) {
        const filmTrack = document.getElementById('filmStripTrack');
        if (!filmTrack || !movies || movies.length === 0) return;

        filmTrack.innerHTML = "";

        const duplicatedMovies = [...movies, ...movies];

        duplicatedMovies.forEach(movie => {
            const posterUrl = movie.poster_path 
                ? `https://image.tmdb.org/t/p/w185${movie.poster_path}` 
                : '/static/images/default-movie-poster.jpg';

            const frame = document.createElement('div');
            frame.className = 'film-frame';
            frame.innerHTML = `<img src="${posterUrl}" alt="${movie.title}" loading="lazy" decoding="async">`;
            
            frame.addEventListener('click', () => fetchMovieDetails(movie.id));
            filmTrack.appendChild(frame);
        });
    }

    // Carga de películas
    async function loadCatalog() {
        setTitle('<i class="fas fa-film"></i> Featured Movies');
        showLoading("Loading movie catalog...");

        try {
            const response = await fetch('/catalog');
            const movies = await response.json();
            displayRecommendations(movies);
        } catch (error) {
            showError();
            console.error("Error cargando el catálogo:", error);
        }
    }

    async function searchMovies() {
        const titleInput = document.getElementById('movieTitle');
        const genreInput = document.getElementById('genre');
        const minRatingInput = document.getElementById('minRating');
        const amountInput = document.getElementById('numRecommendations');

        const title = titleInput ? titleInput.value.trim() : '';
        const genre = genreInput ? genreInput.value : '';
        const minRating = minRatingInput ? minRatingInput.value : '';
        const amount = (amountInput && amountInput.value) ? amountInput.value : 10;

        if (title === "") {
            loadCatalog();
            return;
        }

        const params = new URLSearchParams({
            title,
            n: amount,
            ...(genre && { genre }),
            ...(minRating && { min_rating: minRating })
        });

        setTitle('<i class="fas fa-search"></i> Search Results');
        fetchRecommendations(`/recommendations?${params}`);
    }

    async function fetchRecommendations(url) {
        showLoading("Finding recommendations...");

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Error en la respuesta del servidor");
            const movies = await response.json();
            displayRecommendations(movies);
        } catch (error) {
            showError();
            console.error("Error buscando películas:", error);
        }
    }

    function displayRecommendations(movies) {
        allCurrentMovies = movies || [];
        currentPage = 1;

        if (allCurrentMovies.length > 0) {
            const currentCatalogIds = allCurrentMovies.map(m => m.id);
            loadFeaturedStrip(currentCatalogIds);
        }

        renderPaginatedCatalog();
    }

    function renderPaginatedCatalog() {
        if (!recommendationsDiv) return;
        recommendationsDiv.innerHTML = "";

        if (!allCurrentMovies || allCurrentMovies.length === 0) {
            recommendationsDiv.innerHTML = `
            <div class="no-results-container">
                <i class="fas fa-film fa-4x"></i>
                <h3>No Movies Found</h3>
                <p>Try another title or adjust filters.</p>
            </div>`;
            if (pageIndicator) pageIndicator.innerText = "Página 0 de 0";
            if (prevPageBtn) prevPageBtn.disabled = true;
            if (nextPageBtn) nextPageBtn.disabled = true;
            return;
        }

        const startIndex = (currentPage - 1) * moviesPerPage;
        const endIndex = startIndex + moviesPerPage;
        const pageMovies = allCurrentMovies.slice(startIndex, endIndex);

        const fragment = document.createDocumentFragment();
        pageMovies.forEach(movie => {
            fragment.appendChild(createMovieCard(movie));
        });

        recommendationsDiv.appendChild(fragment);
        addMoreInfoEventListeners();

        // Actualizar UI de paginación
        const totalPages = Math.ceil(allCurrentMovies.length / moviesPerPage) || 1;
        if (pageIndicator) pageIndicator.innerText = `Página ${currentPage} de ${totalPages}`;
        if (prevPageBtn) prevPageBtn.disabled = (currentPage === 1);
        if (nextPageBtn) nextPageBtn.disabled = (currentPage >= totalPages);
    }

    function createMovieCard(movie) {
        const card = document.createElement('div');

        const watchedMovies = JSON.parse(localStorage.getItem('watchedMovies')) || [];
        const isWatched = watchedMovies.includes(movie.id);

        card.className = `movie-card ${isWatched ? 'watched' : ''}`;
        const rating = movie.rating ?? movie.vote_average ?? 0;

        card.innerHTML = `
        <div class="movie-poster" style="background-image:url('${movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/static/images/default-movie-poster.jpg'}')">
        </div>
        <div class="movie-info">
            <h3>${movie.title}</h3>
            <p class="rating"><i class="fas fa-star"></i> ${Number(rating).toFixed(1)}</p>
            
            <button class="more-info-btn" data-id="${movie.id}">More Info</button>
            <button class="watch-btn ${isWatched ? 'active' : ''}" onclick="toggleWatched(${movie.id}, this)">
                <i class="fas ${isWatched ? 'fa-check-circle' : 'fa-eye'}"></i> ${isWatched ? 'Watched' : 'Mark Watched'}
            </button>
        </div>
        `;

        return card;
    }

    window.toggleWatched = function (movieId, btn) {
        let watchedMovies = JSON.parse(localStorage.getItem('watchedMovies')) || [];
        const card = btn.closest('.movie-card');

        if (watchedMovies.includes(movieId)) {
            watchedMovies = watchedMovies.filter(id => id !== movieId);
            if (card) card.classList.remove('watched');
            btn.classList.remove('active');
            btn.innerHTML = `<i class="fas fa-eye"></i> Mark Watched`;
        } else {
            watchedMovies.push(movieId);
            if (card) card.classList.add('watched');
            btn.classList.add('active');
            btn.innerHTML = `<i class="fas fa-check-circle"></i> Watched`;
        }

        localStorage.setItem('watchedMovies', JSON.stringify(watchedMovies));
    };

    function addMoreInfoEventListeners() {
        document.querySelectorAll('.more-info-btn').forEach(button => {
            button.addEventListener('click', () => {
                fetchMovieDetails(button.dataset.id);
            });
        });
    }

    async function fetchMovieDetails(id) {
        try {
            const response = await fetch(`/movie/${id}`);
            const movie = await response.json();
            showMovieModal(movie);
        } catch (error) {
            console.error("Error al obtener detalles:", error);
        }
    }

    function showMovieModal(movie) {
        const modal = document.createElement('div');
        modal.className = "movie-modal";

        modal.innerHTML = `
        <div class="modal-content" style="background:#1c1c1c; padding:30px; border-radius:20px; border:1px solid #d4af37; color:white; max-width:600px; width:90%; position:relative; margin: auto; margin-top: 10vh;">
            <span class="close-modal" style="position:absolute; top:20px; right:25px; font-size:30px; cursor:pointer; color:#d4af37;">&times;</span>
            <img src="${movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : '/static/images/default-movie-poster.jpg'}" style="width:100%; max-height:400px; object-fit:cover; border-radius:12px; margin-bottom:20px;">
            <div class="modal-info">
                <h2 style="color:#d4af37; margin-bottom:15px; font-size: 1.8rem;">${movie.title}</h2>
                <p style="margin-bottom:8px;"><strong>⭐ Rating:</strong> ${movie.vote_average ?? "N/A"}</p>
                <p style="color:#ccc; line-height:1.6;">${movie.overview ?? "No description available."}</p>
            </div>
        </div>
        `;

        modal.style.position = "fixed";
        modal.style.top = "0";
        modal.style.left = "0";
        modal.style.width = "100%";
        modal.style.height = "100%";
        modal.style.background = "rgba(0,0,0,0.8)";
        modal.style.zIndex = "1000";
        modal.style.overflow = "auto";

        document.body.appendChild(modal);

        modal.querySelector('.close-modal').onclick = () => modal.remove();
        modal.onclick = e => {
            if (e.target === modal) modal.remove();
        };
    }

    function setTitle(text) {
        if (catalogTitle) catalogTitle.innerHTML = text;
    }

    function showLoading(text) {
        if (!recommendationsDiv) return;
        recommendationsDiv.innerHTML = `
        <div class="loading" style="text-align:center; padding: 50px; width: 100%; grid-column: 1 / -1;">
            <i class="fas fa-film fa-spin fa-3x" style="color: #d4af37; margin-bottom: 15px;"></i>
            <h3 style="color: #ccc;">${text}</h3>
        </div>
        `;
    }

    function showError() {
        if (!recommendationsDiv) return;
        recommendationsDiv.innerHTML = `
        <div class="error" style="text-align:center; padding: 50px; width: 100%; grid-column: 1 / -1; color: #ff6b6b;">
            <i class="fas fa-exclamation-triangle fa-3x" style="margin-bottom: 15px;"></i>
            <h3>Something went wrong.</h3>
        </div>
        `;
    }
});