package nz.yoobee.kaihelper.ui

// --- Android standard library ---
import android.Manifest
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.widget.ProgressBar
import android.widget.Toast

// --- AndroidX & Jetpack ---
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.recyclerview.widget.LinearLayoutManager

// --- Third-party libraries ---
import com.canhub.cropper.CropImageContract
import com.canhub.cropper.CropImageContractOptions
import com.canhub.cropper.CropImageOptions
import com.canhub.cropper.CropImageView
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

// --- Java standard library ---
import java.io.File

// --- Project-specific (KaiHelper) ---
import nz.yoobee.kaihelper.R
import nz.yoobee.kaihelper.api.ApiClient
import nz.yoobee.kaihelper.api.ExpenseService
import nz.yoobee.kaihelper.api.ReceiptService
import nz.yoobee.kaihelper.databinding.ActivityMainBinding
import nz.yoobee.kaihelper.models.ExpenseDTO
import nz.yoobee.kaihelper.models.ResultDTO
import nz.yoobee.kaihelper.ui.ExpenseDetailActivity
import nz.yoobee.kaihelper.ui.dashboard.ExpenseAdapter

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var adapter: ExpenseAdapter
    private val expenseService = ApiClient.retrofit.create(ExpenseService::class.java)
    private var loadingDialog: AlertDialog? = null

    private var photoUri: Uri? = null

    private val takePictureLauncher =
        registerForActivityResult(ActivityResultContracts.TakePicture()) { success: Boolean ->
            if (success && photoUri != null) {
                val capturedFile = copyUriToFile(photoUri!!)
                if (capturedFile != null && capturedFile.exists()) {
                    // ✂️ Launch cropper before uploading with updated API fields
                    cropImageLauncher.launch(
                        CropImageContractOptions(
                            uri = Uri.fromFile(capturedFile),
                            cropImageOptions = CropImageOptions().apply {
                                // ✅ Free-form crop area (no fixed aspect ratio)
                                fixAspectRatio = false
                                guidelines = CropImageView.Guidelines.ON
                                autoZoomEnabled = true
                                allowRotation = true
                                allowFlipping = false

                                // ✅ Show full crop toolbar UI
                                activityTitle = "Crop Receipt"
                                showCropOverlay = true
                                showProgressBar = true
                                allowCounterRotation = true
                                cropMenuCropButtonTitle = "Done"

                                // ✅ Toolbar & UI colors (visible Done/Cancel)
                                activityBackgroundColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.crop_toolbar_bg
                                )
                                activityMenuIconColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.crop_toolbar_text
                                )
                                // ✅ Optional: tweak crop frame colors
                                borderLineColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.white
                                )
                                borderCornerColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.white
                                )
                                guidelinesColor = ContextCompat.getColor(
                                    this@MainActivity, R.color.crop_toolbar_text
                                )
                            }
                        )
                    )
                } else {
                    Toast.makeText(
                        this,
                        "❌ Failed to prepare image for cropping",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            } else {
                Toast.makeText(this, "❌ Capture canceled", Toast.LENGTH_SHORT).show()
            }
        }

    private val cropImageLauncher = registerForActivityResult(CropImageContract()) { result ->
        if (result.isSuccessful) {
            val croppedUri = result.uriContent
            croppedUri?.let {
                val file = copyUriToFile(it)
                if (file != null && file.exists()) {
                    val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
                    val userId = prefs.getInt("user_id", 1)
                    uploadReceipt(userId, file)
                }
            }
        } else {
            Toast.makeText(this, "Crop canceled", Toast.LENGTH_SHORT).show()
        }
    }

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted: Boolean ->
            if (granted) openCamera()
            else Toast.makeText(this, "Camera permission denied", Toast.LENGTH_SHORT).show()
        }

    private fun openCamera() {
        try {
            val imageFile = File.createTempFile("receipt_", ".jpg", cacheDir)
            photoUri = FileProvider.getUriForFile(
                this,
                "${applicationContext.packageName}.provider",
                imageFile
            )
            photoUri?.let { takePictureLauncher.launch(it) }
        } catch (e: Exception) {
            Toast.makeText(this, "Error launching camera: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    // ✅ This must be here — inside the class, but outside onCreate
    private fun uploadReceipt(userId: Int, imageFile: File) {
        val receiptService = ApiClient.retrofit.create(ReceiptService::class.java)

        // Convert userId to RequestBody
        val userIdBody = RequestBody.create("text/plain".toMediaTypeOrNull(), userId.toString())

        // Convert file to RequestBody
        val requestFile = RequestBody.create("image/jpeg".toMediaTypeOrNull(), imageFile)

        // Wrap file as Multipart
        val multipartBody = MultipartBody.Part.createFormData("file", imageFile.name, requestFile)

        // Make API call
        receiptService.uploadReceipt(userIdBody, multipartBody)
            .enqueue(object : Callback<ResponseBody> {
                override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                    hideLoading()
                    if (response.isSuccessful) {
                        Toast.makeText(applicationContext, "✅ Upload success!", Toast.LENGTH_SHORT).show()
                        loadExpenses()
                    } else {
                        Toast.makeText(applicationContext, "⚠️ Upload failed: ${response.code()}", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                    hideLoading()
                    Log.e("Upload", "Network error", t)
                    Toast.makeText(applicationContext, "❌ Network error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // ✅ RecyclerView setup
        adapter = ExpenseAdapter { selectedExpense ->
            val intent = Intent(this, ExpenseDetailActivity::class.java) // ✅ requires import
            intent.putExtra("expense_id", selectedExpense.expense_id)
            startActivity(intent)
        }

        binding.rvExpenses.layoutManager = LinearLayoutManager(this)
        binding.rvExpenses.adapter = adapter
        // Divider removed for clean card look

        // ✅ Floating Action Button
        binding.iconFunding.setOnClickListener {
            Toast.makeText(this, "Funding tapped", Toast.LENGTH_SHORT).show()
        }

        binding.iconTransaction.setOnClickListener {
            Toast.makeText(this, "Transaction tapped", Toast.LENGTH_SHORT).show()
        }

        binding.iconCamera.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Upload Receipt")
                .setItems(arrayOf("Take Photo", "Choose from Gallery")) { _, which ->
                    when (which) {
                        0 -> { // Camera
                            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                                == PackageManager.PERMISSION_GRANTED
                            ) {
                                openCamera()
                            } else {
                                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
                            }
                        }
                        1 -> pickImageLauncher.launch("image/*")
                    }
                }
                .show()
        }

        binding.iconInsight.setOnClickListener {
            Toast.makeText(this, "Insights", Toast.LENGTH_SHORT).show()
        }

        binding.iconOverview.setOnClickListener {
            Toast.makeText(this, "Overview", Toast.LENGTH_SHORT).show()
        }

        // ✅ Pull-to-refresh setup
        binding.swipeRefresh.setOnRefreshListener {
            loadExpenses()  // 🔹 reload data when dragged down
        }

        // ✅ Load expenses on startup
        loadExpenses()
    }

    private fun copyUriToFile(uri: Uri): File? {
        return try {
            val inputStream = contentResolver.openInputStream(uri) ?: return null
            val tempFile = File.createTempFile("upload_", ".jpg", cacheDir)
            tempFile.outputStream().use { output ->
                inputStream.copyTo(output)
            }
            tempFile
        } catch (e: Exception) {
            Log.e("Upload", "Failed to copy URI to file: ${e.message}", e)
            null
        }
    }

    private fun loadExpenses() {
        val prefs = getSharedPreferences("kaihelper_prefs", MODE_PRIVATE)
        val userId = intent.getIntExtra("user_id", prefs.getInt("user_id", 0))
        Log.d("MainActivity", "Loaded userId=$userId")

        expenseService.getExpensesByUser(userId)
            .enqueue(object : Callback<ResultDTO<List<ExpenseDTO>>> {
                override fun onResponse(
                    call: Call<ResultDTO<List<ExpenseDTO>>>,
                    response: Response<ResultDTO<List<ExpenseDTO>>>
                ) {
                    // stop refresh animation
                    binding.swipeRefresh.isRefreshing = false

                    if (response.isSuccessful) {
                        val result = response.body()
                        if (result?.success == true && !result.data.isNullOrEmpty()) {
                            val list = result.data
                            adapter.submitList(list)
                            updateTotals(list)
                            Log.d("MainActivity", "Loaded ${list.size} expenses")
                        } else {
                            adapter.submitList(emptyList())
                            updateTotals(emptyList())
                            Log.w("MainActivity", "No expenses for user $userId")
                        }
                    } else {
                        Log.e("MainActivity",
                            "Server error ${response.code()} — ${response.errorBody()?.string()}")
                    }
                }

                override fun onFailure(call: Call<ResultDTO<List<ExpenseDTO>>>, t: Throwable) {
                    // stop refresh animation on failure too
                    binding.swipeRefresh.isRefreshing = false
                    Log.e("MainActivity", "Network error: ${t.message}", t)
                }
            })
    }

    /** 🔹 Compute and display total spent */
    private fun updateTotals(list: List<ExpenseDTO>) {
        val totalSpent = list.sumOf { it.amount }
        // Clean username greeting
        binding.tvUserName.text = "Welcome, ${intent.getStringExtra("username") ?: "User"}"
        binding.tvTotalSpent.text = "$%.2f".format(totalSpent)
        binding.tvTotalBudget.text = "$1000.00"  // Example static budget
    }

    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            cropImageLauncher.launch(
                CropImageContractOptions(it, CropImageOptions())
            )
        }
    }

    private fun showLoading(message: String = "Uploading receipt...") {
        if (loadingDialog == null) {
            loadingDialog = AlertDialog.Builder(this)
                .setCancelable(false)
                .setView(ProgressBar(this))
                .setMessage(message)
                .create()
        }
        loadingDialog?.show()
    }

    private fun hideLoading() {
        loadingDialog?.dismiss()
        loadingDialog = null
    }

}
