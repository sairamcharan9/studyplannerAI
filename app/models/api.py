from pydantic import BaseModel

class TranslationRequest(BaseModel):
    text: str
    target_language: str

class SummarizationRequest(BaseModel):
    text: str

class KeywordRequest(BaseModel):
    text: str
