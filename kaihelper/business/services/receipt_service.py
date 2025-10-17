"""
ReceiptService (GPT-4o only)
Refactored for clarity, maintainability, and database consistency.
Handles single receipt-level expense with multiple grocery items.
"""

# --- Standard library imports ---
import os
import base64
import json
import time
from datetime import datetime
from io import BytesIO
from PIL import Image

# --- Third-party imports ---
from openai import OpenAI

# --- First-party imports ---
from kaihelper.business.interfaces.i_receipt_service import IReceiptService
from kaihelper.business.interfaces.icategory_service import ICategoryService
from kaihelper.business.interfaces.igrocery_service import IGroceryService
from kaihelper.business.interfaces.iexpense_service import IExpenseService
from kaihelper.contracts.receipt_dto import ReceiptUploadResponseDTO, ExtractedItemDTO
from kaihelper.contracts.category_dto import CategoryDTO
from kaihelper.contracts.expense_dto import ExpenseDTO
from kaihelper.contracts.grocery_dto import GroceryDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.config.settings import settings


class ReceiptService(IReceiptService):
    """
    Processes receipts using GPT-4o and synchronizes categories, groceries,
    and a single receipt-level expense.
    """

    def __init__(
        self,
        category_service: ICategoryService,
        grocery_service: IGroceryService,
        expense_service: IExpenseService,
    ) -> None:
        """Initialize the receipt service and verify OpenAI API key."""
        self.category_service = category_service
        self.grocery_service = grocery_service
        self.expense_service = expense_service

        if not settings.OPENAI_API_KEY:
            raise RuntimeError("Missing OPENAI_API_KEY in .env or environment.")

        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        self.client = OpenAI()

    def process_receipt(self, user_id: int, image_bytes: bytes) -> ResultDTO:
        """
        Process a receipt:
        - Extract receipt details via GPT-4o.
        - Create or update a single expense record.
        - Sync groceries under that expense.
        """
        start_time = time.time()
        try:
            parsed = self._extract_with_gpt(image_bytes)
            items = [ExtractedItemDTO(**item) for item in parsed.get("items", [])]
            total_amount = float(parsed.get("total_amount", 0.0))
            suggestion = parsed.get("suggestion", "")
            category_name = parsed.get("category", "Groceries")
            category_id = self._ensure_category(category_name)

            #Pass all GPT fields into _save_receipt_expense
            expense_result = self._save_receipt_expense(user_id, category_id, parsed)

            if not expense_result.success:
                return ResultDTO.fail(
                    f"Failed to record receipt expense: {expense_result.message}"
                )

            expense_id = getattr(expense_result.data, "expense_id", None)
            for item in items:
                self._process_item(user_id, item, category_id, expense_id)

            elapsed = round((time.time() - start_time) * 1000, 2)
            print(
                f"[ReceiptService] Processed receipt ({category_name}) with "
                f"{len(items)} items in {elapsed} ms"
            )

            return ResultDTO.ok(
                "Receipt processed successfully",
                ReceiptUploadResponseDTO(
                    category=category_name,
                    total_amount=total_amount,
                    suggestion=suggestion,
                    items=items,
                ),
            )

        except Exception as err:  # pylint: disable=broad-except
            return ResultDTO.fail(f"Failed to process receipt: {repr(err)}")

    def _save_receipt_expense(self, user_id: int, category_id: int | None, parsed: dict) -> ResultDTO:
        """Create a single expense record for the entire receipt, including metadata."""
        try:
            expense_dto = ExpenseDTO(
                expense_id=None,
                user_id=user_id,
                grocery_id=None,
                category_id=category_id,
                amount=float(parsed.get("total_amount", 0.0)),
                description=parsed.get("suggestion") or "Auto-added from receipt scan",
                expense_date=datetime.now().date(),
                notes="Auto-added from receipt scan",
                # --- mapped new fields ---
                store_name=parsed.get("store_name"),
                store_address=parsed.get("store_address"),
                receipt_number=parsed.get("receipt_number"),
                payment_method=parsed.get("payment_method"),
                currency=parsed.get("currency"),
                subtotal_amount=parsed.get("subtotal_amount"),
                tax_amount=parsed.get("tax_amount"),
                discount_amount=parsed.get("discount_amount"),
                due_date=parsed.get("due_date"),
                suggestion=parsed.get("suggestion"),
            )

            print(
                f"[ReceiptService] Creating receipt-level expense "
                f"(Store: {parsed.get('store_name')}, Total: {parsed.get('total_amount')})"
            )
            return self.expense_service.add_expense(expense_dto)
        except Exception as err:  # pylint: disable=broad-except
            return ResultDTO.fail(f"Failed to save receipt expense: {repr(err)}")

    def _process_item(
        self, user_id: int, item: ExtractedItemDTO, category_id: int | None, expense_id: int | None
    ) -> None:
        """Add or update groceries belonging to a receipt."""
        grocery_dto = self._build_grocery_dto(user_id, item, category_id)
        grocery_result = self._save_grocery(user_id, grocery_dto)

        if grocery_result.success:
            print(f"[ReceiptService] Added grocery '{item.item_name}' under expense #{expense_id}")
        else:
            print(f"[ReceiptService] Skipped item '{item.item_name}' – {grocery_result.message}")

    def _ensure_category(self, name: str) -> int | None:
        """Ensure a category exists or create it if missing."""
        try:
            name = name.strip().capitalize()
            result = self.category_service.get_category(name)
            if result.success and result.data:
                category_id = getattr(result.data, "category_id", None)
                print(f"[ReceiptService] Using existing category '{name}' (ID: {category_id})")
                return category_id

            category_dto = CategoryDTO(
                category_id=None,
                name=name,
                description=f"Auto-added category from receipt import: {name}",
            )
            created = self.category_service.add_category(category_dto)
            if created.success and created.data:
                category_id = getattr(created.data, "category_id", None)
                print(f"[ReceiptService] Created new category '{name}' (ID: {category_id})")
                return category_id

            print(f"[ReceiptService] Failed to create category '{name}'")
            return None
        except Exception as err:  # pylint: disable=broad-except
            print(f"[ReceiptService] Failed to ensure category '{name}': {repr(err)}")
            return None

    def _build_grocery_dto(
        self, user_id: int, item: ExtractedItemDTO, category_id: int | None
    ) -> GroceryDTO:
        """Convert a parsed receipt item to a GroceryDTO."""
        return GroceryDTO(
            user_id=user_id,
            category_id=category_id,
            item_name=item.item_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            purchase_date=datetime.now().date(),
            notes="Auto-added from receipt",
            total_cost=round(item.unit_price * item.quantity, 2),
        )

    def _save_grocery(self, user_id: int, dto: GroceryDTO) -> ResultDTO:
        """Add or update a grocery entry."""
        existing = self.grocery_service.find_by_name(user_id, dto.item_name)
        if existing and existing.success and existing.data:
            dto.grocery_id = existing.data.grocery_id
            print(f"[ReceiptService] Updating grocery '{dto.item_name}'")
            return self.grocery_service.update_grocery(dto)

        print(f"[ReceiptService] Adding grocery '{dto.item_name}'")
        return self.grocery_service.add_grocery(dto)

    def _extract_with_gpt(self, image_bytes: bytes) -> dict:
        """
        Use GPT-4o Vision to extract structured receipt data.
        Returns category, items, total amount, and suggestion.
        """
        try:
            #b64_image = base64.b64encode(image_bytes).decode("utf-8")
            with Image.open(BytesIO(image_bytes)) as _img:
                _img = _img.convert("RGB")
                _buf = BytesIO()
                _img.save(_buf, format="JPEG", quality=90, optimize=True)
                jpeg_bytes = _buf.getvalue()

            b64_image = base64.b64encode(jpeg_bytes).decode("ascii")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an intelligent receipt analysis assistant.\n"
                            "Your goal is to extract clean, structured data from an image of a purchase receipt.\n"
                            "\n"
                            "OUTPUT RULES\n"
                            "- Return ONLY valid JSON (no extra text, no Markdown).\n"
                            "- All date fields MUST be date-only strings in ISO format: \"YYYY-MM-DD\".\n"
                            "  • If the receipt shows a datetime, return only the date part.\n"
                            "  • Normalize day-first dates (e.g., \"17/10/2025\") to \"2025-10-17\".\n"
                            "  • Convert month names (e.g., \"Oct 17, 2025\") to \"2025-10-17\".\n"
                            "  • If a date is missing or ambiguous, use null.\n"
                            "- Every string must be trimmed and reasonably capitalized (title case for names).\n"
                            "- Numeric values (unit_price, quantity, subtotal_amount, tax_amount, discount_amount, total_amount) must be numbers (float).\n"
                            "- If a field is missing, include it with null (or an empty array for items).\n"
                            "\n"
                            "RESPONSE SHAPE (exact keys):\n"
                            "{\n"
                            "  \"store_name\": string | null,\n"
                            "  \"store_address\": string | null,\n"
                            "  \"receipt_number\": string | null,\n"
                            "  \"receipt_date\": \"YYYY-MM-DD\" | null,\n"
                            "  \"due_date\": \"YYYY-MM-DD\" | null,\n"
                            "  \"payment_method\": string | null,\n"
                            "  \"category\": string,\n"
                            "  \"currency\": string | null,\n"
                            "  \"items\": [\n"
                            "    {\n"
                            "      \"item_name\": string,\n"
                            "      \"quantity\": float,\n"
                            "      \"unit_price\": float,\n"
                            "      \"total_price\": float | null\n"
                            "    }\n"
                            "  ],\n"
                            "  \"subtotal_amount\": float | null,\n"
                            "  \"tax_amount\": float | null,\n"
                            "  \"discount_amount\": float | null,\n"
                            "  \"total_amount\": float,\n"
                            "  \"suggestion\": string\n"
                            "}\n"
                            "\n"
                            "Also include a short, helpful suggestion for how the user might tag or manage this receipt "
                            "(e.g., \"Consider categorizing this as Groceries for weekly expense tracking.\")."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract and format this receipt as JSON only."},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                            },
                        ],
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            parsed["category"] = str(parsed.get("category", "Groceries")).strip().capitalize()
            for item in parsed.get("items", []):
                item["item_name"] = str(item.get("item_name", "Unknown item")).strip().capitalize()

            parsed.setdefault(
                "suggestion",
                "You can save this receipt under 'Groceries' or tag it by store name for tracking.",
            )

            print(
                f"[GPT-4o] Category: {parsed.get('category')} | "
                f"Items: {len(parsed.get('items', []))} | "
                f"Total: {parsed.get('total_amount', 'N/A')} | "
                f"Suggestion: {parsed.get('suggestion')}"
            )
            return parsed
        except Exception as err:  # pylint: disable=broad-except
            raise RuntimeError(f"GPT-4o extraction failed: {repr(err)}") from err
