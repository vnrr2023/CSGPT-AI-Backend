import os
from markdown import markdown
from fastapi import Request,FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json,random
from celery_config import save_to_db
from ai import format_query
from langchain_core.output_parsers import JsonOutputParser
from utils import fix_json_string_with_re,json_error,cs_error,program_error
os.environ["TEAM_API_KEY"] = ""
from aixplain.factories import ModelFactory

finetune_model = ModelFactory.get("6713df2357c705a318032c20")

model = ModelFactory.get("6626a3a8c8f1d089790cf5a2")

parser=JsonOutputParser()
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_data(query):
    response = finetune_model.run(query, parameters={ "numResults": 50 })
    context=""
    for data in response["details"]:
        context += data["data"] + "."
    context=format_query(query)
    return context


def get_llm_response(query):
    try:
        template='''
        You are tasked with answering questions based on the provided context. Your response should be both accurate and detailed, based solely on the given context. Format your response in proper JSON format with no extra space at start with two keys:
        
        ans: This should contain the detailed answer in markdown format.
        status: This should be a string value indicating relevance. Use "true" if the question is relevant to the context, and "false" if it is not.
        Do not include any additional text or explanations. Only provide the JSON formatted response.
        If you don't find an answer in the context and the question is related to a theoretical topic about  computer science , provide an answer and set the status to "true" .
        if user asks question which is not related to computer science then also set the status as "false" .
        Even if user asks questions for commerce,arts field or related to english grammar set the status to "false" .
        For programming requests (e.g., "write a program",etc etc), avoid providing a direct answer and set the status to "program".
        to prepsent words with apostrophe or double apostrophe in the ans only use ' or ' '
        <context>{context} <context>
        Question: {question}
        '''
        context=get_data(query)
        prompt=template.format(context=context,question=query)
        response = model.run({
            "text": prompt,
            "max_tokens": 8000,
            "temperature": 0.4,
        })
        data=response['data']
        return {"data":data,"status":True}
    except:
        return {"status":False}

def get_llm_response_of_error(query):
    try:
        error_template='''
        You are tasked with answering questions based on the provided context. Your response should be both accurate and detailed, based solely on the given context.Dont give the ans in Markdown format. Format your response in proper JSON format with no extra space at start with two keys:

        ans: This should contain the detailed answer without markdown.
        status: This should be a string value indicating relevance. Use "true" if the question is relevant to the context, and "false" if it is not.
        Do not include any additional text or explanations. Only provide the JSON formatted response.
        If you don't find an answer in the context and the question is related to a theoretical topic about computer science, provide an answer in point format and set the status to "true".
        If the user asks a question that is not related to computer science, set the status to "false".
        Even if the user asks questions related to commerce, arts, or English grammar, set the status to "false".
        For programming requests (e.g., "write a program", etc.), avoid providing a direct answer and set the status to "program".
        To represent words with apostrophes or double apostrophes in the ans, only use ' or ''.
        give me json with no preamble and no markdown and also no nested json .
        <context>{context}</context>
        Question: {question}
        '''
        context=get_data(query)
        prompt=error_template.format(context=context,question=query)
        response = model.run({
            "text": prompt,
            "max_tokens": 8000,
            "temperature": 0.4,
        })
        data=response['data']
        return {"data":data,"status":True}
    except:
        return {"status":False}


def parse_response(response,question):
    try:
        data=parser.parse(response)
    except Exception as e:
        try:
            data=json.loads(fix_json_string_with_re(response))
        except:
            try:
                response=get_llm_response_of_error(question)['data']
                data=parser.parse(response)
            except:
                return {"status":False}
    
    return {"data":data,"status":True}

@app.post("/query/")
async def answer_query(request:Request):
    data=await request.json()
    question=data['question']
    operating_system,browser=data['os'],data['browser']
    user_id=data['user_id']
    if not question:
        return JSONResponse({'markdown_data':"Enter a question...",},status_code=200)
    save_to_db.delay(operating_system,browser,user_id,question)
    response=get_llm_response(question)['data']
    response=parse_response(response,question)
    if response["status"]==False: 
         return JSONResponse({'markdown_data':json_error[random.randint(0,9)]},status_code=200)
    data=response["data"]
    # try:
    #     data=parser.parse(response)
    # except Exception as e:
    #     try:
    #         data=json.loads(fix_json_string_with_re(response))
    #     except:
    #         try:
    #             response=get_llm_response_of_error(question)['data']
    #             data=parser.parse(response)
    #             # return JSONResponse({
    #             #     'markdown_data':data['ans']
    #             # },status_code=200)
    #         except:
    #             return JSONResponse({
    #                 'markdown_data':json_error[random.randint(0,9)]
    #             },status_code=200)
    try: 
        if data['status']=="true":
            return JSONResponse(
                {
                'markdown_data':data['ans'],
                },
                status_code=200
                )
        elif data['status']=="program":
            return JSONResponse({
                'markdown_data':program_error[random.randint(0,9)]
            },status_code=200)
        
        return JSONResponse({
                'markdown_data':cs_error[random.randint(0,9)]
            },status_code=200)
    except:
        print("problem")
        return JSONResponse({
            'markdown_data':json_error[random.randint(0,9)]
        },status_code=200)


@app.get("/test")
async def test():
    return {"data":"ok"}




# https://colab.research.google.com/drive/1OSf75TjFWv4b9663sdSzTMxDTvOBWyXf#scrollTo=3JxP1lR-K7gl