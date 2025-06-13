// JS for links.html and options.html

document.addEventListener('DOMContentLoaded', domContentLoaded)

document
    .querySelectorAll('[data-bs-toggle="tooltip"]')
    .forEach((el) => new bootstrap.Tooltip(el))

const backToTop = document.getElementById('back-to-top')

if (backToTop) {
    window.addEventListener('scroll', debounce(onScroll))
    backToTop.addEventListener('click', () => {
        document.body.scrollTop = 0
        document.documentElement.scrollTop = 0
    })
}

// // Set Timezone Cookie
// const timezone = Cookies.get('timezone')
// if (!sessionStorage.getItem('timezone') || !timezone) {
//     const current = Intl.DateTimeFormat().resolvedOptions().timeZone
//     if (timezone !== current) {
//         Cookies.set('timezone', timezone)
//     }
// }

// Set Timezone Cookie

/**
 * @type {string|undefined}
 */
const timezone = Cookies.get('timezone')
const tz = Intl.DateTimeFormat().resolvedOptions().timeZone
if (timezone !== tz) {
    console.debug('Setting timezone:', tz)
    Cookies.set('timezone', tz)
}

if (typeof ClipboardJS !== 'undefined') {
    const clipboard = new ClipboardJS('.clip')
    clipboard.on('success', function (event) {
        // console.debug('clipboard.success:', event)
        const text = event.text.trim()
        console.debug(`text: "${text}"`)
        if (event.trigger.dataset.toast) {
            showToast(event.trigger.dataset.toast)
        } else {
            showToast('Copied to Clipboard')
        }
    })
    clipboard.on('error', function (event) {
        console.debug('clipboard.error:', event)
        showToast('Clipboard Copy Failed', 'warning')
    })
}

async function domContentLoaded() {
    // Show custom django-toast classes on load
    $('.django-toast').each(function () {
        const toast = new bootstrap.Toast($(this))
        console.debug('toastAlert:', toast)
        $(this).on('mousemove', () => toast.hide())
        toast.show()
    })

    // Register Service Worker
    if ('serviceWorker' in navigator) {
        await registerServiceWorker()
    }
}

async function registerServiceWorker() {
    try {
        const registration = await navigator.serviceWorker.register('/sw.js', {
            scope: '/',
        })
        console.debug('registerServiceWorker:', registration)
        if (registration.installing) {
            console.debug('Service Worker: installing')
        } else if (registration.waiting) {
            console.debug('Service Worker: waiting')
        } else if (registration.active) {
            console.debug('Service Worker: active')
        } else {
            console.warn('Service Worker Registration Unknown:', registration)
        }
    } catch (error) {
        console.error('Service Worker Registration Error:', error)
    }
}

/**
 * Show Bootstrap Toast
 * @function showToast
 * @param {String} message
 * @param {String} type
 */
function showToast(message, type = 'primary') {
    console.log(`showToast: ${type}:`, message)
    const element = document.querySelector('#clone > .toast').cloneNode(true)
    element.addEventListener('mousemove', () => toast.hide())
    element.classList.add(`text-bg-${type}`)
    element.querySelector('.toast-body').innerHTML = message
    document.getElementById('toast-container').appendChild(element)
    const toast = new bootstrap.Toast(element)
    toast.show()
}

/**
 * On Scroll Callback
 * @function onScroll
 */
function onScroll() {
    if (
        document.body.scrollTop > 20 ||
        document.documentElement.scrollTop > 20
    ) {
        backToTop.style.display = 'block'
    } else {
        backToTop.style.display = 'none'
    }
}

/**
 * DeBounce Function
 * @function debounce
 * @param {Function} fn
 * @param {Number} timeout
 */
function debounce(fn, timeout = 300) {
    let timeoutID
    return (...args) => {
        clearTimeout(timeoutID)
        timeoutID = setTimeout(() => fn(...args), timeout)
    }
}
