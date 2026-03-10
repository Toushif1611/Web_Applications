console.log("To-Do App JavaScript loaded");

function toggleSidebar(){
    let sidebar = document.getElementById("sidebar");
    sidebar.classList.toggle("hide");
    sidebar.classList.toggle("show");
}

document.querySelectorAll(".folder-btn").forEach(btn => {
    btn.addEventListener("click", function(){
        let chevron = this.querySelector(".chevron");
        chevron.classList.toggle("rotate");
    });
});