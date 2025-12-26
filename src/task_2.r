# Install dan load library
install.packages("ISLR")
library(ISLR)
dataCredit <- Credit
head(dataCredit)

# Fungsi mode sederhana (mengabaikan NA)
get_mode <- function(x) {
  x <- x[!is.na(x)]           
  uniq_vals <- unique(x)    
  counts <- tabulate(match(x, uniq_vals))
  uniq_vals[which.max(counts)]    
}

# Hitung mode untuk tiap variabel
mode_gender  <- get_mode(dataCredit$Gender)
mode_student <- get_mode(dataCredit$Student)
mode_married <- get_mode(dataCredit$Married)

# Tampilkan hasil
cat("Gender - Mode: ", mode_gender, "\n")
cat("Student - Mode:", mode_student, "\n")
cat("Married - Mode:", mode_married, "\n")

# Ringkasan dalam data.frame
task2_result <- data.frame(
  Variable = c("Gender", "Student", "Married"),
  Mode     = c(mode_gender, mode_student, mode_married),
  stringsAsFactors = FALSE
)
print(task2_result)
