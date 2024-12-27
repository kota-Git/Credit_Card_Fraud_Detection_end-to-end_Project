from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run

from typing import Optional

from Demo_project.constants import APP_HOST, APP_PORT
from Demo_project.pipeline.prediction_pipeline import CreditCardData, CreditCardClassifier
from Demo_project.pipeline.train_pipeline import TrainPipeline

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.LIMIT_BAL: Optional[str] = None
        self.EDUCATION: Optional[str] = None
        self.MARRIAGE:  Optional[str] = None
        self.PAY_0: Optional[str] = None
        self.PAY_2: Optional[str] = None
        self.PAY_3: Optional[str] = None
        self.PAY_4: Optional[str] = None
        self.PAY_5: Optional[str] = None
        self.PAY_6: Optional[str] = None
        self.BILL_AMT1: Optional[str] = None
        self.BILL_AMT6: Optional[str] = None
        self.PAY_AMT1: Optional[str] = None
        self.PAY_AMT2: Optional[str] = None
        self.PAY_AMT3: Optional[str] = None
        self.PAY_AMT4: Optional[str] = None
        self.PAY_AMT5: Optional[str] = None
        self.PAY_AMT6: Optional[str] = None

    async def get_CreditCard_data(self):
        form = await self.request.form()
        self.LIMIT_BAL = form.get("LIMIT_BAL")
        self.EDUCATION = form.get("EDUCATION")
        self.MARRIAGE = form.get("MARRIAGE")
        self.PAY_0 = form.get("PAY_0")
        self.PAY_2 = form.get("PAY_2")
        self.PAY_3 = form.get("PAY_3")
        self.PAY_4 = form.get("PAY_4")
        self.PAY_5 = form.get("PAY_5")
        self.PAY_6 = form.get("PAY_6")
        self.BILL_AMT1 = form.get("BILL_AMT1")
        self.BILL_AMT6 = form.get("BILL_AMT6")
        self.PAY_AMT1 = form.get("PAY_AMT1")
        self.PAY_AMT2 = form.get("PAY_AMT2")
        self.PAY_AMT3 = form.get("PAY_AMT3")
        self.PAY_AMT4 = form.get("PAY_AMT4")
        self.PAY_AMT5 = form.get("PAY_AMT5")
        self.PAY_AMT6 = form.get("PAY_AMT6")

@app.get("/", tags=["authentication"])
async def index(request: Request):

    return templates.TemplateResponse(
            "CreditCard.html",{"request": request, "context": "Rendering"})


@app.get("/train")
async def trainRouteClient():
    try:
        train_pipeline = TrainPipeline()

        train_pipeline.run_pipeline()

        return Response("Training successful !!")

    except Exception as e:
        return Response(f"Error Occurred! {e}")


@app.post("/")
async def predictRouteClient(request: Request):
    try:
        form = DataForm(request)
        await form.get_CreditCard_data()
        
        CreditCard_data = CreditCardData(
                                LIMIT_BAL= form.LIMIT_BAL,
                                EDUCATION = form.EDUCATION,
                                MARRIAGE = form.MARRIAGE,
                                PAY_0 = form.PAY_0,
                                PAY_2= form.PAY_2,
                                PAY_3= form.PAY_3,
                                PAY_4 = form.PAY_4,
                                PAY_5= form.PAY_5,
                                PAY_6= form.PAY_6,
                                BILL_AMT1= form.BILL_AMT1,
                                BILL_AMT6= form.BILL_AMT6,
                                PAY_AMT1= form.PAY_AMT1,
                                PAY_AMT2= form.PAY_AMT2,
                                PAY_AMT3= form.PAY_AMT3,
                                PAY_AMT4= form.PAY_AMT4,
                                PAY_AMT5= form.PAY_AMT5,
                                PAY_AMT6= form.PAY_AMT6
                                )
        
        CreditCard_df = CreditCard_data.get_CreditCard_input_data_frame()

        model_predictor = CreditCardClassifier()

        value = model_predictor.predict(dataframe=CreditCard_df)[0]

        status = None
        if value == 1:
            status = "CreditCard Defaulter"
        else:
            status = "CreditCard Non-Defaulter"

        return templates.TemplateResponse(
            "CreditCard.html",
            {"request": request, "context": status},
        )
        
    except Exception as e:
        return {"status": False, "error": f"{e}"}


if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)