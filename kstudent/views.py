from django.shortcuts import redirect, render
import datetime
from nteacher.models import Exam, Question, Result
import random
import pytz
from plyer import notification
from students.decorators import student_required
from django.contrib.auth import authenticate, get_user_model, logout
from django.http import HttpResponseRedirect

User = get_user_model()

# _pin = "18001-CM-045"
# _shift = 1
pin_ExamDetails = {}


@student_required
def start(request):
    # _shift = request.user.student_profile.current_shift
    # _pin = str(request.user)

    notification.notify(
            title = f"{Exam.objects.filter(Started=True)[0].Subject}-{Exam.objects.filter(Started=True)[0].ExamName}",
            message = "Exam has started. Attempt Soon!",
            timeout = 3
    )

    if Exam.objects.filter(Started=True)[0]:
        if (Exam.objects.filter(Started=True)[0].Started == True and Exam.objects.filter(Started=True)[0].Completed == False) or (Exam.objects.filter(Started=True)[0].Started == Exam.objects.filter(Started=True)[0].Completed == True):
            return render(request, "kstudent/index_student.html", {"current_object": Exam.objects.filter(Started=True)[0]})
        else:
            return render(request, "kstudent/index_student.html", {"current_object": Exam.objects.filter(Started=True)[0]})
    elif Exam.objects.filter(Started=True)[0] == []:
        return render(request, "kstudent/index_student.html", {"current_object": Exam.objects.filter(Started=True)[0]})


@student_required
def displayResultsHistory(request):
    # _shift = request.user.student_profile.current_shift
    _pin = str(request.user)

    sem = request.GET["semester"]
    details = {"marksDetails" : {}}
    if sem == "all":
        r = list(dict.fromkeys([i.Subject for i in Result.objects.filter(Pin=_pin).order_by("-Subject")]))
    elif sem in "123456":
        r = list(dict.fromkeys([i.Subject for i in Result.objects.filter(Pin=_pin, Semester=int(sem)).order_by("-Subject")]))
    else:
        details["marksDetails"] = None
        details["ErrorCode"] = 0
        return render(request, "kstudent/resultHistory.html", details)
    all_written_exam_semesters = list(dict.fromkeys([i.Semester for i in Result.objects.filter(Pin=_pin).order_by("-Subject")]))
    details["ExamWrittenSemesters"] = all_written_exam_semesters
    if len(r):
        for i in r:
            temp = Result.objects.filter(Pin=_pin, Subject=i)
            details["marksDetails"].update({i: temp})
        details["loopCounter"] = range(len(r))
        print(details)
        return render(request, "kstudent/resultHistory.html", details)
    details["marksDetails"] = None
    details["ErrorCode"] = 1
    return render(request, "kstudent/resultHistory.html", details)


@student_required
def homePage(request):
    # print("SSSSSSSSSSSSSSSSSSSSSShiftttttttt : ", request.user.student_profile.current_shift)
    # print("UuuuuuuuuuuuuuuuuuuuuuuuuuuuserNname : ", request.user)
    _shift = request.user.student_profile.current_shift
    _pin = str(request.user)

    try:
        try:
            if pin_ExamDetails[_pin].get("anyGraceTime", 0):
                print("######################Kiran#####################")
                return render(request, "kstudent/resumeExam.html")
                # return render(request, "kstudent/askAdminAuth.html")
        except Exception as temp:
            if temp == _pin:
                pass
            else:
                print(temp)
        _whether_any_exam = Exam.objects.filter(Batch_Shift_Exam__startswith=f"{_pin[0:2]}_{_shift}", Started=True)[0]
        print(_whether_any_exam.ExamName)
        alreadyWritten = Result.objects.filter(Batch_Shift_Exam=f"{_pin[0:2]}_{_shift}_{_whether_any_exam.ExamName}").count()
        print(alreadyWritten)

        if _whether_any_exam and (not alreadyWritten):
            pin_ExamDetails[_pin] = {}
            pin_ExamDetails[_pin]["Batch_Shift_Exam"] = _whether_any_exam.Batch_Shift_Exam
            pin_ExamDetails[_pin]["Subject"] = _whether_any_exam.Subject
            pin_ExamDetails[_pin]["Semester"] = _whether_any_exam.Semester
            pin_ExamDetails[_pin]["examStartTime"] = _whether_any_exam.DateOfExamConducted

            UTC_TIME = datetime.datetime.now(tz=pytz.UTC)
            examDateTime = _whether_any_exam.DateOfExamConducted
            diff = examDateTime - UTC_TIME
            minutes_remaining = diff.total_seconds()/60.0

            return render(request, "kstudent/homePage.html", { "message":1, "timeRemaining":minutes_remaining })
    except Exception as e:
        print(e)
    return render(request, "kstudent/homePage.html", { "message":0 })


