import json
import logging
from typing import Dict, Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.openai_services import ChatAssistantService
from app.util.formattings import format_currency

logger = logging.getLogger(__name__)

chat_assistant_service = ChatAssistantService()
chat_assistant_route = APIRouter(prefix="/openai")


@chat_assistant_route.post(path="/chat_assistant/send_message")
async def send_message(request: Request):
    request = await request.json()
    message_body = request.get("message")

    key = request.get("key")
    data = {"key": key, "message": message_body}
    response = await chat_assistant_service.generate_response(data=data, callback=call_function)
    return JSONResponse(status_code=200, content={"data": response})


def call_function(name: str, args: str) -> str:
    args = json.loads(args)
    logger.debug(f"Calling function: {name} with args: {args}")
    if name == "send_email":
        return send_email(args)
    if name == "calculate_financing":
        return calculate_financing(args)

    return "function not found"


def send_email(args) -> str:
    logger.debug(f"Calling send_email with args: {args}")
    email = args.get("recipient_email")
    return "success"


def calculate_financing(args: Dict[str, float | int | str]) -> str:
    logger.debug(f"Calling calculate_financing with args: {args}")
    cpf = args.get("cpf")
    date_of_birth = args.get("date_of_birth")
    monthly_income = args.get("monthly_income")

    price = calculate_financing_price(args=args)
    sac = calculate_financing_sac(args=args)
    return json.dumps([price, sac])


def calculate_financing_price(args: Dict[str, float | int | str]) -> str | dict[str, str | Any]:
    logger.debug(f"Calling calculate_financing with args: {args}")

    property_value = args.get("property_value")
    initial_deposit = args.get("initial_deposit")
    annual_interest_rate = args.get("annual_interest_rate")
    term_years = args.get("term_years")

    if initial_deposit >= property_value:
        return "A entrada deve ser menor que o valor do imóvel."
    if annual_interest_rate <= 0 or term_years <= 0:
        return "Taxa de juros e prazo devem ser maiores que zero."

    financed_value = property_value - initial_deposit
    monthly_fee = (annual_interest_rate / 100) / 12
    number_of_installments = term_years * 12
    monthly_payment = (financed_value * monthly_fee) / (1 - pow(1 + monthly_fee, -number_of_installments))
    total_cost = monthly_payment * number_of_installments

    return {
        "system": "PRICE",
        "financed_value": format_currency(value=financed_value),
        "monthly_payment": format_currency(value=monthly_payment),
        "total_cost": format_currency(value=total_cost)
    }


def calculate_financing_sac(args: Dict[str, float | int | str]):
    property_value = args.get("property_value")
    initial_deposit = args.get("initial_deposit")
    annual_interest_rate = args.get("annual_interest_rate")
    term_years = args.get("term_years")

    financed_value = property_value - initial_deposit
    total_months = term_years * 12
    monthly_rate = (annual_interest_rate / 100) / 12
    amortization = financed_value / total_months

    first_payment = amortization + (financed_value * monthly_rate)
    last_balance = financed_value - (amortization * (total_months - 1))
    last_payment = amortization + (last_balance * monthly_rate)
    total_cost = (first_payment + last_payment) / 2 * total_months

    return {
        "system": "SAC",
        "financed_value": format_currency(value=financed_value),
        "first_installment": format_currency(value=first_payment),
        "last_installment": format_currency(value=last_payment),
        "total_cost": format_currency(value=total_cost),
    }
