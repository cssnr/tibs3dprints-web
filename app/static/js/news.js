// JS for news.html

document.querySelectorAll('.date').forEach((el) => {
    // console.debug('el.textContent:', el.textContent)
    const date = new Date(0)
    date.setUTCSeconds(parseInt(el.textContent))
    // console.debug('date:', date)
    // el.textContent = date.toLocaleString()
    let options = {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true,
    }
    let fmt = date.toLocaleString('en-US', options)
    el.textContent = fmt.replace(/,([^,]*)$/, ' at$1')
    el.classList.remove('d-none')
})
