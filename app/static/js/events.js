// JS for events.html

const eventsForm = document.getElementById('event-form')

eventsForm.addEventListener('submit', addEvent)

function addEvent(event) {
    event.preventDefault()
    //console.log('event:', event)
    const target = event.currentTarget
    console.log('target:', target)
    //const eventId = event.target.elements.inputEvent.value
    //console.log('eventId:', eventId)
    //const name = event.target.elements.inputName.value
    //console.log('name:', name)
    //const url = event.target.elements.inputUrl.value
    //console.log('url:', url)
    //const token = event.target.elements.inputToken.value
    //console.log('token:', token)
    for (const el of event.target.elements) {
        if (el.nodeName === 'INPUT') {
            console.log(`${el.id}: ${el.value}`)
        }
    }
}
