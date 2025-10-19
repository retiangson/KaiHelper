package nz.yoobee.kaihelper.ui.dashboard

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.models.GroceryDTO
import java.text.NumberFormat
import java.util.*

/**
 * Adapter for displaying grocery items inside ExpenseDetailActivity.
 * Each item represents a grocery from a specific expense.
 */
class GroceryAdapter(
    private var groceries: List<GroceryDTO>
) : RecyclerView.Adapter<GroceryAdapter.ViewHolder>() {

    class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val name: TextView = itemView.findViewById(R.id.tvGroceryName)
        private val details: TextView = itemView.findViewById(R.id.tvGroceryDetails)

        fun bind(item: GroceryDTO) {
            name.text = item.item_name.ifEmpty { "Unnamed item" }

            val currency = NumberFormat.getCurrencyInstance(Locale("en", "NZ"))
            val total = item.total_cost ?: (item.unit_price * item.quantity)
            val origin = if (item.local == true) "Local / Māori-owned" else "Imported"

            details.text = "($origin) Qty: ${item.quantity} × ${currency.format(item.unit_price)}   " +
                    "Total: ${currency.format(total)}"
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_grocery, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(groceries[position])
    }

    override fun getItemCount() = groceries.size

    fun updateData(newGroceries: List<GroceryDTO>) {
        groceries = newGroceries
        notifyDataSetChanged()
    }
}
