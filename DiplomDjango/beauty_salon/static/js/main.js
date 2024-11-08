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

            // После того как категории загружены, добавляем обработчик выбора категории
            $('input[name="category"]').change(function() {
                var categoryId = $(this).val();
                loadServices(categoryId);  // Загружаем услуги для выбранной категории
            });
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при загрузке категорий:', error);
        }
    });


    // Функция для загрузки услуг по выбранной категории
function loadServices(categoryId) {
    $.ajax({
        url: '/get_services_by_category/' + categoryId + '/', // Передаем categoryId в URL
        method: 'GET',
        success: function(response) {
            $('#services-list').html(''); // Очищаем список услуг
            $('#masters-list').html(''); // Очищаем список мастеров
            $('#time-slots-list').html(''); // Очищаем список временных слотов
            $('#services-container').show();  // Показываем контейнер с услугами
            $('#masters-container').hide();  // Скрываем контейнер с мастерами
            $('#time-slots-container').hide();  // Скрываем контейнер с временными слотами

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


// Функция для загрузки мастеров по выбранной услуге
function loadMasters(serviceId) {
    $.ajax({
        url: '/get_masters_by_service/' + serviceId + '/',  // Передаем serviceId в URL
        method: 'GET',
        success: function(response) {
            $('#masters-list').html('');  // Очищаем список мастеров
            $('#masters-container').show();  // Показываем контейнер с мастерами
            $('#time-slots-container').hide();  // Скрываем контейнер с временными слотами

            response.masters.forEach(function(master) {
                var photoHtml = master.photo ? `<img src="${master.photo}" alt="${master.name}" style="width: 50px; height: 50px;">` : '';
                $('#masters-list').append(
                    '<label><input type="radio" name="master" value="' + master.id + '">' +
                    master.name +  // Отображаем отформатированное имя мастера
                    photoHtml +  // Показываем фото, если оно есть
                    '</label><br>'
                );
            });

            // Добавляем обработчик выбора мастера
            $('input[name="master"]').change(function() {
                var masterId = $(this).val();
                loadTimeSlots(masterId);  // Загружаем временные слоты для выбранного мастера
            });
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при загрузке мастеров:', error);
        }
    });
}


    // Функция для загрузки временных слотов по выбранному мастеру
function loadTimeSlots(masterId) {
    $.ajax({
        url: '/get_time_slots_by_master/' + masterId + '/',  // Передаем masterId в URL
        method: 'GET',
        success: function(response) {
            $('#time-slots-list').html('');  // Очищаем список временных слотов
            $('#time-slots-container').show();  // Показываем контейнер с временными слотами

            if (response.time_slots.length === 0) {
                $('#time-slots-list').append('<p>Нет доступных временных слотов.</p>');
            } else {
                response.time_slots.forEach(function(timeSlot) {
                    $('#time-slots-list').append(
                        '<label><input type="radio" name="time_slot" value="' + timeSlot.id + '">' +
                        timeSlot.start_time + ' - ' + timeSlot.end_time + '</label><br>'
                    );
                });
            }
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при загрузке временных слотов:', error);
        }
    });
}
    $(document).ready(function() {
    $('#id_start_date').datepicker({
      format: 'yyyy-mm-dd',
      autoclose: true,
      todayHighlight: true
    });
    $('#id_end_date').datepicker({
      format: 'yyyy-mm-dd',
      autoclose: true,
      todayHighlight: true
    });
  });

});
