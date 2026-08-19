document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    const mobileMenu = document.getElementById("mobileMenu");

    mobileMenu?.addEventListener("click", () => {
        sidebar?.classList.toggle("open");
    });

    document.querySelectorAll(".flash-close").forEach((button) => {
        button.addEventListener("click", () => {
            button.closest(".flash")?.remove();
        });
    });

    setTimeout(() => {
        document.querySelectorAll(".flash").forEach((flash) => {
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-6px)";
            setTimeout(() => flash.remove(), 250);
        });
    }, 4500);
});
