from apscheduler.triggers.interval import IntervalTrigger
from fastapi import HTTPException

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid, json, os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

from app.services.manager import update_penalties


def scheduled_update():
    data = load_data()
    for study in data["studies"]:
        update_penalties(study)
    save_data(data)
    print(">>> 스터디 벌금 자동 업데이트 완료")


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

DATA_FILE = "data/studies.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"studies": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# APScheduler 백그라운드 스케줄러 생성
scheduler = BackgroundScheduler()

# 매주 일요일 23:59 실행
scheduler.add_job(
    scheduled_update,
    IntervalTrigger(seconds=5)
    # CronTrigger(day_of_week="sun", hour=23, minute=59)
)

scheduler.start()

# FastAPI 서버 종료 시 스케줄러도 종료
atexit.register(lambda: scheduler.shutdown())



@app.get("/")
def home(request: Request):
    data = load_data()
    return templates.TemplateResponse("index.html", {"request": request, "studies": data["studies"]})

@app.post("/create-study")
def create_study(name: str = Form(...), password: str = Form(...)):
    data = load_data()
    new_study = {
        "id": str(uuid.uuid4()),
        "name": name,
        "password": password,
        "members": []
    }
    data["studies"].append(new_study)
    save_data(data)
    return RedirectResponse("/", status_code=303)


@app.get("/study/{study_id}")
def study_detail(study_id: str, request: Request):
    data = load_data()
    study = next((s for s in data["studies"] if s["id"] == study_id), None)
    if not study:
        raise HTTPException(status_code=404, detail="스터디를 찾을 수 없음")

    return templates.TemplateResponse("study_detail.html", {"request": request, "study": study})


@app.post("/study/{study_id}/add-member")
def add_member(study_id: str, boj_id: str = Form(...), problem1: str = Form(...), problem2: str = Form(...),
               password: str = Form(...)):
    data = load_data()
    study = next((s for s in data["studies"] if s["id"] == study_id), None)
    if not study:
        raise HTTPException(status_code=404, detail="스터디를 찾을 수 없음")

    if study["password"] != password:
        raise HTTPException(status_code=403, detail="비밀번호 불일치")

    new_member = {
        "boj_id": boj_id,
        "problems": [problem1, problem2],
        "penalty": 0
    }
    study["members"].append(new_member)
    save_data(data)
    return RedirectResponse(f"/study/{study_id}", status_code=303)



