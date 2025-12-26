# Install dan load library
install.packages("ISLR")
library(ISLR)

# Ambil data Credit dari package ISLR
dataCredit <- Credit
head(dataCredit)

# Hitung quartiles untuk variabel Balance
q1 <- quantile(dataCredit$Balance, probs = 0.25)
q2 <- quantile(dataCredit$Balance, probs = 0.50)
q3 <- quantile(dataCredit$Balance, probs = 0.75)
min_val <- min(dataCredit$Balance)
max_val <- max(dataCredit$Balance)
iqr_val <- q3 - q1

# Cetak hasil quartile
cat("Balance Quartiles:\n")
cat("Minimum:", min_val, "\n")
cat("Q1 (25th):", q1, "\n")
cat("Q2 (50th/Median):", q2, "\n")
cat("Q3 (75th):", q3, "\n")
cat("Maximum:", max_val, "\n")
cat("IQR:", iqr_val, "\n")

# Statistik ringkasan Balance
summary(dataCredit$Balance)

# Ringkasan hasil dalam bentuk data frame
task4_result <- data.frame(
  Statistic = c("Minimum", "Q1", "Q2 (Median)", "Q3", "Maximum", "IQR"),
  Value = c(min_val, q1, q2, q3, max_val, iqr_val)
)
print(task4_result)

# --- BOXPLOT ---
boxplot(dataCredit$Balance,
        main = "Boxplot of Balance",
        ylab = "Balance ($)",
        col = "#A3E4D7",      # warna hijau toska lembut
        border = "#1B4F72",   # warna tepi biru tua
        notch = TRUE)         # tampilkan notch di median
