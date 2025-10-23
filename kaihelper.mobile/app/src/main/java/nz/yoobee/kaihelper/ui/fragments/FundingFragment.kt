package nz.yoobee.kaihelper.ui.fragments

import android.os.Bundle
import android.view.View
import androidx.fragment.app.Fragment
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.databinding.FragmentFundingBinding

class FundingFragment : Fragment(R.layout.fragment_funding), DateFilterable {
    private lateinit var binding: FragmentFundingBinding

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = FragmentFundingBinding.bind(view)
    }

    override fun onDateFilterChanged(tab: String, year: Int, month: Int, week: Int) {
        // TODO: Handle Funding data filters
    }
}
