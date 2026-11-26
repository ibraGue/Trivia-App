from fastapi import FastAPI, HTTPException, status
from main import *
from pydantic import BaseModel, Field
import anthropic

app = FastAPI()

class TopicRequest(BaseModel):
    topic: str= Field(max_length=200)


@app.post("/generate", response_model=QuizResponse)
def generate_response(topicrequest: TopicRequest):
    try:
        return generate_quiz(topicrequest.topic)
    except RuntimeError as e:
        print("can't generate the response")
    except ValidationError:
        print("Validation error")
    except TypeError as eb:
        raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing API credentials.",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from eb