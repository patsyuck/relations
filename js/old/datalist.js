// Получаем элементы <datalist> и <input>.
var dataList = document.getElementById('group');
var input = document.getElementById('ajax');

// Создаем новый XMLHttpRequest.
var request = new XMLHttpRequest();

// Обрабатываем изменение состояния для запроса.
request.onreadystatechange = function(response) {
if (request.readyState === 4) {
if (request.status === 200) {
      // Парсируем JSON
var jsonOptions = JSON.parse(request.responseText);

      // Перебираем через цикл массив JSON.
jsonOptions.forEach(function(item) {
        // Создаем новый элемент <option>.
var option = document.createElement('option');
        // Устанавливаем значение, используя элементы массива JSON.
option.value = item;
        // Добавляем элемент <option> к <datalist>.
dataList.appendChild(option);
      });

      // Обновляем текст заполнителя.
input.placeholder = "FORTUNA";
    } else {
      // Возникла ошибка :(
input.placeholder = "Couldn't load datalist";
    }
  }
};

// Обновляем текст заполнителя.
input.placeholder = "Loading groups...";

// Настраиваем и выполняем запрос.
request.open('GET', '../json/datalist.json', true);
request.send();