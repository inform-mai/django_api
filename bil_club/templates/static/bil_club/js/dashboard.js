function startGame(tableId) {
    const clientId = prompt("Введите ID клиента для начала игры (UUID):");

    if (!clientId) {
        alert("Начало игры отменено: клиент не выбран.");
        return;
    }

    fetch(`/api/sessions/start/${tableId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken
        },
        body: `client_id=${clientId}`
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.start_success) {
            alert("Игра успешно начата!\nКлиент: " + data.client_name);

            var card = document.getElementById("table-card-" + tableId);
            if (card) {
                card.querySelector('.card-body').innerHTML = `
                    <div class="d-flex align-items-center">
                        <div class="subheader">Стол</div>
                        <div class="ms-auto">
                            <span class="badge bg-red-lt">Занят</span>
                        </div>
                    </div>
                    <div class="h1 mb-3">Игра идет...</div>
                    <div class="text-muted mb-2">Клиент: ${data.client_name}</div>
                    <button class="btn btn-outline-secondary w-100 mt-2" disabled>Игра идёт...</button>
                `;
            }
        } else {
            alert("Ошибка: " + data.detail);
        }
    })
    .catch(function(error) {
        console.error('Ошибка при начале игры:', error);
        alert("Произошла сетевая ошибка. Проверьте консоль разработчика (F12).");
    });
}


function freezeTable(tableId) {
    var reason = prompt("Причина недоступности:");
    if (!reason) {
        alert("Отменено: причина не указана.");
        return;
    }

    var until = prompt("Недоступен до (формат: 2026-10-22 18:00:00):");
    if (!until) {
        alert("Отменено: дата не указана.");
        return;
    }

    fetch("/api/tables/" + tableId + "/status/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrftoken
        },
        body: "change_to=frozen&unavailable_reason=" + encodeURIComponent(reason) + "&unavailable_until=" + encodeURIComponent(until)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.success_update) {
            alert("Стол переведён на обслуживание!\nПричина: " + reason + "\nДо: " + until);

            var card = document.getElementById("table-card-" + tableId);
            if (card) {
                card.querySelector('.card-body').innerHTML = `
                    <div class="d-flex align-items-center">
                        <div class="subheader">Стол</div>
                        <div class="ms-auto">
                            <span class="badge bg-yellow-lt">На обслуживании</span>
                        </div>
                    </div>
                    <div class="h1 mb-3">🔧 Обслуживание</div>
                    <div class="text-muted small mb-2">Причина: ${reason}</div>
                    <div class="text-muted small mb-2">До: ${until}</div>
                    <button class="btn btn-secondary w-100 mt-2" disabled>Недоступен</button>
                `;
            }
        } else {
            alert("Ошибка: " + data.detail);
        }
    })
    .catch(function(error) {
        console.error("Ошибка при обновлении статуса:", error);
        alert("Произошла сетевая ошибка.");
    });
}