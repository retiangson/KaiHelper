package nz.yoobee.kaihelper.ui.fragments

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.databinding.FragmentTransactionBinding

class TransactionFragment : Fragment(R.layout.fragment_transaction), DateFilterable {
    private lateinit var binding: FragmentTransactionBinding

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = FragmentTransactionBinding.bind(view)
    }

    override fun onDateFilterChanged(tab: String, year: Int, month: Int, week: Int) {
        // TODO: Handle transaction filtering
    }
}