@student_required
def newQuestionFormat(request):
    global pin_ExamDetails

    _shift = request.user.student_profile.current_shift
    _pin = str(request.user)

    try:

        Batch_Shift_Exam = f"{_pin[0:2]}_{_shift}_{Exam.objects.filter(Started=True)[0].ExamName}"
        if Result.objects.filter(Pin=_pin, Batch_Shift_Exam=Batch_Shift_Exam):
            return render(request, "kstudent/notAllowedForExam.html", {"reason": "Looks like you already wrote the Exam! Have a look at the results history...", "custom_flag" : 0})
        if pin_ExamDetails[_pin]["examStartTime"] > datetime.datetime.now(tz=pytz.UTC):
            return render(request, "kstudent/notAllowedForExam.html", {"reason": "You are here before the exam has started", "custom_flag" : 1})
        questionsList = list(Question.objects.filter(Batch_Shift_Exam=Batch_Shift_Exam))

        pin_ExamDetails[_pin]["totalNoOfQuestions"] = len(questionsList)
        pin_ExamDetails[_pin]["currentGoingQuestion"] = 1

        random.shuffle(questionsList)

        pin_ExamDetails[_pin]["questionsList"] = questionsList

        print(pin_ExamDetails)

        if Exam.objects.filter(Started=True)[0]:
            endTime = Exam.objects.filter(Started=True)[0].DateOfExamConducted + datetime.timedelta(minutes=Exam.objects.filter(Started=True)[0].TotalTime)

        pin_ExamDetails[_pin]["startTime"] = datetime.datetime.now(tz=pytz.UTC)
        examDuration = (endTime - datetime.datetime.now(tz=pytz.UTC)).total_seconds()/60.0

        if examDuration <= 0:
            return render(request, "kstudent/notAllowedForExam.html", {"reason":"Sorry the exam you are looking for is completed!"})

        return render(request, "kstudent/newQuestionFormat.html", {"question": questionsList[0], "exam_duration": examDuration, "isLastQuestion": False})
    except IndexError:
        return render(request, "kstudent/notAllowedForExam.html", {"reason": "Sorry, you are not eligible to write the exam because of your credentials!", "custom_flag" : 1})


@student_required
def performOperations(request):
    global pin_ExamDetails

    # _shift = request.user.student_profile.current_shift
    _pin = str(request.user)

    try:
        isLastQuestion = False
        if request.POST:
            qnId = request.POST.get("getId")
            pin_ExamDetails[_pin][qnId] = request.POST.get(qnId)
            pin_ExamDetails[_pin]["currentGoingQuestion"] += 1
        else:
            pin_ExamDetails[_pin]["startTime"] = datetime.datetime.now(tz=pytz.UTC)
        if pin_ExamDetails[_pin]["currentGoingQuestion"] == pin_ExamDetails[_pin]["totalNoOfQuestions"]:
            isLastQuestion = True
        if pin_ExamDetails[_pin].get("anyGraceTime", 0):
            examDuration = pin_ExamDetails[_pin]["anyGraceTime"]
        else:
            examDuration = 0
        print(pin_ExamDetails)

        return render(request, "kstudent/newQuestionFormat.html", {"question": pin_ExamDetails[_pin]["questionsList"][pin_ExamDetails[_pin]["currentGoingQuestion"]-1], "isLastQuestion": isLastQuestion, "exam_duration": examDuration})
    except IndexError:
        return render(request, "kstudent/notAllowedForExam.html", {"reason": "Looks like you already wrote the Exam! Have a look at the results history...", "custom_flag" : 0})


