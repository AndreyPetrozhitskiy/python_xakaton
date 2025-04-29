document.addEventListener('DOMContentLoaded', function () {
    const cards = document.querySelectorAll('.monument-card');
    const modal = document.getElementById('modal');
    const backdrop = document.getElementById('modal-backdrop');
    const modalCover = document.getElementById('modal-cover');
    const modalName = document.getElementById('modal-name');
    const modalWar = document.getElementById('modal-war');
    const modalDate = document.getElementById('modal-date');
    const modalStory = document.getElementById('modal-story');
    const modalMedia = document.getElementById('modal-media');
    const modalComments = document.getElementById('modal-comments');
    const commentForm = document.getElementById('comment-form');
    let currentCardId = null;

    cards.forEach(card => {
        card.addEventListener('click', function () {
            currentCardId = card.dataset.id;
            modalCover.src = card.dataset.cover;
            modalName.textContent = card.dataset.name;
            modalWar.textContent = card.dataset.war;
            modalDate.textContent = card.dataset.date;
            modalStory.textContent = card.dataset.story;

            // Медиа
            modalMedia.innerHTML = '';
            const photos = card.dataset.photos ? card.dataset.photos.split(',') : [];
            const videos = card.dataset.videos ? card.dataset.videos.split(',') : [];
            const audios = card.dataset.audios ? card.dataset.audios.split(',') : [];
            photos.forEach(file => {
                if (file) {
                    const img = document.createElement('img');
                    img.src = '/static/uploads/' + file;
                    img.alt = 'Фото';
                    img.onclick = () => window.open(img.src, '_blank');
                    modalMedia.appendChild(img);
                }
            });
            videos.forEach(file => {
                if (file) {
                    const video = document.createElement('video');
                    video.src = '/static/uploads/' + file;
                    video.controls = true;
                    video.onclick = () => window.open(video.src, '_blank');
                    modalMedia.appendChild(video);
                }
            });
            audios.forEach(file => {
                if (file) {
                    const audio = document.createElement('audio');
                    audio.src = '/static/uploads/' + file;
                    audio.controls = true;
                    modalMedia.appendChild(audio);
                }
            });

            // Комментарии
            loadComments(currentCardId);

            modal.classList.add('show');
            backdrop.classList.add('show');
        });
    });

    window.closeModal = function () {
        modal.classList.remove('show');
        backdrop.classList.remove('show');
    };

    window.submitComment = function (event) {
        event.preventDefault();
        const nick = document.getElementById('comment-nick').value;
        const text = document.getElementById('comment-text').value;
        if (!nick || !text) return false;
        fetch(`/comments/${currentCardId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `nickname=${encodeURIComponent(nick)}&comment=${encodeURIComponent(text)}`
        })
        .then(() => {
            document.getElementById('comment-text').value = '';
            loadComments(currentCardId);
        });
        return false;
    };

    function loadComments(cardId) {
        fetch(`/comments/${cardId}`)
            .then(response => response.json())
            .then(comments => {
                modalComments.innerHTML = '';
                comments.forEach(c => {
                    const li = document.createElement('li');
                    li.textContent = `${c.nickname}: ${c.comment}`;
                    modalComments.appendChild(li);
                });
            });
    }
});
