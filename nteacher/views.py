from django.shortcuts import render,redirect
from django.db.models import Count,Q
from .models import Exam,Question,Result,MyAdmin
from django.contrib import messages
from django.core import serializers
import json
import datetime,time
import pytz
from plyer import notification
from functools import reduce
# auth
from admins.decorators import admin_required

@admin_required
def helpingHome(request,ID,exam):
    try:
        Time = Exam.objects.filter(id = ID).values('TotalTime')[0]['TotalTime']
        Exam.objects.filter(id = ID).update(Started=True)
        notification.notify(
            title="Exam started!",
            ticker="College Tests",
            message = exam+" has started at "+str(datetime.datetime.now().strftime('%d %b %Y - %I:%M %p'))+" which ends in "+str(Time)+" minutes",
            timeout = 1)
        
        if Exam.objects.filter(id = ID).values('Started')[0]['Started']:
            dateconduct = Exam.objects.filter(id=ID).values('DateOfExamConducted')[0]['DateOfExamConducted']
            _afterTime = dateconduct + datetime.timedelta(minutes=Time)
            if _afterTime <= datetime.datetime.now(tz=pytz.UTC):
                _afterTime = datetime.datetime.now(tz=pytz.UTC) + datetime.timedelta(minutes=Time)
            while(datetime.datetime.now(tz=pytz.UTC) < _afterTime):
                if Exam.objects.filter(id=ID).count() and Exam.objects.filter(id=ID).values('Started')[0]['Started']:
                    time.sleep(5)
                    pass
                else:
                    break
            if datetime.datetime.now(tz=pytz.UTC) >= _afterTime and Exam.objects.filter(id = ID).values('Started')[0]['Started']:
                Exam.objects.filter(id=ID).update(Completed=True,Started=False)
                if Exam.objects.filter(id=ID).values('Completed')[0]['Completed']:
                    notification.notify(
                        title="Exam Completed!",
                        ticker="College Tests",
                        message = exam+" has Completed Now! ",
                        timeout = 1)
    except Exception as e:
        pass

