document.addEventListener('DOMContentLoaded', function() {
    var savedName = localStorage.getItem('client_filter_name');
    if (savedName) {
        var nameInput = document.querySelector('input[name="name"]');
        if (nameInput) nameInput.value = savedName;
    }

    var savedSkill = localStorage.getItem('client_filter_skill');
    if (savedSkill) {
        var skillSelect = document.querySelector('select[name="skill"]');
        if (skillSelect) skillSelect.value = savedSkill;
    }
});

document.getElementById('filter-form').addEventListener('submit', function() {
    var name = document.querySelector('input[name="name"]').value;
    var skill = document.querySelector('select[name="skill"]').value;

    localStorage.setItem('client_filter_name', name);
    localStorage.setItem('client_filter_skill', skill);
});

document.getElementById('add-client-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var form = event.target;
    var formData = new FormData(form);

    var form = event.target;
    var url = form.getAttribute('data-url');

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken
        },
        body: formData
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {

        if (data.success_create) {
            alert("Клиент успешно добавлен!\nИмя: " + data.name + "\nТелефон: " + data.phone);

            var modal = bootstrap.Modal.getInstance(document.getElementById('addClientModal'));
            modal.hide();

            form.reset();

            addClientToTable(data);
        } else {
            alert("Ошибка: " + (data.detail || "Неизвестная ошибка"));
        }
    })
    .catch(function(error) {
        console.error("Ошибка при добавлении клиента:", error);
        alert("Произошла сетевая ошибка. Проверьте консоль разработчика (F12).");
    });
});

function addClientToTable(data) {
    var tbody = document.getElementById('clients-table-body');

    var emptyRow = tbody.querySelector('tr td[colspan="5"]');
    if (emptyRow) {
        tbody.innerHTML = '';
    }

    var newRow = document.createElement('tr');
    newRow.id = 'client-row-' + data.client_id;

    var skill = parseInt(data.skill);
    var badgeClass = 'bg-green-lt';
    if (skill > 3) badgeClass = 'bg-red-lt';
    else if (skill > 1) badgeClass = 'bg-yellow-lt';

    var today = new Date();
    var dateStr = today.toLocaleDateString('ru-RU') + ' ' + today.toLocaleTimeString('ru-RU', {hour: '2-digit', minute: '2-digit'});

    newRow.innerHTML = `
        <td>
            <div class="d-flex align-items-center">
                <span class="avatar avatar-sm me-2 bg-blue-lt">👤</span>
                <div>
                    <div class="text-truncate">${data.name}</div>
                </div>
            </div>
        </td>
        <td>${data.phone}</td>
        <td>
            <span class="badge ${badgeClass}">${data.skill}</span>
        </td>
        <td class="text-muted">${dateStr}</td>
        <td>
            <a href="/clients/${data.client_id}/" class="btn btn-sm btn-outline-primary">
                Профиль
            </a>
        </td>
    `;

    tbody.insertBefore(newRow, tbody.firstChild);
}