import anthropic
import sys
from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Annotated, Literal
from fastapi import HTTPException

client = anthropic.Anthropic()


class Question(BaseModel):
    question: str = Field(min_length=5, max_length=200)
    options: list[Annotated[str, Field(min_length=2, max_length=100)]] = Field(min_length=4, max_length=4)
    answer: int = Field(ge=0, le=3)

class QuizResponse(BaseModel):
    status: Literal["ok", "error"]
    message: str | None = None
    @model_validator(mode="after")
    def check_questions(self):
        if self.status == "ok":
            if len(self.questions) < 3:
                raise ValueError("Questions field must have three questions")
        if self.status == "error":
            if not self.message:
                raise ValueError("Message is necessary in case of error")
            if self.questions:
                raise ValueError("No questions should be generated in case of error")
        return self
    questions: list[Question] = Field(max_length=3)



def generate_quiz(topic):
    prompt = f"Generate 3 questions on {topic} that each have four options where one of them is the right answer, and put the index of the right option in answer(0-based). If you're unsure about the topic or the topic is incomprehensible or is a symbol, give status error and list the problem in message. Try to keep questions under 200 characters, and options under 100."


    try:
        message = client.messages.parse(
            model="claude-sonnet-5-5",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            output_format=QuizResponse
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail="Validation Error, couldn't parse the message")

    result = message.parsed_output

    if result:
        return result
    else:
        raise HTTPException(status_code=422)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter your topic: ")
    if not topic:
        raise ValueError("Error: No topic validated")
    if len(topic) > 200:
        raise ValueError("The topic shouldn't exceed 200 characters")
    response = generate_quiz(topic)
    if response.status == "ok":
        print(response.questions)
    else:
        print(response.message)