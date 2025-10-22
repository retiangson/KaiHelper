package nz.yoobee.kaihelper.ui.dashboard

import android.animation.ObjectAnimator
import android.view.LayoutInflater
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.models.GroceryDTO
import kotlin.math.abs

class GroceryAdapter(
    private var groceries: MutableList<GroceryDTO>,
    private val onEdit: (GroceryDTO) -> Unit,
    private val onDelete: (GroceryDTO) -> Unit
) : RecyclerView.Adapter<GroceryAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val layoutForeground: LinearLayout = view.findViewById(R.id.layoutForeground)
        val btnEdit: androidx.appcompat.widget.AppCompatImageButton = view.findViewById(R.id.btnEdit)
        val btnDelete: androidx.appcompat.widget.AppCompatImageButton = view.findViewById(R.id.btnDelete)
        val tvItem: TextView = view.findViewById(R.id.tvGroceryName)
        val tvCost: TextView = view.findViewById(R.id.tvGroceryDetails)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_grocery, parent, false)
        return ViewHolder(view)
    }

    override fun getItemCount() = groceries.size

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val grocery = groceries[position]
        holder.tvItem.text = grocery.item_name
        holder.tvCost.text =
            "Qty: ${grocery.quantity} × $${grocery.unit_price} = $${grocery.total_cost ?: grocery.unit_price * grocery.quantity}"

        // Reset translation each bind
        holder.layoutForeground.translationX = 0f

        var startX = 0f
        var swiping = false

        holder.layoutForeground.setOnTouchListener { v, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    // Stop parent scroll during swipe
                    (v.parent as? RecyclerView)?.requestDisallowInterceptTouchEvent(true)
                    startX = event.rawX
                    swiping = false
                    true
                }

                MotionEvent.ACTION_MOVE -> {
                    val deltaX = event.rawX - startX
                    if (abs(deltaX) > 20) swiping = true

                    // ✅ Allow swipe left (reveal) and right (close)
                    val currentTranslation = holder.layoutForeground.translationX + deltaX
                    holder.layoutForeground.translationX = currentTranslation.coerceIn(-250f, 0f)

                    // update startX continuously so it follows your finger
                    startX = event.rawX
                    true
                }

                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    if (swiping) {
                        val translation = holder.layoutForeground.translationX
                        // ✅ Snap open/close halfway
                        if (translation < -100f) {
                            animateSlide(holder.layoutForeground, -250f)
                        } else {
                            animateSlide(holder.layoutForeground, 0f)
                        }
                    }
                    swiping = false
                    true
                }

                else -> false
            }
        }

        // ✅ Click events
        holder.btnEdit.setOnClickListener {
            animateSlide(holder.layoutForeground, 0f)
            onEdit(grocery)
        }

        holder.btnDelete.setOnClickListener {
            animateSlide(holder.layoutForeground, 0f)
            onDelete(grocery)
        }
    }

    // ✅ Smooth slide animation
    private fun animateSlide(view: View, targetX: Float) {
        ObjectAnimator.ofFloat(view, "translationX", targetX).apply {
            duration = 150   // faster, feels snappier
            start()
        }
    }

    // ✅ Helper methods for data updates
    fun updateData(list: List<GroceryDTO>) {
        groceries.clear()
        groceries.addAll(list)
        notifyDataSetChanged()
    }

    fun updateItem(updated: GroceryDTO) {
        val index = groceries.indexOfFirst { it.grocery_id == updated.grocery_id }
        if (index != -1) {
            groceries[index] = updated
            notifyItemChanged(index)
        }
    }

    fun removeItem(item: GroceryDTO) {
        val index = groceries.indexOf(item)
        if (index != -1) {
            groceries.removeAt(index)
            notifyItemRemoved(index)
        }
    }

    fun getItemAt(position: Int): GroceryDTO = groceries[position]
}
