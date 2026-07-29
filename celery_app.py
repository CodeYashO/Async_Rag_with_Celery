from celery import Celery

celery = Celery(
    "async_rag_with_celery", ## celery app name
    broker="redis://localhost:6379/0", ## this stores the tasks
    backend="redis://localhost:6379/0",  ## this stores the tasks result after execution completed
    include=["tasks"]
)

# syntax -> include["file_name_in_which_tasks_created" .......]
## include=[ "email_tasks" , "ai_tasks" , "report_tasks"]
# we have to mention every task file name in which task's will create

### redis://localhost:6379/0 -> this zero is database in redis there are many databases present in the redis.