@admin_required
def Home(request):
    try:
        subjects = json.dumps({'subject':request.user.my_admin.Subject}) 
        _subject_ = str(request.user.my_admin.Subject)
    except:
        subjects = json.dumps({'subject':'none'}) 
        _subject_ = None
    try:
        
        if request.POST:
            if 'ok' in request.POST:
                _ID = request.POST.get('ok')
                _datetime = request.POST.get('dateTime')
                _datetime = datetime.datetime(*[int(v) for v in _datetime.replace('T', '-').replace(':', '-').split('-')])
                # _datetime = datetime.datetime.strptime(_datetime,'%y-%b-%d %H:%M:%S')
                Exam.objects.filter(id = _ID).update(DateOfExamConducted = _datetime.astimezone(pytz.UTC))
                messages.success(request,' Date Time changed to '+str(_datetime))
            
            if 'delete' in request.POST:
                if 'subject' in request.session and 'exam' in request.session:
                    del request.session['subject'] 
                    del request.session['exam'] 
                ID = request.POST.get('delete')
                sub = Exam.objects.filter(id = ID).values('Subject')[0]['Subject']
                exam = Exam.objects.filter(id = ID).values('ExamName')[0]['ExamName']
                B_S_E = Exam.objects.filter(id = ID).values('Batch_Shift_Exam')[0]['Batch_Shift_Exam']
                Question.objects.filter(Subject__iexact=sub,Batch_Shift_Exam__iexact=B_S_E).delete()
                Result.objects.filter(Subject__iexact=sub,Batch_Shift_Exam__iexact=B_S_E).delete()
                Exam.objects.filter(Subject__iexact=sub,Batch_Shift_Exam__iexact=B_S_E).delete()
                messages.error(request,"Exam named "+sub+" "+exam+" is deleted!",extra_tags='deleted')

            ID = request.POST.get('id')
            if 'start' in request.POST:
                if 'subject' in request.session and 'exam' in request.session:
                    del request.session['subject'] 
                    del request.session['exam'] 
                exam = request.POST.get('start')
                count = Exam.objects.filter(Started=True,Completed=False).count()
                __datetime = Exam.objects.filter(id = ID).values('DateOfExamConducted')[0]['DateOfExamConducted']
                # __datetime = datetime.datetime.strptime(__datetime,'%y %b %d - %H:%M:%S')
                if __datetime >= datetime.datetime.now(tz=pytz.UTC): 
                    if count == 0:
                        helpingHome(request,ID,exam) 
                    else:
                        exam = Exam.objects.filter(Started=True,Completed=False).values('Subject','ExamName')[0]
                        messages.error(request,"Exam named "+str(exam['Subject'])+" "+str(exam['ExamName'])+" is already running!",extra_tags='startRunning')
                else:
                    messages.error(request,' The conduct Date of '+exam+' has been passed out!',extra_tags='passedout')

            if 'stop' in request.POST:
                if Exam.objects.filter(id=ID).count():
                    completed = Exam.objects.filter(id=ID).values('Completed')[0]['Completed']
                    Exam.objects.filter(id=ID).update(Completed=completed,Started=False)
                    exam = request.POST.get('stop')
                    notification.notify(
                    title="Exam Stopped!",
                    ticker="College Tests",
                    message = exam+" is Stopped Now! ",
                    timeout = 1)
                else:
                    messages.error(request,'SomeThing Went wrong!',extra_tags='somethingWentWrong')

            if 'viewQuestions' in request.POST:
                sub = Exam.objects.filter(id = ID).values('Subject')[0]['Subject']
                _exam_ = Exam.objects.filter(id = ID).values('ExamName')[0]['ExamName']
                _Questions = Question.objects.filter(Subject__iexact = sub,ExamName__iexact = _exam_)
                request.session['subject'] = sub
                request.session['exam'] = _exam_
                return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})
            
            if 'SUB' in request.POST:
                subs = request.POST.get('sub')
                MyAdmin(user = request.user.admin_profile.user,Subject = subs).save()
                subjects = subs
                _subject_ = subs
                messages.success(request,'''! Subject(s) are updated! Happy Teaching!''')
            
            if 'UPDSUB' in request.POST:
                subs = request.POST.get('sub')
                MyAdmin.objects.filter(user = request.user.admin_profile.user).update(Subject = subs)
                subjects = subs
                _subject_ = subs
                messages.success(request,'''! Subject(s) are updated!''')

        if Exam.objects.last() and _subject_: 
            _subs = helpwithsubjects(request)
            if Exam.objects.filter(_subs,Completed=True):
                _top4B_S_E = Exam.objects.filter(_subs,Completed=True).order_by('-DateOfExamConducted')[0].Batch_Shift_Exam
                _total_ques = Exam.objects.filter(_subs,Batch_Shift_Exam__iexact=_top4B_S_E).values('TotalQuestions')[0]['TotalQuestions']
                top4 = Result.objects.filter(_subs,Batch_Shift_Exam__iexact=_top4B_S_E).order_by('-Marks','Time_Taken')[0:4]
                _exam = Exam.objects.filter(_subs,Batch_Shift_Exam__iexact = _top4B_S_E).values('ExamName')[0]['ExamName']
                _started_exam = Exam.objects.filter(_subs,Started=True)
                _created_exams = Exam.objects.filter(_subs).filter(Started=False,Completed=False).order_by('-DateOfExamCreation')
                # _justcompleted_exams = Exam.objects.filter(Subject__iexact = _sub,Completed=True).order_by('-DateOfExamConducted')[:3]
                return render(request,'nteacher/home.html',{"startedExam":_started_exam,"createdExams":_created_exams,"top4":top4,"totalq":_total_ques,"exam":_exam,"subs":subjects})
            
            if Exam.objects.filter(Started=True,Completed=False):
                _started_exam = Exam.objects.filter(_subs,Started=True)
                _created_exams = Exam.objects.filter(_subs).filter(Started=False,Completed=False).order_by('-DateOfExamCreation')
                return render(request,'nteacher/home.html',{"startedExam":_started_exam,"createdExams":_created_exams,"subs":subjects})

            if Exam.objects.filter(_subs,Started=False,Completed=False):
                _created_exams = Exam.objects.filter(_subs).filter(Started=False,Completed=False).order_by('-DateOfExamCreation')    
                return render(request,'nteacher/home.html',{"createdExams":_created_exams,"subs":subjects})
        return render(request,'nteacher/home.html',{"subs":subjects}) 
    except Exception as e:
        print(e)
        messages.error(request,'Some Thing Went Wrong!',extra_tags='somethingWentWrong')
        return render(request,'nteacher/home.html',{"subs":subjects}) 
           

