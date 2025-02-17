"""
Web service for model inference.
"""
# pylint: disable=too-few-public-methods, undefined-variable, unused-import, assignment-from-no-return, duplicate-code
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic.dataclasses import dataclass

from config.lab_settings import LabSettings
from lab_7_llm.main import LLMPipeline, TaskDataset


@dataclass
class Query:
    """
    Class for query content.
    """
    question: str


def init_application() -> tuple[FastAPI, LLMPipeline]:
    """
    Initialize core application.

    Run: uvicorn reference_service.server:app --reload

    Returns:
        tuple[fastapi.FastAPI, LLMPipeline]: instance of server and pipeline
    """
    max_length = 120
    batch_size = 1
    device = 'cpu'
    settings_path = Path(__file__).parent / 'settings.json'
    empty_dataset = TaskDataset(pd.DataFrame())

    fastapi_app = FastAPI()
    fastapi_app.mount('/static',
              StaticFiles(directory=f'{Path(__file__).parent}/assets'), name='static')

    settings = LabSettings(settings_path)
    llm_pipeline = LLMPipeline(settings.parameters.model,
                           empty_dataset,
                           max_length, batch_size, device)

    return fastapi_app, llm_pipeline


app, pipeline = init_application()

@app.get('/', response_class=HTMLResponse)
async def root(request: Request) -> Jinja2Templates.TemplateResponse:
    """
    Root endpoint.

    Args:
        request: GET-request to the server

    Returns:
        HTML-template
    """
    templates = Jinja2Templates(directory=f'{Path(__file__).parent}/assets')
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/infer')
async def infer(query: Query) -> JSONResponse:
    """
    Main endpoint for model inference.

    Args:
        query: Query instance, containing text to classify

    Returns:
        JSONResponse instance in {"infer": prediction} format
    """
    prediction = pipeline.infer_sample((query.question, ))
    return JSONResponse(content={'infer': prediction})
