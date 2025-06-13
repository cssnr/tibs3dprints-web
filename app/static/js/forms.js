// Form Submit Handler

document.querySelectorAll('.form-control').forEach((el) => {
    el.addEventListener('focus', () => {
        el.classList.remove('is-invalid')
    })
})

document.querySelector('form.submit')?.addEventListener('submit', formSubmit)

async function formSubmit(event) {
    event.preventDefault()
    console.debug('formSubmit:', event)
    if (event.submitter.classList.contains('disabled')) {
        return console.debug('Double Click Prevented.')
    }

    console.debug('event.target.method:', event.target.method)
    console.debug('event.target.action:', event.target.action)
    console.debug('processing:', event.target.dataset.processing)
    console.debug('success:', event.target.dataset.success)

    try {
        event.submitter.classList.add('disabled')
        document
            .querySelector(event.target.dataset.processing)
            ?.classList.remove('d-none')

        const formData = new FormData(event.target)
        console.debug('formData:', formData)

        const response = await fetch(event.target.action, {
            method: event.target.method,
            body: formData,
        })
        console.debug('response:', response)
        const json = await response.json()
        console.debug('json:', json)
        if (response.ok) {
            console.debug('Success')
            event.target.classList.add('d-none')
            document
                .querySelector(event.target.dataset.success)
                ?.classList.remove('d-none')
        } else if (json.error) {
            console.debug('Error Message')
            showToast(json.error, 'danger')
        } else {
            console.debug('Loop Errors')
            for (const [key, value] of Object.entries(json)) {
                console.debug(`${key}: ${value}`)
                const el = event.target.querySelector(`[name="${key}"]`)
                console.debug('el:', el)
                el.classList.add('is-invalid')
                el.nextElementSibling.textContent = value.toString()
            }
        }
    } catch (error) {
        console.debug('Catch Error:', error)
        showToast(error.message, 'danger')
    } finally {
        event.submitter.classList.remove('disabled')
        document
            .querySelector(event.target.dataset.processing)
            ?.classList.add('d-none')
    }
}
