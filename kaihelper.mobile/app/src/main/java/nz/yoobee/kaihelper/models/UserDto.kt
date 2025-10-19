package nz.yoobee.kaihelper.models

/**
 * Represents the payload sent when logging in.
 * Backend expects: { "username_or_email": "...", "password": "..." }
 */
data class LoginRequestDTO(
    val username_or_email: String,
    val password: String
)

/**
 * Generic login response wrapper.
 * Matches backend response: { "success": true, "message": "...", "data": { ...user... } }
 */
data class LoginResponseDTO(
    val success: Boolean,
    val message: String,
    val data: UserDTO? = null,   // ✅ changed from "user" → "data" to match backend ResultDTO
    val code: Int? = null        // optional status code
)

/**
 * Represents the data sent during registration.
 */
data class RegisterUserDTO(
    val username: String,
    val email: String,
    val full_name: String,
    val password: String,
    val confirm_password: String
)

/**
 * Represents a user object returned from backend.
 */
data class UserDTO(
    val id: Int? = null,
    val username: String? = null,
    val email: String? = null,
    val full_name: String? = null,
    val is_active: Boolean = true
)
