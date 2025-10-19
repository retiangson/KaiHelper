package nz.yoobee.kaihelper.ui

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.GroceryService
import nz.yoobee.kaihelper.databinding.ActivityExpenseDetailBinding
import nz.yoobee.kaihelper.models.GroceryDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.ui.dashboard.GroceryAdapter
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class ExpenseDetailActivity : AppCompatActivity() {
    private lateinit var binding: ActivityExpenseDetailBinding
    private lateinit var adapter: GroceryAdapter
    private val groceryService = ApiClient.retrofit.create(GroceryService::class.java)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityExpenseDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        adapter = GroceryAdapter(emptyList())
        binding.recyclerViewGroceries.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewGroceries.adapter = adapter

        val expenseId = intent.getIntExtra("expense_id", -1)
        if (expenseId != -1) loadGroceries(expenseId)

        //binding.btnBack.setOnClickListener { finish() }
    }

    private fun loadGroceries(expenseId: Int) {
        groceryService.getGroceriesByExpense(expenseId)
            .enqueue(object : Callback<ResultDTO<List<GroceryDTO>>> {
                override fun onResponse(
                    call: Call<ResultDTO<List<GroceryDTO>>>,
                    response: Response<ResultDTO<List<GroceryDTO>>>
                ) {
                    if (response.isSuccessful && response.body()?.success == true) {
                        val groceries = response.body()?.data ?: emptyList()
                        adapter.updateData(groceries)
                        val total = groceries.sumOf { item -> item.total_cost ?: 0.0 }
                        binding.tvTotal.text = "Total: $%.2f".format(total)
                    } else {
                        binding.tvTotal.text = "Failed to load items"
                    }
                }

                override fun onFailure(call: Call<ResultDTO<List<GroceryDTO>>>, t: Throwable) {
                    binding.tvTotal.text = "Error: ${t.message}"
                }
            })
    }
}
