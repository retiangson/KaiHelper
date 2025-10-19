package nz.yoobee.kaihelper.api

import nz.yoobee.kaihelper.models.*
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.POST

interface UserService {
    @POST("api/users/login")
    fun login(@Body dto: LoginRequestDTO): Call<ResultDTO<UserDTO>>

    @POST("api/users/register")
    fun registerUser(@Body dto: RegisterUserDTO): Call<Void>
}
