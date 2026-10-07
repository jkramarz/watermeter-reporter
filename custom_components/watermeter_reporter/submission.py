"""Submit water meter readings to Urząd Gminy Dobczyce."""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.dobczyce.pl/woda"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"


@dataclass(frozen=True)
class ReadingData:
    owner_name: str
    address: str
    meter_number: str
    primary_reading: int
    secondary_reading: int | None
    tertiary_reading: int | None
    reading_date: datetime.date
    notes: str
    dry_run: bool


def parse_captcha_question(label_text: str) -> str:
    """Extract and solve the simple arithmetic CAPTCHA from label text."""
    label_text = label_text.replace("=", " = ").replace("x", "*").replace("X", "*")
    match = re.search(r"(\d+)\s*([+\-*/])\s*(\d+)", label_text)
    if not match:
        raise ValueError(f"Could not parse captcha expression from: {label_text!r}")

    left, operator, right = match.groups()
    left_value, right_value = int(left), int(right)
    if operator == "+":
        return str(left_value + right_value)
    if operator == "-":
        return str(left_value - right_value)
    if operator == "*":
        return str(left_value * right_value)
    if operator == "/":
        if right_value == 0:
            raise ValueError("Division by zero in captcha expression")
        return str(left_value // right_value)
    raise ValueError(f"Unsupported captcha operator: {operator}")


def extract_form_data(html: str) -> dict[str, str]:
    """Extract hidden form fields and solve the CAPTCHA prompt."""
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", action="/woda")
    if form is None:
        raise RuntimeError("Could not find the water meter submission form on the page")

    data = {
        input_element.get("name"): input_element.get("value", "")
        for input_element in soup.find_all("input", type="hidden")
        if input_element.get("name")
    }
    captcha_prompts = soup.find_all("span", class_="field-prefix")
    if len(captcha_prompts) != 1:
        raise RuntimeError("Could not find the captcha prompt text in the page")
    data["captcha_response"] = parse_captcha_question(captcha_prompts[0].get_text())
    return data


def build_payload(data: ReadingData, form_data: dict[str, str]) -> dict[str, str]:
    """Build the form payload for the Dobczyce submission."""
    payload = dict(form_data)
    payload["submitted[nazwisko_i_imi_waciciela_nazwa_zakadu]"] = data.owner_name
    payload["submitted[adres_wodomierza]"] = data.address
    payload["submitted[nr_licznika]"] = data.meter_number
    payload["submitted[wskazanie_licznika_gownego]"] = str(data.primary_reading)
    payload["submitted[wskazanie_drugiego_licznika_jeli_jest]"] = str(data.secondary_reading or "")
    payload["submitted[wskazanie_trzeciego_licznika_jesli_jest]"] = str(data.tertiary_reading or "")
    payload["submitted[uwagi]"] = data.notes
    payload["submitted[data_odczytu][year]"] = str(data.reading_date.year)
    payload["submitted[data_odczytu][month]"] = str(data.reading_date.month)
    payload["submitted[data_odczytu][day]"] = str(data.reading_date.day)
    payload["op"] = payload.get("op", "Wyślij formularz")
    return payload


def submit_reading(data: ReadingData) -> dict[str, bool | str]:
    """Fetch the form, submit the reading, and return a service result."""
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    page = session.get(PAGE_URL, timeout=30)
    if page.status_code != 200:
        return {"success": False, "message": f"Failed to fetch form page: {page.status_code}"}

    payload = build_payload(data, extract_form_data(page.text))
    if data.dry_run:
        return {"success": True, "message": "Dry run payload prepared", "payload": payload}

    response = session.post(
        urljoin(PAGE_URL, "/woda"),
        data=payload,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": PAGE_URL,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
        timeout=30,
    )
    response.encoding = response.apparent_encoding
    if response.status_code != 200:
        return {"success": False, "message": f"Submit failed with status code {response.status_code}"}

    if "Dziekujemy, twoje zgłoszenie zostało przyjęte." in response.text:
        return {"success": True, "message": "Submission appears to have succeeded."}
    return {"success": False, "message": "Submission may have failed. Please check the response content."}
