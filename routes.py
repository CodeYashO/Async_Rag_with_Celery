from celery import result
from model import ChatRequest , ChatRequestId
from fastapi import APIRouter
from tasks import process_chat
from celery.result import AsyncResult
from celery_app import celery

router = APIRouter(prefix="/async_rag/v1")

@router.post("/chat")
def chat(request : ChatRequest):
    user_message = request.message
    celery_task = process_chat.delay(user_message) # sending to celery wroker for processing

    return {
        "id" : celery_task.id,
        "status" : "queued"
    }


#syntax -> function_name.delay(function_argument)
# delay() -> this function will sends the function and argument to the celery worker for execution 


@router.get("/chat_result")
def chat_result(request : ChatRequestId):
    celery_task_id = request.id

    celery_task_result = AsyncResult(celery_task_id , app=celery)

    print(f"############################{celery_task_result}")

    if celery_task_result.ready() == True:
        return {
            "status" : "Completed",
            "result" : celery_task_result.result
        }

    return {
        "status" : celery_task_result.status
    }
