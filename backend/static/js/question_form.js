document.addEventListener("DOMContentLoaded", function () {
    const submitButtons = document.querySelectorAll("input[type='submit'], button[type='submit']");
    const userAnswer = document.getElementById("user_answer");
    const charCount = document.getElementById("charCount");
    const timerElement = document.getElementById("timer");
    const progressContainer = document.querySelector(".progress");
    const cancelButton = document.querySelector("button[name='cancel']");

    // 文字数カウント機能
    if (userAnswer && charCount) {
        userAnswer.addEventListener("input", function () {
            let length = this.value.length;
            charCount.textContent = `現在の文字数: ${length}文字`;
        });
    } else {
        console.error("user_answer または charCount が見つからない！");
    }

    submitButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            if (button.name !== "cancel") {
                userAnswer.setAttribute("required", "true"); // 必須入力
            } else {
                userAnswer.removeAttribute("required"); // 中断なら必須解除
            }
        });
    });

    if (cancelButton) {
        cancelButton.addEventListener("click", function (event) {
            let confirmExit = confirm("本当に試験を中断しますか？\nこの操作は取り消せません。");
            if (!confirmExit) {
                event.preventDefault();
            }
        });
    }

    // 進捗バーの設定
    let totalTime = 120;
    let timeLeft = totalTime;
    let blocks = 10;
    let timePerBlock = totalTime / blocks;

    progressContainer.innerHTML = "";
    let blockElements = [];

    for (let i = 0; i < blocks; i++) {
        let block = document.createElement("div");
        block.classList.add("progress-block", "bg-light");
        progressContainer.appendChild(block);
        blockElements.push(block);
    }

    function updateTimer() {
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        if (timerElement) {
            timerElement.innerText = `残り時間: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }

        let blocksFilled = Math.floor((totalTime - timeLeft) / timePerBlock);

        for (let i = 0; i < blocksFilled; i++) {
            if (blockElements[i]) {
                blockElements[i].classList.remove("bg-light");
                if (i < 5) {
                    blockElements[i].classList.add("bg-success"); // 緑（0～50%）
                } else if (i < 8) {
                    blockElements[i].classList.add("bg-warning"); // オレンジ（51～80%）
                } else {
                    blockElements[i].classList.add("bg-danger"); // 赤（81～100%）
                }
            }
        }

        if (timeLeft > 0) {
            timeLeft--;
            setTimeout(updateTimer, 1000);
        } else {
            alert("試験時間が終了しました！");
        }
    }

    // タイマーを開始
    updateTimer();
});
