// Функция для открытия модального окна
function openModal(src, alt) {
    const modal = document.getElementById('modal');
    const modalImg = document.getElementById('modal-image');
    const captionText = document.getElementById('caption');
    
    modal.style.display = 'block';
    modalImg.src = src;
    captionText.innerHTML = alt;
}
// Функция для закрытия модального окна
function closeModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}
// Закрытие модального окна при клике вне изображения
window.onclick = function(event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}