@admin_required
def PrepareTest(request): 
    try:
        if 'subject' in request.session and 'exam' in request.session:
            del request.session['subject'] 
            del request.session['exam']
        if request.POST:
                dateOfExam = request.POST.get('dateofexam')
                dateOfExam =  str(datetime.datetime(*[int(v) for v in dateOfExam.replace('T', '-').replace(':', '-').split('-')]))
                subject = request.POST.get('subject')
                examName = request.POST.get('examname')
                batch = request.POST.get('batch')
                semester = request.POST.get('semester')
                shift = request.POST.get('shift')
                batch_shift_exam = str(batch) + "_" + str(shift) + "_" + str(examName) 
                totalQuestions = request.POST.get('totalquestion')
                totalTime = request.POST.get('totaltime')
                dateofconduct = datetime.datetime.strptime(dateOfExam,'%Y-%m-%d %H:%M:%S') - datetime.timedelta(hours=5,minutes=30)
                
                request.session['totalQuestions'] = int(totalQuestions) 
                request.session['startTotalQuestionCount'] = 1

                b_s_e = Exam.objects.values('Batch_Shift_Exam')
                for i in b_s_e:
                    if batch_shift_exam.lower() == i['Batch_Shift_Exam'].lower():
                        Exam.objects.filter(Batch_Shift_Exam__iexact=i['Batch_Shift_Exam']).update(DateOfExamCreation = datetime.date.today() ,ExamName = examName , Subject = subject,Batch = batch,Semester = semester,
                            Shift = shift,Batch_Shift_Exam = batch_shift_exam,TotalQuestions = totalQuestions ,
                            TotalTime = totalTime,DateOfExamConducted = dateofconduct.replace(tzinfo=datetime.timezone.utc))
                        return render(request,'nteacher/prepareQuestions.html',{"subject":subject,"session":str(request.session['startTotalQuestionCount'])})

                EXAM = Exam(DateOfExamCreation = datetime.date.today() ,ExamName = examName , Subject = subject,Batch = batch,Semester = semester,
                    Shift = shift,Batch_Shift_Exam = batch_shift_exam,TotalQuestions = totalQuestions ,
                    TotalTime = totalTime,DateOfExamConducted = dateofconduct.replace(tzinfo=datetime.timezone.utc))
                EXAM.save()
                
                if Exam.objects.last():
                    subject = Exam.objects.last().Subject
                    return render(request,'nteacher/prepareQuestions.html',{"subject":subject,"session":str(request.session['startTotalQuestionCount'])})
        if request.user.my_admin.Subject.lower() == "all":
            subs = adminsubjects()
            sems = ['1','2','3','4','5','6']
        else:
            subs = request.user.my_admin.Subject.split()  
            subs = subs if subs else None
            sems = request.user.admin_profile.teach_semesters.split()    
        if Exam.objects.filter(helpwithsubjects(request)):
                dj_data = Exam.objects.filter(helpwithsubjects(request)).only('ExamName','Subject')
                # js_data = json.dumps(dj_data)
                js_data = serializers.serialize('json', dj_data,fields=('ExamName','Subject'))
                return render(request , 'nteacher/prepareTest.html',{"Tests":js_data,"sub":subs,"sem":sems})
        return render(request,'nteacher/prepareTest.html',{"Tests":"none","sub":subs,"sem":sems})
    except Exception as e:
        messages.error(request,'Some Thing Went Wrong!',extra_tags='somethingWentWrong')
        return render(request,'nteacher/prepareTest.html',{"Tests":"none"})
    
