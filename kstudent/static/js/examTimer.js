const display = document.querySelector("#time")

function customOnloadTrigger(param) {
    if (sessionStorage.getItem("shallLoad")) {
        sessionStorage.removeItem("shallLoad")
        location.reload();
    }
    if (sessionStorage.getItem("examEndTime")) {
        startTimer(sessionStorage.getItem("examEndTime"), display)
    }
    else {
        triggerCountdownFunc(param);
    }
}

function startTimer(endAt, display) {
    let minutes, seconds, timeDifference;
    let startInterval = setInterval(function () {

        timeDifference = endAt - new Date().getTime();

        minutes = Math.floor((timeDifference % (1000 * 60 * 60)) / (1000 * 60));
        seconds = Math.floor((timeDifference % (1000 * 60)) / 1000);

        if (timeDifference <= 0) {
            clearInterval(startInterval);
            sessionStorage.removeItem("examEndTime")
            // document.questionForm.submit();
            location.href = "../showingMarks/";
        }
        else {
            display.textContent = (minutes < 10 ? "0" + minutes : minutes) + ":" + (seconds < 10 ? "0" + seconds : seconds);
        }

    }, 1000);
}

const triggerCountdownFunc = (dynamicDuration) => {
    let duration = dynamicDuration;
    let currentDate = new Date().getTime();
    let endTime = new Date(currentDate + duration * 60000).getTime();
    sessionStorage.setItem("examEndTime", endTime)
    startTimer(sessionStorage.getItem("examEndTime"), display)
}