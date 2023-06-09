
function translateElements(translation, elements){
    for(let i=0;i < elements.length; i++){
        if(elements[i].childElementCount > 0){
            elements[i].childNodes[1].innerHTML = translation[elements[i].innerText];
        } else {
            elements[i].innerHTML = translation[elements[i].innerText];
        }
    }
}

function translateGui(transUrl){
    ajaxGet(
        transUrl,
        function (xhttp){
            let translation = JSON.parse(xhttp.responseText);
            translateElements(translation,document.getElementsByClassName("translate"));
            translateElements(translation,document.getElementsByTagName("label"));
        },
        ajaxFail
    );
}