@admin_required
def Questions(request):
    if request.session['totalQuestions'] > 0:
        subject = Exam.objects.last().Subject
        examname = Exam.objects.last().ExamName
        batch = Exam.objects.last().Batch
        shift = Exam.objects.last().Shift
        semester = Exam.objects.last().Semester
        batch_shift_exam = Exam.objects.last().Batch_Shift_Exam
        if request.POST:
            if 'mcq_submit' in request.POST:
                try:
                    question = request.POST.get('question')
                    typeofQuestion = "MCQ"
                    option1 = request.POST.get('option1')
                    option2 = request.POST.get('option2')
                    option3 = request.POST.get('option3')
                    option4 = request.POST.get('option4')
                    answer = request.POST.get('ChooseCorrectone')
                    QUESTION  = Question(Question = question,Question_Type = typeofQuestion, Option_1 = option1 ,Option_2 = option2, Option_3= option3 , Option_4= option4 ,Answer = answer,
                                        Subject = subject,ExamName= examname ,Batch = batch,Semester = semester,Shift = shift,Batch_Shift_Exam = batch_shift_exam)
                    QUESTION.save()
                except Exception as e:
                    pass
            if 'fib_submit' in request.POST:
                try:
                    question = request.POST.get('question')
                    typeofQuestion = "FIB"
                    option1 = "-"
                    option2 = "-"
                    option3 = "-"
                    option4 = "-"
                    answer = request.POST.get('blank')
                    QUESTION  = Question(Question = question,Question_Type = typeofQuestion, Option_1 = option1 ,Option_2 = option2, Option_3= option3 , Option_4= option4 ,Answer = answer,
                                        Subject = subject,ExamName= examname ,Batch = batch,Semester = semester,Shift = shift,Batch_Shift_Exam = batch_shift_exam)
                    QUESTION.save()
                except Exception as e:
                    pass
            request.session['totalQuestions'] -= 1
            print(request.session['totalQuestions'],request.session['startTotalQuestionCount'])
            if request.session['totalQuestions'] > 0:
                request.session['startTotalQuestionCount'] += 1
                return render(request,'nteacher/prepareQuestions.html',{"subject":subject,"session":str(request.session['startTotalQuestionCount'])})  
            else:
                return redirect('Home')        
    elif request.session['totalQuestions'] == 0:
        request.session['totalQuestions'] = -1
        return redirect('Home') 
    return render(request , 'nteacher/prepareTest.html')

