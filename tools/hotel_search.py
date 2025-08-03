# tools/hotel_search.py

import os
import requests
import json
import re
from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from datetime import datetime

class HotelSearchInput(BaseModel):
    query: str = Field(description="A JSON string with keys 'location', 'check_in', 'check_out', and 'adults'.")

class HotelSearchTool(BaseTool):
    name: str = "hotel_search"
    description: str = "Use this tool to search for real, live hotel prices. The input must be a single JSON string containing the keys 'location', 'check_in', 'check_out', and 'adults'."
    args_schema: Type[BaseModel] = HotelSearchInput

    def _run(self, query: str) -> str:
        match = re.search(r'\{.*\}', query, re.DOTALL)
        if not match:
            return "Error: Could not find a valid JSON object in the input."
        json_string = match.group(0)

        try:
            data = json.loads(json_string)
            location = data["location"]
            check_in = data["check_in"]
            check_out = data["check_out"]
            adults = data["adults"]

            rapidapi_key = os.getenv("RAPIDAPI_KEY")
            if not rapidapi_key:
                return "Error: RapidAPI Key is not configured."
            
            print(f"rapidapi_key: {rapidapi_key}")  # Debugging line to check if the key is loaded

            # --- START: NEW, SIMPLER API LOGIC ---
            
            destination_id_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
            locations_list_url = "https://hotels4.p.rapidapi.com/properties/v2/list"
            # 2a. The API needs day, month, and year separately. We parse the date strings.
            check_in_date_obj = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date_obj = datetime.strptime(check_out, "%Y-%m-%d")

            querystring = {"q":location,"locale":"en_US","langid":"1033","siteid":"300000001"}
            
            headers = {
                "content-type": "application/json",
                "x-rapidapi-key": "1db3e0c830msh3882a1dc5722774p1a4488jsn03f5f4c3ad7c",
                "x-rapidapi-host": "hotels4.p.rapidapi.com"
            }
            
            # This API uses a POST request instead of GET
            print(f"DEBUG: Searching for hotels in: {location}")
            print(f"DEBUG: Searching for destination ID for location: {location}")
            response = requests.get(destination_id_url,headers=headers,params=querystring)
            response.raise_for_status()
            properties_data = response.json()
            destination_id = next((item.get('gaiaId') for item in properties_data.get('sr', []) if item.get('type') == 'CITY'), None)
            if not destination_id:
                return f"Could not find a valid destination ID for the location: {location}"
            
            print(f"DEBUG: Found destination ID: {destination_id}")
            payload = {
                "currency": "INR",
                "eapid": 1,
                "locale": "en_US",
                "siteId": 300000001,
                "destination": {
                    "regionId": destination_id  # Using the dynamic ID we just found
                },
                "checkInDate": {
                    "day": check_in_date_obj.day,
                    "month": check_in_date_obj.month,
                    "year": check_in_date_obj.year
                },
                "checkOutDate": {
                    "day": check_out_date_obj.day,
                    "month": check_out_date_obj.month,
                    "year": check_out_date_obj.year
                },
                "rooms": [
                    {
                        "adults": adults
                    }
                ],
                "resultsStartingIndex": 0,
                "resultsSize": 200,
                "sort": "PRICE_LOW_TO_HIGH"
            }

            headers["Content-Type"] = "application/json"
            # print(f"DEBUG: Searching for hotels with payload: {payload}")
            properties_response = requests.post(locations_list_url, json=payload, headers=headers)
            properties_response.raise_for_status()
            properties_data = properties_response.json()
            
            # --- END: NEW, SIMPLER API LOGIC ---

            hotel_list = properties_data.get('data', {}).get('propertySearch', {}).get('properties', [])
            if not hotel_list:
                return "No hotels found for the specified criteria."
            
            summary = f"Found {len(hotel_list)} hotels in {location}. Here are the top 5:\n"
            for hotel in hotel_list[:5]:
                name = hotel.get('name', 'N/A')
                price_display = hotel.get('price', {}).get('displayMessages', [{}])[0].get('lineItems', [{}])[0].get('value', 'N/A')
                rating = hotel.get('reviews', {}).get('score', 'N/A')
                summary += f"- {name} (Rating: {rating}/10) - Price: {price_display}\n"
            
            return summary

        except requests.exceptions.RequestException as e:
            return f"Error making API request: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    async def _arun(self, query: str) -> str:
        return self._run(query)