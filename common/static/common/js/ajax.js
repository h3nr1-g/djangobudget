function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function ajaxGet(url, okay_200_function, non_200_function) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            okay_200_function(this);
        }
        if (this.readyState == 4 && this.status != 200) {
            non_200_function(this);
        }

    };
    xhttp.open("GET", url, true);
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send();
}

function ajaxPost(url, okay_200_function, non_200_function) {
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            okay_200_function(this);
        }
        if (this.readyState == 4 && this.status != 200) {
            non_200_function(this);
        }

    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send();
}

function ajaxDeleteAndReload(url, question) {
    if (question && !confirm(question)) {
        return;
    }
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            window.location.reload();
        }
    };
    xhttp.open("DELETE", url, true);
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send();
}

function ajaxDeleteAndRedirect(url,redirect_url, question) {
    if (question && !confirm(question)) {
        return;
    }
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href=redirect_url;
        }
        if (this.readyState == 4 && this.status != 200) {
            ajax_fail(this);
        }
    };
    xhttp.open("DELETE", url, true);
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send();
}

function ajaxFail(request) {
    alert("Received response with status code: " + String(request.status));
    alert(JSON.parse(request.responseText).error);
}

function ajaxDeleteAndDo(url, do_func, question) {
    if (question && !confirm(question)) {
        return;
    }
    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
           do_func(xhttp);
        }
    };
    xhttp.open("DELETE", url, true);
    xhttp.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
    xhttp.send();
}
