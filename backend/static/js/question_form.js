document.addEventListener("DOMContentLoaded", function () {
    const submitButtons = document.querySelectorAll("input[type='submit'], button[type='submit']");
    const cancelButton = document.getElementById("cancel-button");
    const userAnswer = document.getElementById("user_answer");

    submitButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            if (button.name !== "cancel") {
                // 🔹 通常の送信ボタンなら required を追加
                userAnswer.setAttribute("required", "true");
            } else {
                // 🔹 中断ボタンなら required を削除
                userAnswer.removeAttribute("required");
            }
        });
    });
});
