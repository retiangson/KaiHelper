package nz.yoobee.kaihelper.models

data class GroceryDTO(
    val grocery_id: Int?,
    val user_id: Int,
    val category_id: Int?,
    val expense_id: Int?,
    val item_name: String,
    val unit_price: Double,
    val quantity: Double,
    val purchase_date: String,
    val notes: String?,
    val created_at: String?,
    val updated_at: String?,
    val receipt_image: String?,
    val total_cost: Double?,
    val local: Boolean?
)