@admin_required
def Viewtesthistory(request):
    try:
        if request.POST:
            if not 'average1' in request.POST and not 'average2' in request.POST and not 'ok' in request.POST and not 'delete' in request.POST:
                ID = request.POST.get('id')
                subj = Exam.objects.filter(id = ID).values('Subject')[0]['Subject']
                examname = Exam.objects.filter(id = ID).values('ExamName')[0]['ExamName']
                B_S_E = Exam.objects.filter(id= ID).values('Batch_Shift_Exam')[0]['Batch_Shift_Exam']
            
            if 'ok' in request.POST:
                _ID = request.POST.get('ok')
                _datetime = request.POST.get('dateTime1')
                _datetime = datetime.datetime(*[int(v) for v in _datetime.replace('T', '-').replace(':', '-').split('-')])
                # _datetime = datetime.datetime.strptime(_datetime,'%y-%b-%d %H:%M:%S')
                Exam.objects.filter(id = _ID).update(DateOfExamConducted = _datetime.astimezone(pytz.UTC))
                messages.success(request,' Date Time changed to '+str(_datetime))
            
            if 'delete' in request.POST:
                if 'subject' in request.session and 'exam' in request.session:
                    del request.session['subject'] 
                    del request.session['exam']
                ID = request.POST.get('delete')
                subj = Exam.objects.filter(id = ID).values('Subject')[0]['Subject']
                examname = Exam.objects.filter(id = ID).values('ExamName')[0]['ExamName']
                B_S_E = Exam.objects.filter(id= ID).values('Batch_Shift_Exam')[0]['Batch_Shift_Exam']
                Question.objects.filter(Subject__iexact=subj,Batch_Shift_Exam__iexact=B_S_E).delete()
                Result.objects.filter(Subject__iexact=subj,Batch_Shift_Exam__iexact=B_S_E).delete()
                Exam.objects.filter(Subject__iexact=subj,Batch_Shift_Exam__iexact=B_S_E).delete()
                messages.error(request,'Exam '+subj+" "+examname+" and its data is deleted!",extra_tags='deleted')    

            if 'check' in request.POST:
                if 'subject' in request.session and 'exam' in request.session:
                    del request.session['subject'] 
                    del request.session['exam']
                results = Result.objects.filter(Subject__iexact=subj,Batch_Shift_Exam__iexact=B_S_E).order_by('-Marks','Time_Taken')
                return render(request,'nteacher/ShowResult.html',{"subject":subj,"exam":examname,"results":results})

            if 'viewQuestions' in request.POST:
                _Questions = Question.objects.filter(Subject__iexact = subj,ExamName__iexact = examname)
                request.session['subject'] = subj
                request.session['exam'] = examname
                return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})

            if 'reconduct' in request.POST:
                if 'subject' in request.session and 'exam' in request.session:
                    del request.session['subject'] 
                    del request.session['exam']
                __datetime = Exam.objects.filter(id = ID).values('DateOfExamConducted')[0]['DateOfExamConducted']
                exam = request.POST.get('reconduct')
                if __datetime >= datetime.datetime.now(tz=pytz.UTC): 
                    count = Exam.objects.filter(Started=True,Completed=True).count()
                    if not count:  
                        helpingHome(request,ID,exam)  
                    else:
                        exam = Exam.objects.filter(Started=True,Completed=True).values('Subject','ExamName')[0]
                        messages.error(request,"Exam named "+str(exam['Subject'])+" "+str(exam['ExamName'])+" is already running!",extra_tags='reconductRunning')
                else:
                    messages.error(request,' The conduct Date of '+exam+' has been passed out!',extra_tags='passedout')       
            
            if 'average1' in request.POST:
                sub = request.POST['average1']
                totalNoOfExams = Exam.objects.filter(Subject__iexact=sub,Shift=1,Completed=True).count()
                if totalNoOfExams:
                    final_results_in_dicts = {}
                    groupPins = Result.objects.filter(Shift=1,Subject__iexact = sub).values("Pin").annotate(dcount=Count("Pin"))
                    for i in groupPins:
                        final_results_in_dicts[i["Pin"]] = {}
                        final_results_in_dicts[i["Pin"]]['avg'] = 0
                        final_results_in_dicts[i["Pin"]]["exams_attempted"] = 0
                    for j in Result.objects.filter(Subject__iexact=sub,Shift=1):
                        final_results_in_dicts[j.Pin]["avg"] += j.Marks
                        final_results_in_dicts[j.Pin]["exams_attempted"] += 1
                    for k in final_results_in_dicts:
                        final_results_in_dicts[k]["avg"] /= totalNoOfExams    
                    return render(request,'nteacher/ShowResult.html',{"subject":sub,"final":final_results_in_dicts,"totalExams":totalNoOfExams})
                else:
                    messages.error(request,'No Exams Found which are conducted for Shift 1',extra_tags='notFound')
            
            if 'average2' in request.POST:
                sub = request.POST['average2']
                totalNoOfExams = Exam.objects.filter(Subject__iexact=sub,Shift=2,Completed=True).count()
                if totalNoOfExams:
                    final_results_in_dicts = {}
                    groupPins = Result.objects.filter(Shift=2,Subject__iexact = sub).values("Pin").annotate(dcount=Count("Pin"))
                    for i in groupPins:
                        final_results_in_dicts[i["Pin"]] = {}
                        final_results_in_dicts[i["Pin"]]['avg'] = 0
                        final_results_in_dicts[i["Pin"]]["exams_attempted"] = 0
                    for j in Result.objects.filter(Subject__iexact=sub,Shift=2):
                        final_results_in_dicts[j.Pin]["avg"] += j.Marks
                        final_results_in_dicts[j.Pin]["exams_attempted"] += 1
                    for k in final_results_in_dicts:
                        final_results_in_dicts[k]["avg"] /= totalNoOfExams    
                    return render(request,'nteacher/ShowResult.html',{"subject":sub,"final":final_results_in_dicts,"totalExams":totalNoOfExams})
                else:
                    messages.error(request,'No Exams Found which are conducted for Shift 2',extra_tags='notFound')
        if Exam.objects.last():
            _exams = Exam.objects.filter(helpwithsubjects(request)).filter(Completed = True).order_by('-DateOfExamConducted')[:3]
            _sem1 = Exam.objects.filter(helpwithsubjects(request),Semester__iexact=1,Completed=True)
            _sem2 = Exam.objects.filter(helpwithsubjects(request),Semester__iexact=2,Completed=True)
            _sem3 = Exam.objects.filter(helpwithsubjects(request),Semester__iexact=3,Completed=True)
            _sem4 = Exam.objects.filter(helpwithsubjects(request),Semester__iexact=4,Completed=True)
            _sem5 = Exam.objects.filter(helpwithsubjects(request),Semester__iexact=5,Completed=True)
            _sem6 = Exam.objects.filter(helpwithsubjects(request),Semester__iexact=6,Completed=True)
            return render(request, 'nteacher/Viewtesthistory.html',{"previouscompletedtests":list(zip(_exams,helpingTime(_exams))),
            "sem1":list(zip(_sem1,helpingTime(_sem1))),
            "sem2":list(zip(_sem2,helpingTime(_sem2))),
            "sem3":list(zip(_sem3,helpingTime(_sem3))),
            "sem4":list(zip(_sem4,helpingTime(_sem4))),
            "sem5":list(zip(_sem5,helpingTime(_sem5))),
            "sem6":list(zip(_sem6,helpingTime(_sem6))),
            "subs":request.user.my_admin.Subject.split() if request.user.my_admin.Subject.lower() != "all" else adminsubjects()})
        return render(request,'nteacher/Viewtesthistory.html')
    except Exception as e:
        messages.error(request,'Some Thing Went Wrong!',extra_tags='somethingWentWrong')
        return render(request,'nteacher/Viewtesthistory.html')
    
