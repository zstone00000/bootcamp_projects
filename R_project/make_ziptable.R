library(readxl)
library(tidyr)
library(dplyr)

make_ziptable <- function(filepath, seed = 19){
  tract_zip = read_excel(filepath)
  tract_zip = tract_zip %>%
    select(tract = TRACT, zip = ZIP) %>%
    mutate(tract = as.numeric(tract), zip = as.numeric(zip))
  
  set.seed(seed)
  zip_table = tract_zip %>%
    group_by(tract) %>%
    summarize(zip = nth(zip, sample(1:n(),size = 1)))
  
  return(zip_table)
}




