from celery import Celery
import psycopg2
import uuid
from datetime import datetime

class Config:
    CELERY_BROKER_URL:str="redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND:str="redis://127.0.0.1:6379/0"


settings=Config()
celery_app=Celery(__name__,broker=settings.CELERY_BROKER_URL,backend=settings.CELERY_RESULT_BACKEND)


def connect_db():
    connection = psycopg2.connect(
        host='localhost',
        port='5432',
        dbname='' ,
        user='' ,
        password='' 
    )
    return connection,connection.cursor()

@celery_app.task
def save_to_db(operating_system,browser,user_id,question):
    try:
        user_info_query='''
        insert into csgpt_app_userinfo
        values (%s,%s,%s,%s);
        '''
        question_query='''
        insert into csgpt_app_question (id,text,user_id,date_of_question)
        values (%s,%s,%s,%s);
        '''
        uuid_=str(uuid.uuid4())
        current_datetime = datetime.now()
        user_info_values = (uuid_,operating_system,browser,current_datetime)  
        question_values = (uuid_,question,user_id,current_datetime)

        connection,cursor=connect_db()
        cursor.execute(user_info_query,user_info_values)
        connection.commit()
        cursor.execute(question_query,question_values)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(e)
        cursor.close()
        connection.close()