# Install dan load library
install.packages("ISLR")
library(ISLR)
dataCredit <- Credit
head(dataCredit)

# Hitung percentile 10, 37, dan 91
percentile_10 <- quantile(dataCredit$Education, probs = 0.10)
percentile_37 <- quantile(dataCredit$Education, probs = 0.37)
percentile_91 <- quantile(dataCredit$Education, probs = 0.91)

# Tampilkan hasil
cat("Education - 10th Percentile:", percentile_10, "\n")
cat("Education - 37th Percentile:", percentile_37, "\n")
cat("Education - 91st Percentile:", percentile_91, "\n")

# Ringkasan gabungan (dalam satu perintah)
percentiles <- quantile(dataCredit$Education, probs = c(0.10, 0.37, 0.91))
print(percentiles)

# Ringkasan dalam data frame agar lebih rapi
task3_result <- data.frame(
  Percentile = c("10th", "37th", "91st"),
  Value = c(percentile_10, percentile_37, percentile_91)
)
print(task3_result)
