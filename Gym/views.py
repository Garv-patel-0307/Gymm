import json
import secrets
from django.shortcuts import render, redirect
from .models import User, Biceps, Triceps, Forearms, Leg, Back, Chest, Shoulder, Abs
from colorama import Fore, Style, init
from django.http import HttpResponse
from django.http import JsonResponse
from datetime import date, datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .backup_utils import backup_database_to_github

Biceps_Exercises = ["preacher curl", "seated bicep curls", "Rope hammer curl"]
Triceps_Exercises = ["Over-head tricep extension", "Single arm rope pull-down", "Road/Rope pull-down"]
Forearms_Exercises = ["Forearm curl", "Reversed Forearm curl", "Forearm rotation"]
Leg_Exercises = ["Squats", "Leg Extension", "RDL", "calf Raise", "Leg-Press"]
Back_Exercises = ["Close-Grip Latpull-Down", "Latpull-Down", "Machine Rowing", "Lower back", "Single-Arm Latpull-down"]
Chest_Exercises = ["Incline Bench-press", "xBench-press", "Pec-Deck Fly", "Decline Bench-press"]
Shoulder_Exercises = ["cable lateral raise", "Rear delt fly machine", "machine shoulder press", "Shrugs"]
Abs_Exercises = ["Crunches", "Hangging leg raise"]
records = [] 
Today_exercises = []

now = datetime.now()
date1= now.date()

def parse_weight(text):
    weight_str = text[0]
    val = float(weight_str)
    return int(val) if val.is_integer() else val

def login(request):
    if request.method == "POST":
        usname = request.POST['Username']
        pswd = request.POST['password']

        try:
            user = User.objects.get(username=usname)
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Invalid Username"})

        if user.password == pswd:
            request.session['user_id'] = user.id
            return redirect('/index/')
        else:
            return render(request, "login.html", {"error":"Wrong Passwod"})
    return render(request, "login.html")

def signup(request):
    if request.method == "POST":
        image = request.FILES.get('profile_image')
        user = User(
            username = request.POST['username'],
            phone_number =  request.POST['phone'],
            email = request.POST['email'],
            password = request.POST['pswd'],
            joined_date = date1,
            img = image
        )
        user.save()
        backup_database_to_github()
        request.session['user_id'] = user.id
        return redirect("/index/")
    return render(request, "signup.html")

def get_user_id(request):
    user_id = request.session.get('user_id')
    return user_id

def current_day():
    today_get = date.today()
    today = today_get.strftime("%A")
    today = str(today)
    return today




