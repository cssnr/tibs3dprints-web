// const socket = new WebSocket('wss://' + window.location.host + '/ws/home/')
//
// socket.onopen = function (event) {
//     console.log('socket.onopen:', event)
// }
//
// socket.onmessage = function (event) {
//     console.log('socket.onmessage:', event)
//     let data = JSON.parse(event.data)
//     console.log('data:', data)
//     showToast(data.message, 'primary')
// }
//
// socket.onerror = function (event) {
//     console.error('socket.onerror:', event)
// }
//
// socket.onclose = function (event) {
//     console.log('socket.onclose:', event)
//     if (![1000, 1001].includes(event.code)) {
//         console.warn('WebSocket Disconnected!')
//     }
// }

class WebSocketClient {
    constructor() {
        this.toast = new bootstrap.Toast(document.getElementById('ws-toast'))
        this.url = 'wss://' + window.location.host + '/ws/home/'
        this.wsConnect()
    }

    wsConnect() {
        this.socket = new WebSocket(this.url)

        this.socket.onopen = (event) => {
            // console.log('socket.onopen:', event)
            console.log('Connected to WebSockets.')
            this.toast.hide()
            if (this.reconnect) {
                // console.debug('clearTimeout')
                clearTimeout(this.reconnect)
            }
        }

        this.socket.onmessage = (event) => {
            console.log('socket.onmessage:', event)
            this.onMessage(event)
        }

        this.socket.onclose = (event) => {
            // console.log('socket.onclose:', event)
            if (![1000, 1001].includes(event.code)) {
                console.debug('wsReconnect')
                if (!this.toast.isShown()) {
                    this.toast.show()
                }
                this.wsReconnect()
            }
        }
    }

    wsReconnect() {
        this.reconnect = setTimeout(() => this.wsConnect(), 5000)
    }

    onMessage(event) {
        if (event.data === 'pong') {
            return
        }
        const data = JSON.parse(event.data)
        console.log('data:', data)
        showToast(data.message, data.type || 'primary')
    }

    sendMessage(data) {
        this.socket.send(data)
    }
}

const ws = new WebSocketClient()
