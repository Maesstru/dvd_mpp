var santaBtn = document.getElementsByClassName("clickable")
    var menu = document.getElementById("action-options")
    var glass = document.getElementById("sticla")
    for(var i=0;i<santaBtn.length;i++){
        santaBtn[i].addEventListener("click",() => {
        menu.classList.toggle("slide")
        glass.classList.toggle("in-use")
    })
    }
    glass.addEventListener("click", () => {
        menu.classList.remove("slide")
        glass.classList.remove("in-use")
    })