"""
Receipt-related DTOs
Defines data structures for receipt extraction and upload responses.
"""

# --- Standard library imports ---
from typing import List, Optional

# --- Third-party imports ---
from pydantic import BaseModel, Field


class ExtractedItemDTO(BaseModel):
    """
    Represents an individual item extracted from a receipt.

    Attributes:
        item_name (str): The name of the item (capitalized).
        quantity (float): The quantity purchased (supports fractional values).
        unit_price (float): The price per item or unit.
        category (str | None): Optional classification of the item.
        total_price (float | None): Computed total (quantity × unit_price).
    """
    item_name: str = Field(..., description="Name of the grocery or product item")
    quantity: float = Field(..., description="Quantity purchased (may be fractional)")
    unit_price: float = Field(..., description="Price per unit or item")
    category: Optional[str] = Field("Uncategorized", description="Optional item category")
    total_price: Optional[float] = Field(None, description="Total = quantity × unit_price")


class ReceiptUploadResponseDTO(BaseModel):
    """
    Represents the structured receipt data after GPT-4o extraction and parsing.

    Attributes:
        store_name (str | None): Optional name of the store.
        store_address (str | None): Optional store location or address.
        receipt_number (str | None): Unique identifier on the receipt.
        receipt_date (str | None): Date of purchase in YYYY-MM-DD format.
        due_date (str | None): Optional due date for bills or invoices.
        payment_method (str | None): Payment type (e.g., Cash, Card).
        currency (str | None): Currency used (e.g., NZD, USD).
        category (str | None): Main classification of the receipt.
        subtotal_amount (float | None): Pre-tax subtotal amount.
        tax_amount (float | None): Total tax on the receipt.
        discount_amount (float | None): Discount applied to the total.
        total_amount (float): Final total amount from the receipt.
        suggestion (str | None): Smart hint on how to tag or manage this receipt.
        items (list[ExtractedItemDTO]): List of extracted line items.
    """
    store_name: Optional[str] = Field(None, description="Store name from receipt header")
    store_address: Optional[str] = Field(None, description="Store address if visible")
    receipt_number: Optional[str] = Field(None, description="Receipt or invoice number")
    receipt_date: Optional[str] = Field(None, description="Date of purchase (YYYY-MM-DD)")
    due_date: Optional[str] = Field(None, description="Due date for payment if applicable")
    payment_method: Optional[str] = Field(None, description="Payment type (e.g., Card, Cash)")
    currency: Optional[str] = Field(None, description="Currency code (e.g., NZD, USD)")
    category: Optional[str] = Field("Uncategorized", description="Main receipt category")
    subtotal_amount: Optional[float] = Field(None, description="Subtotal before taxes or discounts")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    discount_amount: Optional[float] = Field(None, description="Discount applied to total")
    total_amount: float = Field(..., description="Final total amount from receipt")
    suggestion: Optional[str] = Field(None, description="AI suggestion for tagging or budgeting")
    items: List[ExtractedItemDTO] = Field(..., description="List of items parsed from receipt")
