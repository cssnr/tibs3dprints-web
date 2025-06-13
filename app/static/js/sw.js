// Service Worker

const cacheName = 'v1'

const cacheResources = [
    '/',
    '/news/',
    '/message/',
    '/contact/',

    '/static/css/main.css',
    '/static/bootstrap/bootstrap.css',
    '/static/bootstrap/theme.js',

    '/static/js/forms.js',
    '/static/js/home.js',
    '/static/js/main.js',
    '/static/js/news.js',
    '/static/js/socket.js',
    '/static/js/user.js',

    '/static/images/apple-touch-icon.png',
    '/static/images/avatar.png',
    '/static/images/favicon.ico',

    '/static/dist/bootstrap/bootstrap.bundle.min.js',
    '/static/dist/clipboard/clipboard.min.js',
    '/static/dist/fontawesome/css/all.min.css',
    '/static/dist/fontawesome/webfonts/fa-brands-400.woff2',
    '/static/dist/fontawesome/webfonts/fa-regular-400.woff2',
    '/static/dist/fontawesome/webfonts/fa-solid-900.woff2',
    '/static/dist/jquery/jquery.min.js',
    '/static/dist/js-cookie/js.cookie.min.js',
]

const cacheExcludes = [
    '/api',
    '/admin',
    '/flower',
    '/oauth',
    '/phpmyadmin',
    '/redis',
    '/ws',
]

const addResourcesToCache = async (cacheResources) => {
    console.debug('%c addResourcesToCache:', 'color: Cyan', cacheResources)
    try {
        const cache = await caches.open(cacheName)
        await cache.addAll(cacheResources)
    } catch (e) {
        console.error(`cache.addAll error: ${e.message}`, e)
    }
}

const putInCache = async (request, response) => {
    console.debug('%c putInCache:', 'color: Khaki', `${request.url}`)
    try {
        const cache = await caches.open(cacheName)
        await cache.put(request, response)
    } catch (e) {
        console.error(`cache.put error: ${e.message}`, e)
    }
}

const cleanupCache = async (event) => {
    console.debug('%c cleanupCache:', 'color: Coral', event)
    const keys = await caches.keys()
    console.debug('keys:', keys)
    for (const key of keys) {
        if (key !== cacheName) {
            console.log('%c Removing Old Cache:', 'color: Yellow', `${key}`)
            try {
                await caches.delete(key)
            } catch (e) {
                console.error(`caches.delete error: ${e.message}`, e)
            }
        }
    }
}

const cacheFirst = async (event) => {
    console.debug('%c cacheFirst:', 'color: Aqua', event.request.url)

    const responseFromCache = await caches.match(event.request)
    if (responseFromCache?.ok) {
        return responseFromCache
    }

    try {
        const responseFromNetwork = await fetch(event.request)
        if (responseFromNetwork?.ok) {
            await putInCache(event.request, responseFromNetwork.clone())
        }
        return responseFromNetwork
    } catch (e) {
        console.debug(`fetch error: ${e.message}`, 'color: OrangeRed')
    }

    return return408(event)
}

const networkFirst = async (event) => {
    console.debug('%c networkFirst:', 'color: Orange', event.request.url)

    try {
        const responseFromNetwork = await fetch(event.request)
        // console.debug('responseFromNetwork:', responseFromNetwork)
        if (responseFromNetwork.type === 'opaqueredirect') {
            console.debug('%c opaqueredirect:', 'color: Yellow', event.request)
            return responseFromNetwork
        }
        if (responseFromNetwork?.ok) {
            // noinspection ES6MissingAwait
            putInCache(event.request, responseFromNetwork.clone())
            return responseFromNetwork
        }
    } catch (e) {
        console.debug(`fetch error: ${e.message}`, 'color: OrangeRed')
    }

    const responseFromCache = await caches.match(event.request)
    // console.debug('responseFromCache:', responseFromCache)
    if (responseFromCache?.ok) {
        return responseFromCache
    }

    return return408(event)
}

function return408(event) {
    console.debug('%c 408: No Network/Cache:', 'color: Red', event.request.url)
    return new Response('No Network or Cache Available', {
        status: 408,
        headers: { 'Content-Type': 'text/plain' },
    })
}

async function fetchResponse(event) {
    // console.debug('fetchResponse:', event.request)
    const url = new URL(event.request.url)
    // console.debug('url:', url)
    // console.debug('url.pathname:', url.pathname)
    if (
        event.request.method !== 'GET' ||
        self.location.origin !== url.origin ||
        cacheExcludes.some((e) => url.pathname.startsWith(e))
    ) {
        console.debug('%c Excluded:', 'color: Yellow', event.request.url)
        return
    }
    if (url.pathname.startsWith('/static/')) {
        return event.respondWith(cacheFirst(event))
    }
    return event.respondWith(networkFirst(event))
}

self.addEventListener('fetch', fetchResponse)

self.addEventListener('install', (event) => {
    console.debug('%c install:', 'color: Cyan', event)
    event.waitUntil(addResourcesToCache(cacheResources))
    // noinspection JSIgnoredPromiseFromCall
    self.skipWaiting()
})

self.addEventListener('activate', (event) => {
    console.debug('%c activate:', 'color: Cyan', event)
    event.waitUntil(cleanupCache(event))
})
