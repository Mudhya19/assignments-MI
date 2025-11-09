# 1. Install dan load library
install.packages("ISLR")
library(ISLR)

# 2. Ambil data dan lihat struktur
dataCredit <- Credit
head(dataCredit)
dim(dataCredit)

# 3. Hitung Mean dan Median
# Mean
mean_Rating <- mean(dataCredit$Rating, na.rm = TRUE)
mean_Cards <- mean(dataCredit$Cards, na.rm = TRUE)
mean_Age <- mean(dataCredit$Age, na.rm = TRUE)

# Median
median_Rating <- median(dataCredit$Rating, na.rm = TRUE)
median_Cards <- median(dataCredit$Cards, na.rm = TRUE)
median_Age <- median(dataCredit$Age, na.rm = TRUE)

# 4. Cetak hasil
cat("Mean of Rating:", mean_Rating, "\n")
cat("Median of Rating:", median_Rating, "\n\n")

cat("Mean of Cards:", mean_Cards, "\n")
cat("Median of Cards:", median_Cards, "\n\n")

cat("Mean of Age:", mean_Age, "\n")
cat("Median of Age:", median_Age, "\n")
