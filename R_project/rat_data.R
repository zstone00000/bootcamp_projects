library(rjson)
library(data.table)
library(dplyr)

import_ratdata <- function(filepath) {
  rat_data = fromJSON(file = filepath, simplify = TRUE)
  
  data.frame(rat_data[[1]])
  
  json.file = sapply(rat_data, function(x) {
    x[sapply(x, is.null)] <- NA
    unlist(x)
    as.data.frame(x)
  })
  
  
  rat = data.table::rbindlist(json.file, fill= TRUE)
  
  rat = rat %>%
    select(-'location.human_address')
  
  return(rat)
}


