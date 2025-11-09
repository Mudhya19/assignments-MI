# Install dan load library
install.packages("ISLR")
library(ISLR)
dataCredit <- Credit
head(dataCredit)

# Hitung korelasi dengan metode Pearson
cor_limit_rating <- with(dataCredit, cor(Limit, Rating, method = "pearson"))
cor_age_cards <- with(dataCredit, cor(Age, Cards, method = "pearson"))
cor_income_education <- with(dataCredit, cor(Income, Education, method = "pearson"))

# Cetak hasil korelasi
cat("Limit vs Rating:", round(cor_limit_rating, 3), "\n")
cat("Age vs Cards:", round(cor_age_cards, 3), "\n")
cat("Income vs Education:", round(cor_income_education, 3), "\n")

# Scatter plot + garis tren
par(mfrow = c(1, 3))  # tampilkan 3 grafik sejajar

# 1️⃣ Limit vs Rating
plot(dataCredit$Limit, dataCredit$Rating,
     main = "Limit vs Rating",
     xlab = "Limit", ylab = "Rating",
     col = "#6A5ACD", pch = 16)          # ungu kebiruan
abline(lm(Rating ~ Limit, data = dataCredit), col = "#FF6347", lwd = 2)  # garis merah tomat

# 2️⃣ Age vs Cards
plot(dataCredit$Age, dataCredit$Cards,
     main = "Age vs Cards",
     xlab = "Age", ylab = "Cards",
     col = "#20B2AA", pch = 17)          # hijau toska
abline(lm(Cards ~ Age, data = dataCredit), col = "#8B0000", lwd = 2)     # garis merah gelap

# 3️⃣ Income vs Education
plot(dataCredit$Income, dataCredit$Education,
     main = "Income vs Education",
     xlab = "Income", ylab = "Education",
     col = "#FF69B4", pch = 15)          # pink cerah
abline(lm(Education ~ Income, data = dataCredit), col = "#00008B", lwd = 2)  # garis biru tua

# Kembalikan layout plot
par(mfrow = c(1, 1))

# Ringkasan hasil korelasi
task5_result <- data.frame(
  Pair = c("Limit vs Rating", "Age vs Cards", "Income vs Education"),
  Correlation = c(cor_limit_rating, cor_age_cards, cor_income_education)
)
print(task5_result)
