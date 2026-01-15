import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException
import json

load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

class OpenCageRateLimitError(Exception):
    pass
class OpenCageInvalidInputError(Exception):
    pass
class OpenCageUnknownError(Exception):
    pass

async def geocode_async(query : str, countrycode: str = "lk"):
    url = "https://api.opencagedata.com/geocode/v1/json"

    params = {
        "q" : query,
        "key" : OPENCAGE_API_KEY,
        "limit" : 1,
        "countrycode" : countrycode
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url=url, params=params)
    except httpx.TimeoutException:
        raise OpenCageUnknownError("Timeout contacting OpenCage API")
    except httpx.RequestError:
        raise OpenCageUnknownError("Network error contacting OpenCage API")

    data = response.json()

    status = data.get("status", {})
    code = status.get("code", 200)

    if code == 400:
        raise OpenCageInvalidInputError(status.get("message", "Invalid input"))
    elif code == 402:
        raise OpenCageRateLimitError("OpenCage rate limit exceeded")
    elif code == 429:
        raise OpenCageRateLimitError("Too many requests")
    elif code >= 500:
        raise OpenCageUnknownError("OpenCage server error")

    if not data.get("results"):
        return None, None, None

    result = data["results"][0]
    lat = result["geometry"]["lat"]
    lng = result["geometry"]["lng"]
    formatted = result.get("formatted")

    return lat, lng, formatted


