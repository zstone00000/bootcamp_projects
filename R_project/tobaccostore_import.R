library(tidyr)
library(dplyr)

import_tobac <- function(filepath) {
  tobac = read.csv(filepath)
  tobac_clean = tobac %>%
    filter(License.Status == 'Active') %>%
    select(id = DCA.License.Number, zip = Address.ZIP,
           boro = Address.Borough, tractGID = Census.Tract, long = Longitude, lat = Latitude)
  return(tobac_clean)
}







