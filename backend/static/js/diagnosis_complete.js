document.addEventListener('DOMContentLoaded', function() {
    var progressBar = document.getElementById('progress-bar');
    var percentageText = document.getElementById('circle-percentage');
    var circumference = 440;  // 円周 (2πr: 半径70なので、440pxが円周)
    var width = 0;

    // セッションIDはdata属性から取得する
    var sessionId = document.getElementById('progress-container').getAttribute('data-session-id'); 
    var resultUrl = "/socialinsight/result_scores/" + sessionId;

    var interval = setInterval(function() {
        if (width >= 100) {
            clearInterval(interval);
            // アニメーションが終わったら結果ページへリダイレクト
            window.location.href = resultUrl;
        } else {
            width += 10;
            var offset = circumference - (width / 100) * circumference;  // プログレスの計算
            progressBar.style.strokeDashoffset = offset;
            percentageText.textContent = width + '%';
        }
    }, 500); // 0.5秒ごとに進行
});
