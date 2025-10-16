"""
ReceiptService (GPT-4o only)
Refactored for clarity, maintainability, and database consistency.
Handles single receipt-level expense with multiple grocery items.
"""

import os
import base64
import json
import time
from datetime import datetime
from openai import OpenAI

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
    """Processes receipts using GPT-4o and synchronizes categories, groceries, and a single receipt-level expense."""

    def __init__(
        self,
        category_service: ICategoryService,
        grocery_service: IGroceryService,
        expense_service: IExpenseService,
    ):
        self.category_service = category_service
        self.grocery_service = grocery_service
        self.expense_service = expense_service

        # 🔐 Ensure OpenAI key is configured
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("Missing OPENAI_API_KEY in .env or environment.")

        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        self.client = OpenAI()

    # ------------------------------------------------------------------
    def process_receipt(self, user_id: int, image_bytes: bytes) -> ResultDTO:
        """
        Main entry:
        - Extract receipt details via GPT-4o.
        - Create or update the expense record (receipt-level).
        - Sync groceries (items) under that expense.
        """
        start_time = time.time()

        try:
            parsed = self._extract_with_gpt(image_bytes)
            items = [ExtractedItemDTO(**item) for item in parsed.get("items", [])]
            total_amount = float(parsed.get("total_amount", 0.0))
            suggestion = parsed.get("suggestion", "")
            category_name = parsed.get("category", "Groceries")

            # 1️⃣ Ensure the receipt's category exists
            category_id = self._ensure_category(category_name)

            # 2️⃣ Create or update a single expense record for this receipt
            expense_result = self._save_receipt_expense(user_id, category_id, total_amount, suggestion)
            if not expense_result.success:
                return ResultDTO.error(f"Failed to record receipt expense: {expense_result.message}")

            expense_id = getattr(expense_result.data, "expense_id", None)

            # 3️⃣ Process all items under this one receipt
            for item in items:
                self._process_item(user_id, item, category_id, expense_id)

            elapsed = round((time.time() - start_time) * 1000, 2)
            print(f"[ReceiptService] ✅ Processed receipt ({category_name}) with {len(items)} items in {elapsed} ms")

            return ResultDTO.ok(
                "Receipt processed successfully",
                ReceiptUploadResponseDTO(
                    category=category_name,
                    total_amount=total_amount,
                    suggestion=suggestion,
                    items=items,
                ),
            )

        except Exception as e:
            return ResultDTO.error(f"Failed to process receipt: {e}")

    # ------------------------------------------------------------------
    def _save_receipt_expense(
        self, user_id: int, category_id: int | None, total_amount: float, comment: str
    ) -> ResultDTO:
        """Create or update a single expense record for the entire receipt."""
        try:
            expense_dto = ExpenseDTO(
                expense_id=None,
                user_id=user_id,
                grocery_id=None,  # this is a receipt-level expense
                category_id=category_id,
                amount=total_amount,
                description=comment or "Auto-added from receipt scan",
                expense_date=datetime.now().date(),
                notes="Auto-added from receipt scan"
            )

            print(
                f"[ReceiptService] 💰 Creating receipt-level expense "
                f"(Category ID: {category_id}, Total: {total_amount})"
            )
            return self.expense_service.add_expense(expense_dto)

        except Exception as e:
            return ResultDTO.error(f"Failed to save receipt expense: {e}")

    # ------------------------------------------------------------------
    def _process_item(self, user_id: int, item: ExtractedItemDTO, category_id: int | None, expense_id: int | None):
        """Add or update groceries belonging to a receipt."""
        grocery_dto = self._build_grocery_dto(user_id, item, category_id)
        grocery_result = self._save_grocery(user_id, grocery_dto)

        if grocery_result.success:
            print(f"[ReceiptService] ✅ Added grocery '{item.item_name}' under receipt expense #{expense_id}")
        else:
            print(f"[Warning] ⚠️ Skipped item '{item.item_name}' – {grocery_result.message}")

    # ------------------------------------------------------------------
    def _ensure_category(self, name: str) -> int | None:
        """Ensure a category exists or create it if missing."""
        try:
            name = name.strip().capitalize()

            result = self.category_service.get_category(name)
            if result.success and result.data:
                category_id = getattr(result.data, "category_id", None)
                print(f"[ReceiptService] 🏷️ Using existing category '{name}' (ID: {category_id})")
                return category_id

            # Create new category
            category_dto = CategoryDTO(
                category_id=None,
                name=name,
                description=f"Auto-added category from receipt import: {name}",
            )
            created = self.category_service.add_category(category_dto)
            if created.success and created.data:
                category_id = getattr(created.data, "category_id", None)
                print(f"[ReceiptService] 🆕 Created new category '{name}' (ID: {category_id})")
                return category_id

            print(f"[Warning] ⚠️ Failed to create category '{name}'")
            return None

        except Exception as e:
            print(f"[Error] ❌ Failed to ensure category '{name}': {e}")
            return None

    # ------------------------------------------------------------------
    def _build_grocery_dto(self, user_id: int, item: ExtractedItemDTO, category_id: int | None) -> GroceryDTO:
        """Convert receipt item to GroceryDTO."""
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

    # ------------------------------------------------------------------
    def _save_grocery(self, user_id: int, dto: GroceryDTO) -> ResultDTO:
        """Add or update a grocery entry."""
        existing = self.grocery_service.find_by_name(user_id, dto.item_name)
        if existing and existing.success and existing.data:
            dto.grocery_id = existing.data.grocery_id
            print(f"[ReceiptService] 🔄 Updating grocery '{dto.item_name}'")
            return self.grocery_service.update_grocery(dto)

        print(f"[ReceiptService] ➕ Adding grocery '{dto.item_name}'")
        return self.grocery_service.add_grocery(dto)

    # ------------------------------------------------------------------
    def _extract_with_gpt(self, image_bytes: bytes) -> dict:
        """
        Use GPT-4o Vision to extract structured receipt data.
        Returns category, items, total amount, and suggestion.
        """
        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a smart receipt analysis assistant. "
                            "Analyze the image of a purchase receipt and return structured JSON. "
                            "Return one high-level category for the receipt (e.g., 'Groceries', 'Gas', 'Shopping', 'Bills', 'Dining'). "
                            "Extract a list of line items (item_name, quantity, unit_price). "
                            "Ensure item_name starts with a capital letter. "
                            "Include the total_amount and a short suggestion message "
                            "for how the user might save or tag this receipt. "
                            "Return JSON only with fields: "
                            "{ category, items:[{item_name,quantity,unit_price}], total_amount, suggestion }."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract and format this receipt clearly as JSON only.",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                            },
                        ],
                    },
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)

            # 🧠 Post-process cleanup
            parsed["category"] = str(parsed.get("category", "Groceries")).strip().capitalize()
            for item in parsed.get("items", []):
                item["item_name"] = str(item.get("item_name", "Unknown item")).strip().capitalize()

            parsed.setdefault(
                "suggestion",
                "You can save this receipt under 'Groceries' or tag it by store name for easy tracking.",
            )

            print(
                f"[GPT-4o] ✅ Category: {parsed.get('category')} | "
                f"Items: {len(parsed.get('items', []))} | "
                f"Total: {parsed.get('total_amount', 'N/A')} | "
                f"Suggestion: {parsed.get('suggestion')}"
            )
            return parsed

        except Exception as e:
            raise RuntimeError(f"GPT-4o extraction failed: {e}")
