library(tidyr)
library(dplyr)


cty_to_boro <- function(county) {
  switch(county, 'Richmond' = 'Staten Island', 
         'Kings' = 'Brooklyn', 'New York' = 'Manhattan', 
         'Queens' = 'Queens', 'Bronx' = 'Bronx')
}

import_chronic <- function (filepath) {
  chronic = read.csv(filepath)
  
  chronic = chronic %>%
    filter(Primary.County %in% c('Kings', 'New York','Richmond', 'Queens', 'Bronx')) %>%
    mutate(Primary.County = sapply(Primary.County, cty_to_boro)) %>%
    rename(Boro = Primary.County) %>%
    arrange(Year, Boro)
  
  return(chronic)
}

import_totals <- function (filepath) {
  totals = read.csv(filepath)
  
  totals = totals %>%
    filter(County %in% c('Kings', 'New York','Richmond', 'Queens', 'Bronx')) %>%
    mutate(County = sapply(County, cty_to_boro)) %>%
    rename(Boro = County) %>%
    arrange(Year, Boro)
  
  return(totals)
}






