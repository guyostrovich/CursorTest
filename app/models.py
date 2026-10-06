"""Pydantic models describing what the API returns."""

from pydantic import BaseModel


class Product(BaseModel):
    """One product in the Acme MedTech portfolio (from data/portfolio.yaml)."""

    id: str
    name: str
    category: str
    intended_use: str
    fda_pathway: str  # 510k, PMA or De Novo
    markets: list[str]
    has_software: bool
    uses_ai: bool
    tags: list[str]
    product_codes: list[str] = []


class Update(BaseModel):
    """One regulatory update (from a markdown file in data/updates)."""

    id: str
    title: str
    date: str  # YYYY-MM-DD
    jurisdiction: str  # FDA or EU
    tags: list[str]
    source_url: str
    body: str


class Clearance(BaseModel):
    """A 510(k) clearance. Field names match openFDA's, so a raw record fits directly."""

    k_number: str = ""
    device_name: str = ""
    applicant: str = ""
    product_code: str = ""
    decision_date: str = ""
    decision_description: str = ""


class Recall(BaseModel):
    """A device recall. Field names match openFDA's, so a raw record fits directly."""

    product_res_number: str = ""
    recalling_firm: str = ""
    product_description: str = ""
    reason_for_recall: str = ""
    recall_status: str = ""
    product_code: str = ""
    event_date_initiated: str = ""
