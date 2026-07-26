## This file is for creating the tasks for celery
from celery_app import celery
from rag import rag_pipeline

@celery.task
def process_chat(user_message):
    
    return rag_pipeline(user_message)