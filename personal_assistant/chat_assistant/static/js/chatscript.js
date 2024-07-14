// JavaScript for handling chat functionality (optional for dynamic chat features)
document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    var userInput = document.getElementById('user-input');
    var message = userInput.value.trim();

    if (message !== '') {
        var chatBox = document.getElementById('chat-box');
        var userMessageElement = document.createElement('div');
        userMessageElement.classList.add('message', 'user-message');
        userMessageElement.innerHTML = '<p>' + message + '</p>';
        chatBox.appendChild(userMessageElement);

        // Simulate AI response (replace with actual AI response handling)
        setTimeout(function() {
            var aiMessageElement = document.createElement('div');
            aiMessageElement.classList.add('message', 'ai-message');
            aiMessageElement.innerHTML = '<p>This is a sample AI response.</p>';
            chatBox.appendChild(aiMessageElement);
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 500);

        userInput.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}
