$(document).ready(function() {
    // Получение категорий с сервера
    $.ajax({
        url: '/get_categories/',
        method: 'GET',
        success: function(response) {
            response.categories.forEach(function(category) {
                $('#categories-list').append(
                    '<label><input type="radio" name="category" value="' + category.id + '">' + category.name + '</label><br>'
                );
            });

            // Обработчик выбора категории
            $('input[name="category"]').change(function() {
                var categoryId = $(this).val();
                resetForm();  // Сброс формы при смене категории
                loadServices(categoryId);
            });
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при загрузке категорий:', xhr.responseText || error);
        }
    });

    // Функция сброса формы при смене категории или услуги
    function resetForm() {
        $('#services-list').html('');
        $('#masters-list').html('');
        $('#time-slots-list').html('');
        $('#services-container').hide();
        $('#masters-container').hide();
        $('#time-slots-container').hide();
        $('#calendar-container').hide();
        $('#booking-button-container').hide();  // Скрываем кнопку бронирования
    }

    // Функция для загрузки услуг по выбранной категории
    function loadServices(categoryId) {
        $.ajax({
            url: '/get_services_by_category/' + categoryId + '/',
            method: 'GET',
            success: function(response) {
                $('#services-list').html(''); // Очищаем список услуг
                $('#services-container').show();  // Показываем контейнер с услугами

                // Добавляем услуги в список
                response.services.forEach(function(service) {
                    $('#services-list').append(
                        '<label><input type="radio" name="service" value="' + service.id + '">' + service.name + ' - ' + service.price + ' руб - ' + service.duration + ' мин</label><br>'
                    );
                });

                // После того как услуги загружены, добавляем обработчик выбора услуги
                $('input[name="service"]').change(function() {
                    var serviceId = $(this).val();
                    loadMasters(serviceId);  // Загружаем мастеров для выбранной услуги
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке услуг:', error);
            }
        });
    }

    // Функция для загрузки мастеров
    function loadMasters(serviceId) {
        $.ajax({
            url: '/get_masters_by_service/' + serviceId + '/',
            method: 'GET',
            success: function(response) {
                $('#masters-list').html('');
                response.masters.forEach(function(master) {
                    var photoHtml = master.photo ? `<img src="${master.photo}" alt="${master.name}" style="width: 50px; height: 50px;">` : '';
                    $('#masters-list').append(
                        '<label><input type="radio" name="master" value="' + master.id + '">' +
                        master.name + ' ' + photoHtml + '</label><br>'
                    );
                });
                $('#masters-container').show();

                // Обработчик выбора мастера
                $('input[name="master"]').change(function() {
                    var masterId = $(this).val();
                    loadAvailableDates(masterId);
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке мастеров:', xhr.responseText || error);
            }
        });
    }

    // Функция для загрузки доступных дат
    function loadAvailableDates(masterId) {
        $.ajax({
            url: '/get_available_dates_by_master/' + masterId + '/',
            method: 'GET',
            success: function(response) {
                $('#date-list').html('');
                if (Array.isArray(response.dates) && response.dates.length > 0) {
                    response.dates.forEach(function(date) {
                        $('#date-list').append(
                            '<label><input type="radio" name="date" value="' + date + '">' + date + '</label><br>'
                        );
                    });
                } else {
                    $('#date-list').append('<p>Нет доступных дат.</p>');
                }
                $('#calendar-container').show();

                // Обработчик выбора даты
                $('input[name="date"]').change(function() {
                    var selectedDate = $(this).val();
                    loadTimeSlots(masterId, selectedDate);
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке доступных дат:', xhr.responseText || error);
            }
        });
    }

    // Функция для загрузки временных слотов
    function loadTimeSlots(masterId, selectedDate) {
        $.ajax({
            url: `/get_time_slots_by_master_and_date/${masterId}/${selectedDate}/`,
            method: 'GET',
            success: function(response) {
                renderTimeSlots(response.time_slots);
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке временных слотов:', xhr.responseText || error);
            }
        });
    }

    // Рендеринг временных слотов
    function renderTimeSlots(slots) {
        const timeSlotsList = document.getElementById('time-slots-list');
        timeSlotsList.innerHTML = '';

        if (slots.length === 0) {
            timeSlotsList.innerHTML = '<p>Нет доступных временных слотов.</p>';
            return;
        }

        slots.forEach(function(slot) {
            const slotElement = document.createElement('input');
            slotElement.type = 'radio';
            slotElement.name = 'time_slot';
            slotElement.value = slot.id;

            const slotLabel = document.createElement('label');
            slotLabel.textContent = `${slot.start_time} - ${slot.end_time}`;

            const wrapper = document.createElement('div');
            wrapper.appendChild(slotElement);
            wrapper.appendChild(slotLabel);

            timeSlotsList.appendChild(wrapper);
        });

        $('#time-slots-container').show();
    }

    // Обработчик выбора временного слота
    $('#time-slots-list').on('change', 'input[name="time_slot"]', function() {
        var timeSlotId = $(this).val();
        if (timeSlotId) {
            $('#booking-button-container').show();
        }
    });

    // Функция для создания бронирования
    function createBooking(clientId, masterId, datetime, serviceId) {
        console.log("Отправка POST-запроса на сервер");
        console.log({
            client: clientId,
            master: masterId,
            datetime: datetime,
            service: serviceId,
            status: 'pending'
        });

        $.ajax({
            url: '/api/bookings/',  // URL вашего API для создания записи
            method: 'POST',  // Убедитесь, что это POST
            contentType: 'application/json',
            data: JSON.stringify({
                client: clientId,
                master: masterId,
                datetime: datetime,
                service: serviceId,
                status: 'pending'
            }),
            success: function(response) {
                console.log('Запись успешно создана:', response);
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при создании записи:', xhr.responseText);
            }
        });
    }

    // Обработчик кнопки бронирования
    $('#booking-button').click(function() {
        var clientId = $('#client-id').val(); // Получаем ID клиента из скрытого поля
        var masterId = $('input[name="master"]:checked').val();
        var serviceId = $('input[name="service"]:checked').val();
        var date = $('input[name="date"]:checked').val();
        var timeSlotId = $('input[name="time_slot"]:checked').val();

        if (clientId && masterId && serviceId && date && timeSlotId) {
            var datetime = date + ' ' + timeSlotId; // Формируем полное время для записи
            createBooking(clientId, masterId, datetime, serviceId);
        } else {
            alert('Пожалуйста, заполните все поля.');
        }
    });

    // Инициализация слайдера Bootstrap
    $('#reviewCarousel').carousel({
        interval: 5000,
        ride: 'carousel'
    });

    // Установка одинаковой высоты для всех слайдов
    var maxHeight = 0;
    $('#reviewCarousel .carousel-item').each(function() {
        var itemHeight = $(this).outerHeight();
        if (itemHeight > maxHeight) {
            maxHeight = itemHeight;
        }
    });
    $('#reviewCarousel').height(maxHeight);
});
