// CSRF токен для AJAX запросов
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Функция для AJAX запросов лайков
function sendLike(url, value, ratingElement) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
        body: `value=${value}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            ratingElement.textContent = data.rating;
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка. Попробуйте еще раз.');
    });
}

// Функция для отметки правильного ответа
function markCorrect(answerId, url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Убираем отметки со всех ответов
            document.querySelectorAll('.correct-badge').forEach(badge => {
                badge.style.display = 'none';
            });
            // Показываем отметку на выбранном ответе
            const badge = document.getElementById(`correct-badge-${data.answer_id}`);
            if (badge) {
                badge.style.display = 'inline-block';
            }
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка. Попробуйте еще раз.');
    });
}

// Инициализация обработчиков при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing like buttons...');

    // Лайки вопросов
    const questionLikeButtons = document.querySelectorAll('.like-question-btn');
    console.log('Found question like buttons:', questionLikeButtons.length);

    questionLikeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const questionId = this.dataset.questionId;
            const value = this.dataset.value;
            const ratingElement = document.getElementById(`question-rating-${questionId}`);
            const url = `/question/${questionId}/like/`;
            console.log('Question like clicked:', questionId, value);
            sendLike(url, value, ratingElement);
        });
    });

    // Лайки ответов
    const answerLikeButtons = document.querySelectorAll('.like-answer-btn');
    console.log('Found answer like buttons:', answerLikeButtons.length);

    answerLikeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const answerId = this.dataset.answerId;
            const value = this.dataset.value;
            const ratingElement = document.getElementById(`answer-rating-${answerId}`);
            const url = `/answer/${answerId}/like/`;
            console.log('Answer like clicked:', answerId, value);
            sendLike(url, value, ratingElement);
        });
    });

    // Отметка правильного ответа
    const markCorrectButtons = document.querySelectorAll('.mark-correct-btn');
    console.log('Found mark correct buttons:', markCorrectButtons.length);

    markCorrectButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const answerId = this.dataset.answerId;
            const url = `/answer/${answerId}/correct/`;
            console.log('Mark correct clicked:', answerId);
            markCorrect(answerId, url);
        });
    });
});
