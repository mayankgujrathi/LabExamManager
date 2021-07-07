const __token = function(){
  const name = 'csrftoken'
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}()

const _utils = {
  mov: url => window.location.assign(window.location.origin + url),
  dismiss: (func=() => {}) => {
    M.Toast.dismissAll()
    setTimeout(() => {
      func()
    }, 380)
  },
  info: (message, func = () => {}) => M.toast({
    html: `<i class="material-icons blue-text">info</i>&ensp;${message}`,
    classes: 'rounded',
    completeCallback: func
  }),
  error: (message, func = () => {}) => M.toast({
    html: `<i class="material-icons red-text">highlight_off</i>&ensp;${message}`,
    classes: 'rounded',
    completeCallback: func
  }),
  success: (message, func = () => {}) => M.toast({
    html: `<i class="material-icons teal-text">check_circle</i>&ensp;${message}`,
    classes: 'rounded',
    completeCallback: func
  }),
  warning: (message, func = () => {}) => M.toast({
    html: `<i class="material-icons yellow-text">warning</i>&ensp;${message}`,
    classes: 'rounded',
    completeCallback: func
  }),
  getColor: () => {
    const color = [
      {red: 'white-text'},
      {green: 'white-text'},
      {pink: 'white-text'},
      {yellow: 'black-text'},
      {purple: 'white-text'},
      {blue: 'white-text'},
      {cyan: 'white-text'},
      {teal: 'white-text'},
      {lime: 'black-text'},
      {amber: 'black-text'},
      {'deep-orange': 'white-text'},
      {brown: 'white-text'},
      {grey: 'white-text'},
      {'blue-grey': 'white-text'},
    ]
    return color[Math.floor(Math.random() * (color.length - 0) + 0)]
  },
  deload: (delay=500) => setTimeout(() => {window.location.reload()}, delay),
  post: (url, data, stringify=true) => fetch(
      new Request(
        `${window.location.origin}${url}`,
        { headers: { 'X-CSRFToken': __token } }
      ),
      {
        method: 'POST',
        mode: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'HTTP_X_CSRFTOKEN': __token,
          'X-CSRFToken': __token,
        },
        body: stringify? JSON.stringify(data): data,
      }
    ).then(res => res.json().then(data => data)),
  postFile: (url, data, custHeaders={}) => fetch(
      new Request(
        `${window.location.origin}${url}`,
        { headers: { 'X-CSRFToken': __token } }
      ),
      {
        method: 'POST',
        mode: 'same-origin',
        headers: {
          ...custHeaders,
          'HTTP_X_CSRFTOKEN': __token,
          'X-CSRFToken': __token,
        },
        body: data,
      }
    ).then(res => res.json().then(data => data)),
  update: (url, data, stringify=true) => {
    return fetch(
      new Request(
        `${window.location.origin}${url}`,
        { headers: { 'X-CSRFToken': __token } }
      ),
      {
        method: 'UPDATE',
        mode: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'HTTP_X_CSRFTOKEN': __token,
          'X-CSRFToken': __token,
        },
        body: stringify? JSON.stringify(data): data,
      }
    ).then(res => res.json().then(data => data))
  },
  get: (url, method='GET') => fetch(
      new Request(
        `${window.location.origin}${url}`,
        { headers: { 'X-CSRFToken': __token } }
      ),
      {
        method,
        mode: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'HTTP_X_CSRFTOKEN': __token,
          'X-CSRFToken': __token,
        },
      }
    ).then(res => res.json().then(data => data)),
  delete: (url, data) => fetch(
      new Request(
        `${window.location.origin}${url}`,
        { headers: { 'X-CSRFToken': __token } }
      ),
      {
        method: 'DELETE',
        mode: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'HTTP_X_CSRFTOKEN': __token,
          'X-CSRFToken': __token,
        },
        body: JSON.stringify(data),
      }
    ).then(res => res.json().then(data => data))
}
