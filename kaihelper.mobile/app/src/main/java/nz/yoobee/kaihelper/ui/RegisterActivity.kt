package nz.yoobee.kaihelper.ui

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.UserService
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import nz.yoobee.kaihelper.models.RegisterUserDTO

class RegisterActivity : AppCompatActivity() {

    private lateinit var service: UserService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_register)

        service = ApiClient.retrofit.create(UserService::class.java)

        val username = findViewById<EditText>(R.id.etUsername)
        val fullName = findViewById<EditText>(R.id.etFullName)
        val email = findViewById<EditText>(R.id.etEmail)
        val password = findViewById<EditText>(R.id.etPassword)
        val confirmPassword = findViewById<EditText>(R.id.etConfirmPassword)
        val btnRegister = findViewById<Button>(R.id.btnRegister)
        val tvBackToLogin = findViewById<TextView>(R.id.tvBackToLogin)

        btnRegister.setOnClickListener {
            val dto = RegisterUserDTO(
                username.text.toString(),
                email.text.toString(),
                fullName.text.toString(),
                password.text.toString(),
                confirmPassword.text.toString()
            )

            val call = service.registerUser(dto)
            call.enqueue(object : Callback<Void> {
                override fun onResponse(call: Call<Void>, response: Response<Void>) {
                    if (response.isSuccessful) {
                        Toast.makeText(applicationContext, "Registration successful!", Toast.LENGTH_SHORT).show()
                        finish()
                    } else {
                        Toast.makeText(applicationContext, "Failed to register", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Void>, t: Throwable) {
                    Toast.makeText(applicationContext, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
        }

        tvBackToLogin.setOnClickListener {
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
            finish()
        }
    }
}
