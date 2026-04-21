import uuid
from datetime import date as dt_date

def parse_done_dates(done_str: str) -> set[str]:
    if not done_str:
        return set()
    return {d.strip() for d in done_str.split(",") if d.strip()}

def serialize_done_dates(done_dates: set[str]) -> str:
    return ",".join(sorted(done_dates))

def save_new_task(name, desc, freq, task_date):
    new_id = str(uuid.uuid4())  # במקום timestamp
    db.table("tasks").insert({
        "id": new_id,
        "task_name": name,
        "description": desc,
        "recurring": freq,
        "task_date": str(task_date),
        "done_dates": ""
    }).execute()

def mark_task_done(task_id, existing_done_str, day_str):
    done = parse_done_dates(existing_done_str)
    done.add(day_str)  # מונע כפילויות
    db.table("tasks").update({"done_dates": serialize_done_dates(done)}).eq("id", task_id).execute()
