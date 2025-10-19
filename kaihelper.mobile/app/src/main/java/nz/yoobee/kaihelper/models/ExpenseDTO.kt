package nz.yoobee.kaihelper.models

data class ExpenseDTO(
    val expense_id: Int,
    val user_id: Int,
    val category_id: Int?,
    val grocery_id: Int?,
    val amount: Double,
    val description: String?,
    val expense_date: String?,
    val created_at: String?,
    val updated_at: String?,
    val receipt_image: String?,
    val notes: String?,
    val store_name: String?,
    val store_address: String?,
    val receipt_number: String?,
    val payment_method: String?,
    val currency: String?,
    val subtotal_amount: Double?,
    val tax_amount: Double?,
    val discount_amount: Double?,
    val due_date: String?,
    val suggestion: String?,
    val category_name: String?
)
