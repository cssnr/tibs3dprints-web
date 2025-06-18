// poll.js

document.addEventListener('DOMContentLoaded', () => {
    console.log(`DOMContentLoaded: %c poll.js`, 'color: Green')
    const params = new URLSearchParams(window.location.search)
    console.log('params:', params)

    const items = ['title', 'question', 'name1', 'name2']
    for (const item of items) {
        console.log('item:', item)
        const value = params.get(item)
        console.log('value:', value)
        if (!value?.length) continue
        const el = document.getElementById(item)
        console.log('el:', el)
        if (el == null) continue
        el.textContent = value
    }

    const img1Url = params.get('img1')
    console.log('img1Url:', img1Url)
    const img2Url = params.get('img2')
    console.log('img2Url:', img2Url)

    if (img1Url) {
        document.getElementById('previewImage1').src =
            decodeURIComponent(img1Url)
    }
    if (img2Url) {
        document.getElementById('previewImage2').src =
            decodeURIComponent(img2Url)
    }
})
