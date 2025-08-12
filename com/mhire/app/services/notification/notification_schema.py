from pydantic import BaseModel

class Quote(BaseModel):
    quote: str
    timestamp: str