def home(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just Logged In" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})
    return render(request, "index.html", {"User" : user})

def exercises(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just Open Exercise List" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "exercises.html", {"error": "User not found"})
    return render(request, "exercises.html", {"User" : user})




def workout(request):
    today = current_day()

    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just Start Workout" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    if today == "Monday" or today == "Thursday":
        Today_exercises.clear()
        muscle = "Biceps, Triceps & Foreamrs"
        for i in Biceps_Exercises + Triceps_Exercises + Forearms_Exercises:
            Today_exercises.append(i)
    elif today == "Tuesday" or today == "Friday":
        Today_exercises.clear()
        muscle = "Back & Legs"
        for i in Back_Exercises + Leg_Exercises:
            Today_exercises.append(i)
    elif today == "Wednesday" or today == "Saturday":
        Today_exercises.clear()
        muscle = "Chest, Shoulder & Abs"
        for i in Chest_Exercises + Shoulder_Exercises + Abs_Exercises:
            Today_exercises.append(i)
    else:
        print("Not match any.")
        context = {
            "emoji": "😴",
            "motivated": "Rest Day! Recovery Is Part of the Grind! 🛌💪",
            "level": "Recovery Mode Activated! 🔋🚀",
            "progress": "You put in the work. Now let your body recover, rebuild, and come back stronger! 💪🔥",
            "home": "no",
            "User": user
        }

        return render(request, "404.html", context)

    if request.method == "POST":
        username = user.username
        data = json.loads(request.body)
        workout_data = data.get("workout", [])
        for exercise in workout_data:
            exercise_name = exercise["exercise_name"]
            set_1_value = f"0 kg × 0 Reps"
            set_2_value = f"0 kg × 0 Reps"

            for set_data in exercise["sets"]:
                set_number = set_data["set_number"]
                weight = set_data["weight"]
                reps = set_data["reps"]


                if set_number == 1:
                    set_1_value = f"{weight} kg × {reps} Reps"
                elif set_number == 2:
                    set_2_value = f"{weight} kg × {reps} Reps"

                # print(f"{exercise_name} = Set{set_number} = {weight} kg × {reps} Reps")

            if exercise_name in Biceps_Exercises:
                workout = Biceps(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Triceps_Exercises:
                workout = Triceps(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Forearms_Exercises:
                workout = Forearms(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Leg_Exercises:
                workout = Leg(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Back_Exercises:
                workout = Back(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Chest_Exercises:
                workout = Chest(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Shoulder_Exercises:
                workout = Shoulder(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

            elif exercise_name in Abs_Exercises:
                workout = Abs(
                    username = username,
                    exercise = exercise_name,
                    date = date1,
                    day = today,
                    set_1 = set_1_value,
                    set_2 = set_2_value
                )
                workout.save()

        backup_database_to_github()

        models_list_Biceps = [Biceps, Triceps, Forearms]
        models_list_Back = [Back, Leg]
        models_list_Chest = [Chest, Shoulder, Abs]
        email_data = []
        date_for = date1.strftime("%d-%m-%Y")

        if today == "Monday" or today == "Thursday":
            emoji = "💪"
            for model in models_list_Biceps:
                records = model.objects.filter(username=user.username, date=date1)
                email_data.extend(records)
        
        elif today == "Tuesday" or today == "Friday":
            emoji = "🦵"
            for model in models_list_Back:
                records = model.objects.filter(username=user.username, date=date1)
                email_data.extend(records)

        elif today == "Wednesday" or today == "Saturday":
            emoji = "🎯"
            for model in models_list_Chest:
                records = model.objects.filter(username=user.username, date=date1)
                email_data.extend(records)

        # Build the exercise block
        exercise_lines = []
        for item in email_data:
            exercise_lines.append(
                f" { emoji } {item.exercise}\n"
                f"     • Set 1: {item.set_1}\n"
                f"     • Set 2: {item.set_2}"
            )

        # Fallback text if no workouts were logged for that date
        exercise_summary = (
            "\n\n".join(exercise_lines)
            if exercise_lines
            else "No exercises recorded for today."
        )
            
        subject = f"🔥 Workout Logged: {muscle} ({date_for})"
        body = f"""Hi {user.username},

Great work showing up and putting in the sweat today! Consistency is where the magic happens.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WORKOUT SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 Day & Date:    {today}, {date_for}
🎯 Focus Group:   {muscle}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{exercise_summary}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECOVERY CHECKLIST:
• Hydrate: Drink 500ml+ water over the next hour.
• Refuel: Aim for 20-30g of quality protein.
• Rest: Get 7-8 hours of sleep tonight.

See you at the next session!
Your Gym Bros
"""

        try:
            print("Email send.")
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            messages.success(request, 'Gym Progress Report has been sent to your email.')
            # return redirect('verify_otp')
        except Exception as e:
            messages.error(request, f'Failed to send email: {e}')

        return JsonResponse({
            "status": "success",
            "message": "Workout saved successfully",
        })

    return render(request, "workout.html", {"exercises" : Today_exercises, "Muscle_group": muscle, "User": user})

def history(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just Open History" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})\

    biceps_record = Biceps.objects.filter(username=user.username)
    tricpes_record = Triceps.objects.filter(username=user.username)
    forearms_record = Forearms.objects.filter(username=user.username)
    back_records = Back.objects.filter(username=user.username)
    leg_records = Leg.objects.filter(username=user.username)
    chest_record = Chest.objects.filter(username=user.username)
    shoulder_record = Shoulder.objects.filter(username=user.username)
    abs_record = Abs.objects.filter(username=user.username)
    
    for record in biceps_record:
        record.muscle_group = "Biceps"
        records.append(record)

    for record in tricpes_record:
        record.muscle_group = "Triceps"
        records.append(record)

    for record in forearms_record:
        record.muscle_group = "Forearms"
        records.append(record)

    for record in back_records: 
        record.muscle_group = "Back" 
        records.append(record)

    for record in leg_records:
        record.muscle_group = "Leg" 
        records.append(record)

    for record in chest_record:
        record.muscle_group = "Chest"
        records.append(record)

    for record in shoulder_record:
        record.muscle_group = "Shoulder"
        records.append(record)

    for record in abs_record:
        record.muscle_group = "Abs"
        records.append(record)

    records.sort(
        key=lambda x: str(getattr(x, 'date', '') or ''), 
        reverse=True
    )
    
    context = { 
        "User": user, 
        "records": records
    }
    
    return render(request, "history.html", context)

def Biceps_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Biceps Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Biceps_Data = Biceps.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Biceps_Data,
        "User": user
    }
    return render(request, "Biceps.html", context)
    
def Triceps_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Triceps Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Triceps_Data = Triceps.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Triceps_Data,
        "User": user
    }
    return render(request, "Triceps.html", context)
    
def Forearms_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Forearms Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Forearms_Data = Forearms.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Forearms_Data,
        "User": user
    }
    return render(request, "Forearms.html", context)
    
def Leg_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Leg Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Leg_Data = Leg.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Leg_Data,
        "User": user
    }
    return render(request, "Leg.html", context)
    
def Back_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Back Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Back_Data = Back.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Back_Data,
        "User": user
    }
    return render(request, "Back.html", context)
    
def Chest_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Chest Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Chest_Data = Chest.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Chest_Data,
        "User": user
    }
    return render(request, "Chest.html", context)
    
def Shoulder_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Shoulder Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Shoulder_Data = Shoulder.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Shoulder_Data,
        "User": user
    }
    return render(request, "Shoulder.html", context)
    
def Abs_(request):
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just See Abs Records" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    Abs_Data = Abs.objects.filter(username = user.username).order_by('-date', '-id')
    context = {
        "records": Abs_Data,
        "User": user
    }
    return render(request, "Abs.html", context)

def profile(request):
    records.clear()
    user_id = get_user_id(request)
    try:
        user = User.objects.get(id=user_id)
        print("\033[38;2;182;255;0m" + f"{user.username} Just Open Profile" + "\033[0m")
    except User.DoesNotExist:
        return render(request, "index.html", {"error": "User not found"})

    try:
        Biceps_PR_set_1 = Biceps.objects.filter(username = user.username).order_by('-set_1').first()
        Biceps_PR_set_2 = Biceps.objects.filter(username = user.username).order_by('-set_2').first()
        set1_spilt = Biceps_PR_set_1.set_1.split()
        set2_split = Biceps_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])

        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Biceps_PR = Biceps_PR_set_1
        else: 
            weight = weight2 
            reps = reps2 
            Biceps_PR = Biceps_PR_set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 1,
            "muscle": "Bicep",
            "record": Biceps_PR
        })
    except AttributeError:
        pass
    except (IndexError, ValueError, ZeroDivisionError):
        pass

    try:
        Triceps_PR_set_1 = Triceps.objects.filter(username = user.username).order_by('-set_1').first()
        Triceps_PR_set_2 = Triceps.objects.filter(username = user.username).order_by('-set_2').first() 
        set1_spilt = Triceps_PR_set_1.set_1.split()
        set2_split = Triceps_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])

        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Triceps_PR = Triceps_PR_set_1 
        else: 
            weight = weight2 
            reps = reps2 
            Triceps_PR = Triceps_PR_set_2
        records.append({
            "symbol": "df",
            "number": 2,
            "weight": weight,
            "reps": reps,
            "record": Triceps_PR
        })
    except AttributeError:
        pass
    except (IndexError, ValueError, ZeroDivisionError):
        pass

    try:
        Forearms_PR_set_1 = Forearms.objects.filter(username = user.username).order_by('-set_1').first()
        Forearms_PR_set_2 = Forearms.objects.filter(username = user.username).order_by('-set_2').first()
        set1_spilt = Forearms_PR_set_1.set_1.split()
        set2_split = Forearms_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])

        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Forearms_PR = Forearms_PR_set_1
        else: 
            weight = weight2 
            reps = reps2 
            Forearms_PR = Forearms_PR_set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 3,
            "muscle": "Forearms",
            "record": Forearms_PR
        })
    except AttributeError:
        pass
    except (IndexError, ValueError, ZeroDivisionError):
        pass
        
    try:
        Leg_PR_set_1 = Leg.objects.filter(username = user.username).order_by('-set_1').first()
        Leg_PR_set_2 = Leg.objects.filter(username = user.username).order_by('-set_2').first()
        set1_spilt = Leg_PR_set_1.set_1.split()
        set2_split = Leg_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])

        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Leg_PR = Leg_PR_set_1
        else: 
            weight = weight2 
            reps = reps2 
            Leg_PR = Leg_PR_set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 4,
            "muscle": "Leg",
            "record": Leg_PR
        })
    except AttributeError:
        pass
    except (IndexError, ValueError, ZeroDivisionError):
        pass

    try:
        Back_PR_set_1 = Back.objects.filter(username = user.username).order_by('-set_1').first()
        Back_PR_set_2 = Back.objects.filter(username = user.username).order_by('-set_2').first()
        set1_spilt = Back_PR_set_1.set_1.split()
        set2_split = Back_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])

        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Back_PR = Back_PR_set_1
        else: 
            weight = weight2 
            reps = reps2 
            Back_PR = Back_PR_set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 5,
            "muscle": "Back",
            "record": Back_PR
        })
    except AttributeError:
        pass
    except (IndexError, ValueError, ZeroDivisionError):
        pass

    try:
        Chest_PR_set_1 = Chest.objects.filter(username = user.username).order_by('-set_1').first()
        Chest_PR_set_2 = Chest.objects.filter(username = user.username).order_by('-set_2').first()
        set1_spilt = Chest_PR_set_1.set_1.split()
        set2_split = Chest_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])

        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1
            Chest_PR = Chest_PR_set_1 
        else: 
            weight = weight2 
            reps = reps2 
            Chest_PR = Chest_PR_set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 6,
            "muscle": "Chest",
            "record": Chest_PR
        })
        
    except AttributeError:
        pass
    
    except (IndexError, ValueError, ZeroDivisionError):
        pass

    try:
        Shoulder_PR_set_1 = Shoulder.objects.filter(username = user.username).order_by('-set_1').first()
        Shoulder_PR_set_2 = Shoulder.objects.filter(username = user.username).order_by('-set_2').first()
        set1_spilt = Shoulder_PR_set_1.set_1.split()
        set2_split = Shoulder_PR_set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])
        
        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Shoulder_PR = Shoulder_PR_set_1
        else: 
            weight = weight2
            reps = reps2 
            Shoulder_PR = Shoulder_PR_set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 7,
            "muscle": "Shouler",
            "record": Shoulder_PR
        })

    except AttributeError:
        pass

    except (IndexError, ValueError, ZeroDivisionError):
        pass

    try:
        Abs_PR_Set_1 = Abs.objects.filter(username = user.username).order_by('-set_1').first()
        Abs_PR_Set_2 = Abs.objects.filter(username = user.username).order_by('-set_1').first()
        set1_spilt = Abs_PR_Set_1.set_1.split()
        set2_split = Abs_PR_Set_2.set_2.split()
        weight1 = parse_weight(set1_spilt)
        weight2 = parse_weight(set2_split)
        reps1 = int(set1_spilt[3])
        reps2 = int(set2_split[3])
            
        if (weight1, reps1) >= (weight2, reps2):   
            weight = weight1 
            reps = reps1 
            Abs_PR = Abs_PR_Set_1

        else: 
            weight = weight2 
            reps = reps2 
            Abs_PR = Abs_PR_Set_2
        records.append({
            "weight": weight,
            "reps": reps,
            "number": 8,
            "muscle": "Abs",
            "record": Abs_PR
        })
        
    except AttributeError:
        pass

    except (IndexError, ValueError, ZeroDivisionError):
        pass

    context = {
        "User": user,
        "PRS": records
    }
    return render(request, "profile.html", context)

