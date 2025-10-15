import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware 

# -------------------------
# კონფიგურაცია
# -------------------------
GITA_BASE_URL = "https://gita-ai.mediapark.tech"
GITA_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjaXZpdHRhX3Rlc3RfYWNjb3VudCIsImV4cCI6MTc1OTg4NDE4Mn0.34gYOJQDm_53beNF97IShFJGaes6i55N6s-dEyKoOuw"
FULL_ENDPOINT = f"{GITA_BASE_URL}/v1/chat/message"

app = FastAPI(title="Chat API (JSON)")

# ---------------------------------
# CORS კონფიგურაცია
# ---------------------------------
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# -------------------------
# Schemas
# -------------------------
class SendMessageBody(BaseModel):
    message: str
    conversation_history: Optional[list] = None

# -------------------------
# Route
# -------------------------
@app.post("/chat/send-message")
async def send_message(body: SendMessageBody):
    payload = {
        "query": body.message,
        "user_id": "anonymous"
    }
    if body.conversation_history:
        payload["conversation_history"] = body.conversation_history

    gita_headers = {
        "x-api-key": GITA_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                FULL_ENDPOINT,
                headers=gita_headers,
                json=payload
            )
            
            # აგდებს HTTPStatusError-ს თუ სტატუსი არ არის 2xx
            resp.raise_for_status() 
            
            # --- ცვლილება აქ! ტექსტის დამუშავება ---
            # ვიღებთ პასუხს როგორც სუფთა ტექსტს
            raw_text = resp.text.strip()
            
            if not raw_text:
                return {"reply": "პასუხი GITA AI-სგან ცარიელია."}
                
            # ვამოწმებთ და ვაშორებთ 'data:' პრეფიქსს, რომელიც დამახასიათებელია Streaming-ისთვის
            if raw_text.startswith("data: "):
                reply_text = raw_text[len("data: "):].strip()
            else:
                # თუ 'data:' პრეფიქსი არ არის, ვცდილობთ JSON-ის გარდაქმნას
                try:
                    data = resp.json()
                    reply_text = data.get("answer", "პასუხი ვერ მოიძებნა 'answer' ველში")
                except:
                    # თუ ვერც JSON-ად გარდაიქმნა და ვერც 'data:' იყო, ვიყენებთ ნედლ ტექსტს
                    reply_text = raw_text
            
            # ვუბრუნებთ დამუშავებულ ტექსტს JavaScript-ს
            return {"reply": reply_text}

    except httpx.HTTPStatusError as e:
        print(f"GITA API HTTP სტატუსის შეცდომა: {e.response.status_code}")
        return {"reply": f"GITA API-ს შეცდომა: HTTP {e.response.status_code}. (შესაძლოა API Key-ის პრობლემაა)."}
        
    except httpx.RequestError as e:
        print(f"HTTPX Request ქსელური შეცდომა: {e.__class__.__name__} - {e}")
        return {"reply": "ქსელური შეცდომა GITA AI-სთან დაკავშირებისას. შეამოწმეთ ინტერნეტი."}
    
    except Exception as e:
        print(f"გაუთვალისწინებელი შიდა შეცდომა: {e}") 
        return {"reply": "გაუთვალისწინებელი შიდა სერვერის შეცდომა."}