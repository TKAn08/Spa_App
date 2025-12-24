var form1 = document.getElementById("form1");
var form2 = document.getElementById("form2");
var form3 = document.getElementById("form3");
var next1 = document.getElementById("next1");
var next2 = document.getElementById("next2");
var back1 = document.getElementById("back1");
var back2 = document.getElementById("back2");
var submitBtn = document.getElementById("submit");
const errorText = document.getElementsByClassName('error-text');
const registerForm = document.getElementById("registerForm")

const rootStyles = getComputedStyle(document.documentElement);
var progress = document.getElementById("progress");
const progress_col = parseInt(rootStyles.getPropertyValue('--container-width')) / 3;

next1.onclick = function () {

    //Xử lý đăng nhập
    const username = document.querySelector('input[name="username"]');
    const password = document.querySelector('input[name="password"]');
    const confirmPassword = document.querySelector('input[name="confirm_password"]');
    var message = "";
    if (!username.value.trim() || !password.value.trim() || !confirmPassword.value.trim())
        message = `Không được để trống`;
    else if (username.value.trim().length < 8)
        message = `Tên đăng nhập ít nhất 8 ký tự`;
    else if (password.value.trim() != confirmPassword.value.trim())
        message = "Mật khẩu không trùng khớp";
    else {
        form1.style.left = "-550px";
        form2.style.left = "0px";
        progress.style.width = `${progress_col * 2}px`;
    }

    if (message) {
        errorText[0].style.display = 'block';
        errorText[0].innerText = message
    }
}
back1.onclick = function () {
    form1.style.left = "0px";
    form2.style.left = "550px";
    progress.style.width = `${progress_col}px`
}
next2.onclick = function () {
    form2.style.left = "-550px";
    form3.style.left = "0px";
    progress.style.width = `${progress_col * 3}px`;
}
back2.onclick = function () {
    form2.style.left = "0px";
    form3.style.left = "550px";
    progress.style.width = `${progress_col * 2}px`
}

registerForm.addEventListener("submit", function (e) {
    const first_name = document.querySelector('input[name="first_name"]');
    const last_name = document.querySelector('input[name="last_name"]');
    const phoneNumber = document.querySelector('input[name="phone_number"]');
    var message = "";
    //Check rỗng
    if (!first_name.value.trim() || !last_name.value.trim() || !phoneNumber.value.trim()) {
        message = `Không được để trống`;
    } else if (!/^\d{9,11}$/.test(phoneNumber.value)) {
        message = `Số điện thoại không hợp lệ`;
    }

    if (message) {
        e.preventDefault();
        console.log("abc");
        errorText[1].style.display = 'block';
        errorText[1].innerText = message;
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const flash = document.getElementById("flash-msg");

    if (!flash) return;

    // Thêm class fade-out
    flash.classList.add("fade-out");

    // 1.5s đầu: làm mờ
    setTimeout(() => {
        flash.classList.add("hidden");
    }, 2000);

    // Nếu là đăng ký thành công thì 3s sau redirect
    if (flash.innerText.includes("Đăng ký thành công")) {
        setTimeout(() => {
            window.location.href = "/login";
        }, 3000);
    }
});

function togglePassword(btn) {
    const input = btn.closest('div').querySelector('.password-input');
    input.type = input.type === 'password' ? 'text' : 'password';
}

