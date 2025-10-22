package nz.yoobee.kaihelper.ui

import android.util.Log
import android.graphics.Canvas
import android.graphics.Color
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.ItemTouchHelper
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import it.xabaras.android.recyclerview.swipedecorator.RecyclerViewSwipeDecorator
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.GroceryService
import nz.yoobee.kaihelper.databinding.ActivityExpenseDetailBinding
import nz.yoobee.kaihelper.models.GroceryDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.ui.dashboard.GroceryAdapter
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import android.widget.EditText
import kotlin.Int
import com.google.gson.Gson
import com.google.gson.GsonBuilder

class ExpenseDetailActivity : AppCompatActivity() {
    private lateinit var binding: ActivityExpenseDetailBinding
    private lateinit var adapter: GroceryAdapter
    private val groceryService = ApiClient.retrofit.create(GroceryService::class.java)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityExpenseDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // ✅ Initialize adapter with callback functions
        adapter = GroceryAdapter(
            groceries = mutableListOf(),
            onEdit = { grocery -> showEditDialog(grocery) },
            onDelete = { grocery -> confirmDelete(grocery) }
        )

        binding.recyclerViewGroceries.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewGroceries.adapter = adapter


        // ✅ Load data
        val expenseId = intent.getIntExtra("expense_id", -1)
        if (expenseId != -1) loadGroceries(expenseId)
    }

    // ✅ Load groceries for selected expense
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
                        val total = groceries.sumOf { it.total_cost ?: 0.0 }
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

    // ✅ Dialog when user swipes an item
    //private fun showSwipeOptions(grocery: GroceryDTO) {
    //    val options = arrayOf("Edit", "Delete")
    //    AlertDialog.Builder(this)
    //        .setTitle("Choose action for '${grocery.item_name}'")
    //        .setItems(options) { _, which ->
    //            when (which) {
    //                0 -> showEditDialog(grocery)
    //                1 -> confirmDelete(grocery)
    //            }
    //        }
    //        .show()
    //}

    // ✅ Edit grocery dialog (Double-safe version)
    private fun showEditDialog(grocery: GroceryDTO) {
        val dialogView = layoutInflater.inflate(R.layout.dialog_edit_grocery, null)
        val etName = dialogView.findViewById<EditText>(R.id.etItemName)
        val etQty = dialogView.findViewById<EditText>(R.id.etQuantity)
        val etPrice = dialogView.findViewById<EditText>(R.id.etUnitPrice)

        etName.setText(grocery.item_name)
        etQty.setText(grocery.quantity.toString())
        etPrice.setText(grocery.unit_price.toString())

        AlertDialog.Builder(this)
            .setTitle("Edit Grocery")
            .setView(dialogView)
            .setPositiveButton("Save") { _, _ ->
                val qtyInput = etQty.text.toString().trim()
                val priceInput = etPrice.text.toString().trim()
                val nameInput = etName.text.toString().trim()

                // Safely parse numbers, fallback to current values
                val quantity = qtyInput.toDoubleOrNull() ?: grocery.quantity
                val unitPrice = priceInput.toDoubleOrNull() ?: grocery.unit_price
                val totalCost = quantity * unitPrice

                val createdDate = grocery.created_at?.substring(0, 10)
                val updatedDate = java.time.LocalDate.now().toString()

                // Build updated grocery object
                val updated = grocery.copy(
                    item_name = if (etName.text.toString().isNotEmpty()) etName.text.toString() else grocery.item_name,
                    quantity = quantity,
                    unit_price = unitPrice,
                    total_cost = totalCost,
                    created_at = createdDate,
                    updated_at = updatedDate
                )
                Log.d("API_RESPONSE", "Response body: ${Gson().toJson(grocery)}")
                Log.d("API_RESPONSE", "Response body: ${Gson().toJson(updated)}")
                groceryService.updateGrocery(updated)
                    .enqueue(object : Callback<ResultDTO<GroceryDTO>> {
                        override fun onResponse(
                            call: Call<ResultDTO<GroceryDTO>>,
                            response: Response<ResultDTO<GroceryDTO>>
                        ) {
                            if (response.isSuccessful && response.body()?.success == true) {
                                adapter.updateItem(updated)
                                Toast.makeText(
                                    this@ExpenseDetailActivity,
                                    "✅ Grocery updated",
                                    Toast.LENGTH_SHORT
                                ).show()
                            } else {
                                Toast.makeText(
                                    this@ExpenseDetailActivity,
                                    "⚠️ Failed to update: ${response.errorBody()?.string()}",
                                    Toast.LENGTH_SHORT
                                ).show()
                            }
                        }

                        override fun onFailure(call: Call<ResultDTO<GroceryDTO>>, t: Throwable) {
                            Toast.makeText(
                                this@ExpenseDetailActivity,
                                "❌ Error: ${t.message}",
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    })
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    // ✅ Confirm deletion
    private fun confirmDelete(grocery: GroceryDTO) {
        AlertDialog.Builder(this)
            .setTitle("Delete Grocery")
            .setMessage("Are you sure you want to delete '${grocery.item_name}'?")
            .setPositiveButton("Delete") { _, _ ->
                groceryService.deleteGrocery(grocery.grocery_id ?: 0)
                    .enqueue(object : Callback<ResultDTO<Boolean>> {
                        override fun onResponse(
                            call: Call<ResultDTO<Boolean>>,
                            response: Response<ResultDTO<Boolean>>
                        ) {
                            if (response.isSuccessful && response.body()?.success == true) {
                                adapter.removeItem(grocery)
                                Toast.makeText(this@ExpenseDetailActivity, "🗑️ Grocery deleted", Toast.LENGTH_SHORT).show()
                            } else {
                                Toast.makeText(this@ExpenseDetailActivity, "⚠️ Delete failed", Toast.LENGTH_SHORT).show()
                            }
                        }

                        override fun onFailure(call: Call<ResultDTO<Boolean>>, t: Throwable) {
                            Toast.makeText(this@ExpenseDetailActivity, "❌ Error: ${t.message}", Toast.LENGTH_SHORT).show()
                        }
                    })
            }
            .setNegativeButton("Cancel", null)
            .show()
    }
}
