// JS for news.html

document.getElementById('send-toast').addEventListener('click', testToast)

const input = document.getElementById('toast-message')

function testToast(event) {
    console.debug('testToast:', event)
    showToast(input.value || 'Test Toast Message')
}