def calculate_session_score(record):
    """Calculates the 2-set average estimated 1RM for a given session record."""
    try:
        set1_split = record.set_1.split()
        set2_split = record.set_2.split()

        w1 = parse_weight(set1_split)
        w2 = parse_weight(set2_split)

        r1 = int(set1_split[3])
        r2 = int(set2_split[3])

        # Epley 1RM formula: weight * (1 + reps/30)
        formula1 = w1 * (1 + (r1 / 30))
        formula2 = w2 * (1 + (r2 / 30))

        return (formula1 + formula2) / 2.0
    except (AttributeError, IndexError, ValueError, ZeroDivisionError):
        return None

def get_progress_summary(user, model_and_exercise_pairs):
    """model_and_exercise_pairs: list of tuples -> (ModelClass, "Exercise_Name")"""
    today_scores = []
    past_scores = []

    for model_class, exercise_name in model_and_exercise_pairs:
        # Query the actual Model class, filtering by the exercise name string
        records = list(
            model_class.objects.filter(
                username=user.username, exercise=exercise_name
            ).order_by("-date")[:2]
        )

        if len(records) < 2:
            continue

        score_today = calculate_session_score(records[0])
        score_past = calculate_session_score(records[1])

        if score_today is not None and score_past is not None and score_past > 0:
            today_scores.append(score_today)
            past_scores.append(score_past)

    if not today_scores:
        return {
            "today_avg": 0.0,
            "past_avg": 0.0,
            "pct_change": 0.0,
            "is_greater": False,
            "exercises_counted": 0,
        }

    avg_today = sum(today_scores) / len(today_scores)
    avg_past = sum(past_scores) / len(past_scores)
    pct_change = ((avg_today - avg_past) / avg_past) * 100

    return {
        "today_avg": round(avg_today, 2),
        "past_avg": round(avg_past, 2),
        "pct_change": round(pct_change, 2),
        "is_greater": avg_today > avg_past,
        "exercises_counted": len(today_scores),
    }

