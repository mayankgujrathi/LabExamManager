const display = document.querySelector("#time")

function customOnloadRemainingTimeForExamStartFuncTrigger(param) {
    if (sessionStorage.getItem("remainingTimeForExamStart")) {
        startTimer(sessionStorage.getItem("remainingTimeForExamStart"), display)
    }
    else {
        triggerCountdownRemainingTimeForExamStartFunc(param);
    }
}

function startTimer(endAt, display) {
    let minutes, seconds, timeDifference;
    let startInterval = setInterval(function () {

        timeDifference = endAt - new Date().getTime();

        minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
        seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

        if (timeDifference <= 0) {
            sessionStorage.removeItem("remainingTimeForExamStart")
            clearInterval(startInterval);
            location.href = "./acknowledge";
        }
        else {
            display.textContent = (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);
        }

    }, 1000);
}

const triggerCountdownRemainingTimeForExamStartFunc = (dynamicDuration) => {
    let duration = dynamicDuration;
    let currentDate = new Date().getTime();
    let endTime = new Date(currentDate + duration * 60000).getTime();
    sessionStorage.setItem("remainingTimeForExamStart", endTime)
    startTimer(sessionStorage.getItem("remainingTimeForExamStart"), display)
}