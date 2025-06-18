// Admin JS

document.addEventListener('formset:added', (event) => {
    console.log('formset:added - event.detail:', event.detail)
})

document.addEventListener('formset:removed', (event) => {
    console.log('formset:removed - event.detail:', event.detail)
})

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded - admin.js')
})

document.getElementById('previewPoll').addEventListener('click', (e) => {
    const pollForm = document.getElementById('poll_form')
    console.log('pollForm:', pollForm)

    const data = {
        title: pollForm.elements['id_title']?.value,
        question: pollForm.elements['id_question']?.value,
        name1: pollForm.elements['id_choice_set-0-name']?.value,
        name2: pollForm.elements['id_choice_set-1-name']?.value,
    }
    console.log('data:', data)

    const dataQueryString = new URLSearchParams(data).toString()
    console.log('dataQueryString:', dataQueryString)

    const fileEl1 = pollForm.elements['id_choice_set-0-file']
    const fileEl2 = pollForm.elements['id_choice_set-1-file']

    const filesToRead = []

    if (fileEl1?.files.length > 0) filesToRead.push(fileEl1.files[0])
    if (fileEl2?.files.length > 0) filesToRead.push(fileEl2.files[0])

    console.log('filesToRead:', filesToRead)

    const objectUrls = filesToRead.map((file) => URL.createObjectURL(file))
    const fileQueryString = objectUrls
        .map((url, i) => `img${i + 1}=${encodeURIComponent(url)}`)
        .join('&')
    console.log('fileQueryString:', fileQueryString)

    window.open(
        `/preview/poll/?${dataQueryString}&${fileQueryString}`,
        '_blank',
        'width=400,height=680,resizable=yes'
    )
})
