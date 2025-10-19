package nz.yoobee.kaihelper.ui

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.UserService
import nz.yoobee.kaihelper.models.LoginRequestDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.models.UserDTO
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class LoginActivity : AppCompatActivity() {

    private lateinit var service: UserService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        // ✅ Initialize Retrofit service
        service = ApiClient.retrofit.create(UserService::class.java)

        // ✅ UI references
        val username = findViewById<EditText>(R.id.etEmail)
        val password = findViewById<EditText>(R.id.etPassword)
        val btnLogin = findViewById<Button>(R.id.btnLogin)
        val btnRegister = findViewById<Button>(R.id.btnRegister)
        val progress = findViewById<ProgressBar>(R.id.progressBar)

        // 🔹 Handle Login Click
        btnLogin.setOnClickListener {
            val emailText = username.text.toString().trim()
            val passwordText = password.text.toString().trim()

            if (emailText.isEmpty() || passwordText.isEmpty()) {
                Toast.makeText(this, "Please fill in both fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnLogin.isEnabled = false
            progress.visibility = View.VISIBLE

            val dto = LoginRequestDTO(emailText, passwordText)
            val call = service.login(dto)

            call.enqueue(object : Callback<ResultDTO<UserDTO>> {
                override fun onResponse(
                    call: Call<ResultDTO<UserDTO>>,
                    response: Response<ResultDTO<UserDTO>>
                ) {
                    progress.visibility = View.GONE
                    btnLogin.isEnabled = true

                    Log.d("LoginActivity", "Response Code: ${response.code()}")

                    if (response.isSuccessful) {
                        val body = response.body()
                        Log.d("LoginActivity", "Response Body: $body")

                        if (body?.success == true && body.data != null) {
                            val user = body.data
                            val userId = user.id ?: 0
                            val usernameValue = user.username ?: emailText

                            // ✅ Save session locally
                            val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
                            prefs.edit()
                                .putInt("user_id", userId)
                                .putString("username", usernameValue)
                                .apply()

                            Log.i(
                                "LoginActivity",
                                "Login success → userId=$userId username=$usernameValue"
                            )

                            Toast.makeText(
                                this@LoginActivity,
                                "Welcome $usernameValue!",
                                Toast.LENGTH_SHORT
                            ).show()

                            // ✅ Navigate to MainActivity
                            val intent = Intent(this@LoginActivity, MainActivity::class.java)
                            intent.putExtra("user_id", userId)
                            intent.putExtra("username", usernameValue)
                            startActivity(intent)
                            finish()

                        } else {
                            // ❌ Invalid credentials or backend rejected
                            val errorMsg = body?.message ?: "Invalid credentials"
                            Toast.makeText(this@LoginActivity, errorMsg, Toast.LENGTH_SHORT).show()
                            Log.w("LoginActivity", "Login failed: $errorMsg")
                        }

                    } else {
                        // ❌ Non-200 HTTP response
                        val errorJson = response.errorBody()?.string()
                        val code = response.code()
                        Toast.makeText(
                            this@LoginActivity,
                            "Server error: $code",
                            Toast.LENGTH_LONG
                        ).show()
                        Log.e("LoginActivity", "Server error $code → $errorJson")
                    }
                }

                override fun onFailure(call: Call<ResultDTO<UserDTO>>, t: Throwable) {
                    progress.visibility = View.GONE
                    btnLogin.isEnabled = true

                    val message = t.localizedMessage ?: "Unknown network error"
                    Toast.makeText(
                        this@LoginActivity,
                        "Connection failed: $message",
                        Toast.LENGTH_LONG
                    ).show()

                    Log.e("LoginActivity", "Network error: $message", t)
                }
            })
        }

        // 🔹 Handle Register Button
        btnRegister.setOnClickListener {
            startActivity(Intent(this, RegisterActivity::class.java))
        }
    }
}
