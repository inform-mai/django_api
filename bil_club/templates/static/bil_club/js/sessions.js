function endSession(sessionId, clientId) {
    if (!confirm("Завершить эту игру?")) {
        return;
    }

    fetch("/api/sessions/end/" + sessionId + "/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrftoken
        },
        body: "client_id=" + clientId
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.end_success) {
            alert(
                "Игра завершена!\n" +
                "Время: " + data.time_spent + "\n" +
                "Стоимость: " + data.total_cost + " ₽"
            );

            var row = document.getElementById("session-row-" + sessionId);
            if (row) {
                row.remove();
            }

            var tbody = document.getElementById("sessions-table-body");
            if (tbody.children.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-muted py-4">
                            Нет активных игр
                        </td>
                    </tr>
                `;
            }
        } else {
            alert("Ошибка: " + data.detail);
        }
    })
    .catch(function(error) {
        console.error("Ошибка при завершении игры:", error);
        alert("Произошла сетевая ошибка. Проверьте консоль разработчика (F12).");
    });
}