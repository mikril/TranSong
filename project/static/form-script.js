var sendButton = document.getElementsByClassName("Send")[0];
var songsListBlock = document.getElementsByClassName("songsList")[0];
var tagsListBlock = document.getElementsByClassName("tagsList")[0];
songsList=[]
tagsList=[]
var form = document.getElementsByClassName("playListForm")[0];
form.addEventListener("keydown", function(event) {
field = form.querySelector('input:focus')
if (event.key)
    field.setCustomValidity("")
if (event.key === "Enter" & field.id === "songs") {
    event.preventDefault();
    if (!field.value.includes("https://genius.com/"))  {
        field.setCustomValidity("Используйте ссылки на genius")
        field.reportValidity()
        form.noValidate = true;
    }   
    else {
    var wrapper = document.createElement("div");
    wrapper.style.display = "flex";
    var text = document.createTextNode(field.value.length > 40 ? (field.value.slice(0,40) + "...") : field.value);
        songsList.push(field.value)
        var button = document.createElement("button");
        button.textContent = "X";
        button.id = songsList.length - 1
        button.type = "button";
        button.classList.add("button-x");
        button.onclick = function(e) {songsList[ e.target.id]=NaN;
                                    e.target.parentNode.remove()}
        button.style.display = "block"
        wrapper.appendChild(text);
        wrapper.appendChild(button);
        songsListBlock.appendChild(wrapper);    
        field.value = ""
    }    
}

if (event.key === "Enter" & field.id === "tags"  ) {
    event.preventDefault();
    if (tagsList.length >= 3 | field.value === "") {
        field.setCustomValidity("Максимум 3");
        field.reportValidity()
        form.noValidate = true;
    }
    else{
    var wrapper = document.createElement("div");
    wrapper.style.display = "flex";
    var text = document.createTextNode('#'+field.value);
        tagsList.push(field.value)
        var button = document.createElement("button");
        button.textContent = "X";
        button.id = field.value
        button.type = "button";
        button.classList.add("button-x");
        button.onclick=function(e) {tagsList.splice(tagsList.indexOf(e.target.id), 1);
                                    e.target.parentNode.remove()}
        button.style.display="block"
        wrapper.appendChild(text);
        wrapper.appendChild(button);
        tagsListBlock.appendChild(wrapper);
        field.value=""
    }
}
if (event.key === "Enter" & songsList.length == 0) {
    event.preventDefault();
}
});


form.addEventListener("submit", function(event) {
    event.preventDefault();
    nameInput=document.getElementById("name")
    photo_urlInput=document.getElementById("photo_url")
    songsList=songsList.filter(function(value) {
        return value===value;
    });
    console.log(songsList)
    if (songsList.length===0) {

        songInput=document.getElementById("songs")
        songInput.focus()
        songInput.setCustomValidity("Не добавлены песни");
        songInput.reportValidity()
        form.noValidate = true;
        
    }
    else if (nameInput.value==="") {
        nameInput.focus()
        nameInput.setCustomValidity("Не добавлено название подборки");
        nameInput.reportValidity()
        form.noValidate = true;
        }
        else if (photo_urlInput.value==="") {
        photo_urlInput.focus()
        photo_urlInput.setCustomValidity("Не добавлена обложка подборки");
        photo_urlInput.reportValidity()
        form.noValidate = true;
        }
    else{
    var formData = new FormData(form);
    // Изменяем значение поля "name"
    formData.set("songs", songsList);
    formData.set("tags", tagsList);

    // Отправляем форму с измененными данными
    var xhr = new XMLHttpRequest();
    xhr.open("POST", form.action);
    xhr.send(formData);
    window.location.href = "../successful";}
});