@student_required
def showingMarks(request):
    global pin_ExamDetails

    _shift = request.user.student_profile.current_shift
    _pin = str(request.user)

    pin_ExamDetails[_pin].pop("anyGraceTime", 0)
    timeTakenForCompletion = pin_ExamDetails[_pin].get("durationOfExamWritten", 0) + (datetime.datetime.now(tz=pytz.UTC) - pin_ExamDetails[_pin]["startTime"]).total_seconds()/60.0

    if request.POST:
        qnId = request.POST.get("getId")
        pin_ExamDetails[_pin][qnId] = request.POST.get(qnId)
        pin_ExamDetails[_pin]["currentGoingQuestion"] += 1
    l = []
    marks = 0
    questionsList = list(Question.objects.filter(Batch_Shift_Exam=pin_ExamDetails[_pin]["Batch_Shift_Exam"], Subject=pin_ExamDetails[_pin]["Subject"]))
    for exactAnswers in questionsList:
        isNone = pin_ExamDetails[_pin].get(str(exactAnswers.id), None)
        l.append(isNone)
        if isNone != None and pin_ExamDetails[_pin][str(exactAnswers.id)].lower() == exactAnswers.Answer.lower():
            marks += 1

    zipped_list = zip(questionsList, l)

    if Result.objects.filter(Batch_Shift_Exam=pin_ExamDetails[_pin]["Batch_Shift_Exam"], Pin=_pin).count() == 1:
        pass
    else:
        r = Result(Pin=_pin, Marks=marks, Subject=pin_ExamDetails[_pin]["Subject"], Shift=_shift, Semester=pin_ExamDetails[_pin]["Semester"], Batch_Shift_Exam=pin_ExamDetails[_pin]["Batch_Shift_Exam"], Time_Taken=round(timeTakenForCompletion,2))
        r.save()

    return render(request, "kstudent/displayMarks.html", {"details":{"attained_marks": marks, "total_marks":pin_ExamDetails[_pin]["totalNoOfQuestions"]}, "zip_list":zipped_list})


@student_required
def delayExam(request):
    global pin_ExamDetails

    # _shift = request.user.student_profile.current_shift
    _pin = str(request.user)

    pin_ExamDetails[_pin]["anyGraceTime"] = float(request.GET["gracePeriod"])
    pin_ExamDetails[_pin]["durationOfExamWritten"] = pin_ExamDetails[_pin].get("durationOfExamWritten", 0) + (datetime.datetime.now(tz=pytz.UTC) - pin_ExamDetails[_pin]["startTime"]).total_seconds()/60.0
    print("At Delay Exam : ", pin_ExamDetails[_pin])
    # Logout
    logout(request)
    # return render(request, "kstudent/notAllowedForExam.html", {"reason": "Your exam has been paused take new PC and continue it.", "custom_flag": 1})
    # return redirect('')
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('users-login')


@student_required
def exam_pause_auth(request):
    if request.POST:
        uName = request.POST["username"]
        passWord = request.POST["password"]
        user = authenticate(username=uName, password=passWord)
        if user is not None:
            try:
                c_user = User.objects.filter(id=user.id)[0]
                if c_user.is_active and c_user.is_superuser:
                    # After authentication
                    # return render(request, "kstudent/resumeExam.html")
                    return redirect("performOperations")
                    # pass
                else:
                    # If auth fails
                    print("Auth failed - 1")
                    # pass
            except Exception as e:
                print("Auth with admin failed due to : ", e)
        else:
            # If auth fails
            print("Auth failed - 2")
            # pass
    return render(request, "kstudent/adminAuth.html")