def error_404_view(request):
    today = current_day()
    user_id = get_user_id(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("/index/")

    # Pair each actual Django Model with its list of exercise strings
    workout_pairs = []

    if today in ["Monday", "Thursday"]:
        for name in Biceps_Exercises:
            workout_pairs.append((Biceps, name))
        for name in Triceps_Exercises:
            workout_pairs.append((Triceps, name))
        for name in Forearms_Exercises:
            workout_pairs.append((Forearms, name))

    elif today in ["Tuesday", "Friday"]:
        for name in Back_Exercises:
            workout_pairs.append((Back, name))
        for name in Leg_Exercises:
            workout_pairs.append((Leg, name))

    elif today in ["Wednesday", "Saturday"]:
        for name in Chest_Exercises:
            workout_pairs.append((Chest, name))
        for name in Shoulder_Exercises:
            workout_pairs.append((Shoulder, name))
        for name in Abs_Exercises:
            workout_pairs.append((Abs, name))

    stats = get_progress_summary(user, workout_pairs)

    if stats["is_greater"]:
        context = {
            "emoji": "🎉",
            "motivated": "Great Job! You Beat Your Last Workout! 📈",
            "level": "Level Up! 🚀",
            "progress": (
                f"Today's Avg ({stats['today_avg']}) beat your last session "
                f"({stats['past_avg']}) by {stats['pct_change']}% across {stats['exercises_counted']} exercises! 💪🔥"
            ),
            "User": user,
            "stats": stats,
        }
    else:
        context = {
            "emoji": "⚠️",
            "motivated": "Keep Going! Consistency is Key! 🔑",
            "level": "Reset & Recharge! 🔋",
            "progress": (
                f"Today's Avg was {stats['today_avg']} vs {stats['past_avg']} last session. "
                "Champions are made on the hard days. Let's attack the next session! 🥊🏋️"
            ),
            "User": user,
            "stats": stats,
        }

    return render(request, "404.html", context)