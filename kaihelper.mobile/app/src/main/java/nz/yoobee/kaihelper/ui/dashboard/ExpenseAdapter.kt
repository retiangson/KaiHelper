package nz.yoobee.kaihelper.ui.dashboard

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.models.ExpenseDTO
import java.text.NumberFormat
import java.util.*

/**
 * RecyclerView adapter for displaying expenses with click support.
 */
class ExpenseAdapter(
    private val onItemClick: (ExpenseDTO) -> Unit   // ✅ Explicit click listener
) : ListAdapter<ExpenseDTO, ExpenseAdapter.ViewHolder>(ExpenseDiffCallback()) {

    inner class ViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val desc: TextView = itemView.findViewById(R.id.tvExpenseDescription)
        private val date: TextView = itemView.findViewById(R.id.tvExpenseDate)
        private val amount: TextView = itemView.findViewById(R.id.tvExpenseAmount)

        fun bind(item: ExpenseDTO) {
            desc.text = item.store_name ?: "Unnamed expense"
            date.text = "${item.expense_date ?: "Unknown"} | ${item.category_name ?: "Uncategorized"}"

            val formattedAmount = try {
                NumberFormat.getCurrencyInstance(Locale("en", "NZ")).format(item.amount)
            } catch (e: Exception) {
                "$${item.amount}"
            }
            amount.text = formattedAmount

            // ✅ click listener works
            itemView.setOnClickListener { onItemClick(item) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_expense, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ExpenseDiffCallback : DiffUtil.ItemCallback<ExpenseDTO>() {
        override fun areItemsTheSame(oldItem: ExpenseDTO, newItem: ExpenseDTO): Boolean =
            oldItem.expense_id == newItem.expense_id

        override fun areContentsTheSame(oldItem: ExpenseDTO, newItem: ExpenseDTO): Boolean =
            oldItem == newItem
    }
}
