package nz.yoobee.kaihelper.models

/**
 * Generic wrapper for API responses.
 * Matches backend JSON: { "success": true, "message": "...", "data": ... }
 */
data class ResultDTO<T>(
    val success: Boolean,
    val message: String,
    val data: T?,       // Can be List<ExpenseDTO>, UserDTO, etc.
    val code: Int?      // Optional status code (e.g., 200, 400)
)
