package nz.yoobee.kaihelper.api

import nz.yoobee.kaihelper.models.CategoryDTO
import nz.yoobee.kaihelper.models.ResultDTO
import retrofit2.Call
import retrofit2.http.GET

interface CategoryService {
    @GET("/api/categories/")
    fun getCategories(): Call<ResultDTO<Any>>
}