@admin_required
def ShowResult(request):
    return render(request,'nteacher/ShowResult.html')

@admin_required
def previewQuestions(request):
    try:
        changed = False
        _subject = Exam.objects.last().Subject
        _examname = Exam.objects.last().ExamName
        _Questions = Question.objects.filter(Subject__iexact = _subject,ExamName__iexact = _examname)
        if request.POST:
            if 'subject' in request.session and 'exam' in request.session:
                _subject = request.session['subject']
                _examname = request.session['exam']
                _Questions = Question.objects.filter(Subject__iexact = _subject,ExamName__iexact = _examname)
            if '_save' in request.POST:
                try:
                    ID = request.POST.get('id')
                    question = request.POST.get('question')
                    option1 = request.POST.get('input_radio_text_1')
                    option2 = request.POST.get('input_radio_text_2')
                    option3 = request.POST.get('input_radio_text_3')
                    option4 = request.POST.get('input_radio_text_4')
                    answer = request.POST.get('Option_radio_'+ID)

                    qu = Question.objects.filter(id = ID)
                    for q in qu: 
                        if q.Question != question:
                            changed = True
                            break
                        elif q.Option_1 != option1:
                            changed = True
                            break
                        elif q.Option_2 != option2:
                            changed = True
                            break
                        elif q.Option_3 != option3:
                            changed = True
                            break
                        elif q.Option_4 != option4:
                            changed = True
                            break
                    if changed:
                        Question.objects.filter(id = ID).update(Question = question, Option_1 = option1 ,Option_2 = option2, Option_3= option3 , Option_4= option4 ,Answer = answer)
                        _Questions = Question.objects.filter(Subject__iexact = _subject).filter(ExamName__iexact = _examname)
                        messages.success(request, 'A Question got Updated!')
                    return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})
                except Exception as e:
                    messages.error(request,'SomeThing Went Wrong! May be You didn\'t Save the Question correctly. ')
                    return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})
            if '_save1' in request.POST:
                try:
                    ID = request.POST.get('id')
                    question = request.POST.get('question')
                    answer = request.POST.get('Answer_blank')
                    Question.objects.filter(id = ID).update(Question = question,Answer = answer)
                    _Questions = Question.objects.filter(Subject__iexact = _subject).filter(ExamName__iexact = _examname)
                    messages.success(request, 'A Question got Updated!')
                    return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})
                except Exception as e:
                    messages.error(request,'SomeThing Went Wrong! May be You didn\'t Save the Question correctly. ')
                    return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})
            if '_delete' in request.POST:
                ID = request.POST.get('id')
                Question.objects.filter(id = ID).delete()
                messages.info(request, 'A Question deleted Sucessfully.')
        return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})
    except Exception as e:
        _subject = Exam.objects.last().Subject
        _examname = Exam.objects.last().ExamName
        _Questions = Question.objects.filter(Subject__iexact = _subject,ExamName__iexact = _examname)
        return render(request,'nteacher/previewQuestions.html',{"Questions":_Questions})

def helpingTime(exam):
    examDates = []
    for i in exam.values('DateOfExamConducted'):
        examDates.append(dict({'time':i['DateOfExamConducted'].astimezone(tz=None).strftime('%d %b %Y - %I:%M %p')}))
    return examDates    

def helpwithsubjects(request):
    try:
        if request.user.my_admin.Subject.lower() == "all":
            subj = adminsubjects()
        else: 
            subj = request.user.my_admin.Subject.split()
        q_list = map(lambda n: Q(Subject__iexact=n), subj)
        q_list = reduce(lambda a, b: a | b, q_list)
        return q_list
    except:
        return None

def adminsubjects():
    subs = ""
    for s in MyAdmin.objects.values_list('Subject'):
        for i in s:
            if not "all".lower() == i.lower():  
                subs+=str(i)+" "
    subs = subs.split()
    return subs