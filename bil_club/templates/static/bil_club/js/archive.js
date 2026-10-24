let currentState = {
    search: '',
    room: '',
    ordering: '-start_at'
};

let currentPage = 1;

let abortController = null;


document.addEventListener('DOMContentLoaded', function() {
    loadStateFromStorage();

    document.getElementById('search-input').value = currentState.search;
    document.getElementById('room-filter').value = currentState.room;
    document.getElementById('sort-select').value = currentState.ordering;

    setupEventListeners();

    loadArchiveData();
});


function saveStateToStorage() {
    localStorage.setItem('archive_search', currentState.search);
    localStorage.setItem('archive_ordering', currentState.ordering);
}

function loadStateFromStorage() {
    const savedSearch = localStorage.getItem('archive_search');
    const savedOrdering = localStorage.getItem('archive_ordering');

    if (savedSearch) currentState.search = savedSearch;
    if (savedOrdering) currentState.ordering = savedOrdering;
}


function setupEventListeners() {
    const searchInput = document.getElementById('search-input');
    const roomFilter = document.getElementById('room-filter');
    const sortSelect = document.getElementById('sort-select');

    let searchTimeout;
    searchInput.addEventListener('input', function(e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentState.search = e.target.value.trim();
            currentPage = 1;
            saveStateToStorage();
            loadArchiveData();
        }, 500);
    });

    roomFilter.addEventListener('change', function(e) {
        currentState.room = e.target.value;
        currentPage = 1;
        loadArchiveData();
    });

    sortSelect.addEventListener('change', function(e) {
        currentState.ordering = e.target.value;
        currentPage = 1;
        saveStateToStorage();
        loadArchiveData();
    });
}


async function loadArchiveData() {

    if (abortController) {
        abortController.abort();
    }
    abortController = new AbortController();

    showLoading();

    try {
        const params = new URLSearchParams({
            search: currentState.search,
            room: currentState.room,
            ordering: currentState.ordering,
            page: currentPage
        });

        const url = `/api/archive/sessions?${params.toString()}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: abortController.signal
        });

        if (!response.ok) {
            throw new Error(`HTTP ошибка: ${response.status}`);
        }

        const data = await response.json();

        if (data.game_sessions && data.game_sessions.length > 0) {
            renderTable(data.game_sessions);
            renderPagination(data.pagination);
            showTable();
        } else {
            showEmpty();
        }

    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Предыдущий запрос отменён');
        } else {
            console.error('Ошибка загрузки:', error);
            showError();
        }
    }
}


function renderTable(sessions) {
    const tbody = document.getElementById('archive-table-body');
    tbody.innerHTML = '';

    sessions.forEach(session => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';
        row.onclick = () => loadSessionDetails(session.id);

        row.innerHTML = `
            <td><strong>${session.client_name}</strong></td>
            <td>
                <div>${session.table_type}</div>
                <div class="text-muted small">${session.room_name}</div>
            </td>
            <td>${session.start_at}</td>
            <td>${session.duration_minutes} мин</td>
            <td><strong>${session.total_cost.toFixed(2)} ₽</strong></td>
        `;

        tbody.appendChild(row);
    });
}


async function loadSessionDetails(sessionId) {
    try {
        const response = await fetch(`/api/archive/sessions/${sessionId}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP ошибка: ${response.status}`);
        }

        const session = await response.json();
        renderDetailsCard(session);

    } catch (error) {
        console.error('Ошибка загрузки деталей:', error);
        alert('Не удалось загрузить детали игры');
    }
}

function renderDetailsCard(session) {
    const detailsHTML = `
        <div class="card-body">
            <h3 class="card-title mb-4">Детали игры</h3>

            <div class="mb-3">
                <div class="text-muted small">Клиент</div>
                <div class="fs-5"><strong>${session.client_name}</strong></div>
                <div class="text-muted">${session.client_phone}</div>
            </div>

            <div class="mb-3">
                <div class="text-muted small">Уровень навыков</div>
                <div class="fs-5">
                    <span class="badge bg-blue-lt">${session.client_skill}</span>
                </div>
            </div>

            <div class="mb-3">
                <div class="text-muted small">Зал / Стол</div>
                <div class="fs-5">${session.room_name} / ${session.table_type}</div>
            </div>

            <div class="mb-3">
                <div class="text-muted small">Цена за час</div>
                <div class="fs-5">${session.price_per_hour.toFixed(2)} ₽</div>
            </div>

            <div class="mb-3">
                <div class="text-muted small">Начало</div>
                <div class="fs-5">${session.start_at}</div>
            </div>

            <div class="mb-3">
                <div class="text-muted small">Окончание</div>
                <div class="fs-5">${session.end_at || '—'}</div>
            </div>

            <div class="mb-3">
                <div class="text-muted small">Длительность</div>
                <div class="fs-5">${session.duration_minutes} минут</div>
            </div>

            <div class="pt-3 border-top">
                <div class="text-muted small">Итого</div>
                <div class="fs-2 fw-bold text-green">${session.total_cost.toFixed(2)} ₽</div>
            </div>
        </div>
    `;

    document.getElementById('details-card').innerHTML = detailsHTML;
}


function renderPagination(pagination) {
    const controls = document.getElementById('pagination-controls');
    const info = document.getElementById('pagination-info');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    controls.classList.remove('d-none');
    info.textContent = `Страница ${pagination.current_page} из ${pagination.total_pages}`;

    btnPrev.disabled = !pagination.has_previous;
    btnNext.disabled = !pagination.has_next;
}

function changePage(direction) {
    currentPage += direction;
    loadArchiveData();
}


function showLoading() {
    document.getElementById('loading-spinner').classList.remove('d-none');
    document.getElementById('archive-table').classList.add('d-none');
    document.getElementById('error-state').classList.add('d-none');
    document.getElementById('empty-state').classList.add('d-none');
    document.getElementById('pagination-controls').classList.add('d-none');
}

function showTable() {
    document.getElementById('loading-spinner').classList.add('d-none');
    document.getElementById('archive-table').classList.remove('d-none');
    document.getElementById('error-state').classList.add('d-none');
    document.getElementById('empty-state').classList.add('d-none');
}

function showEmpty() {
    document.getElementById('loading-spinner').classList.add('d-none');
    document.getElementById('archive-table').classList.add('d-none');
    document.getElementById('error-state').classList.add('d-none');
    document.getElementById('empty-state').classList.remove('d-none');
    document.getElementById('pagination-controls').classList.add('d-none');
}

function showError() {
    document.getElementById('loading-spinner').classList.add('d-none');
    document.getElementById('archive-table').classList.add('d-none');
    document.getElementById('error-state').classList.remove('d-none');
    document.getElementById('empty-state').classList.add('d-none');
    document.getElementById('pagination-controls').classList.add('d-none');
}