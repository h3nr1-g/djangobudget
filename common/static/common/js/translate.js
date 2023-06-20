
function translateElements(translation, elements){
    for(let i=0;i < elements.length; i++){
        let trans = translation[elements[i].innerText];
        if(trans == undefined)
            continue;

        if(elements[i].childElementCount > 0){
            elements[i].childNodes[1].innerHTML = trans;
        } else {
            elements[i].innerHTML = trans;
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