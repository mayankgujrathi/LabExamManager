const display = document.querySelector("#time")
const answersClickBtn = document.querySelector("#showAnswerOnClick");
const answersPresentDiv = document.querySelector("#displayAnswersCard");

answersClickBtn.addEventListener("click", () => {
    answersPresentDiv.style.display = "block";
})

function startTimer(endAt, display) {
    let minutes, seconds, timeDifference;
    let startInterval = setInterval(function () {

        timeDifference = endAt - new Date().getTime();

        minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
        seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

        if (timeDifference <= 0) {
            sessionStorage.removeItem("examEndTime");
            clearInterval(startInterval);
            answersClickBtn.disabled = false;
        }
        else {
            display.textContent = (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);
        }

    }, 1000);
}

const triggerRemainingAnswerTimeCountdownFunc = () => {
    startTimer(sessionStorage.getItem("examEndTime"), display)
}