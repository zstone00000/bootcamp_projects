library(readxl)
library(tidyr)
library(dplyr)
library(ggplot2)



#Reads in census as semi-structured dataframe
import_census2020 <- function(censuspath) {
  read_excel(censuspath, sheet = "2010, 2020, and Change") 
}

#Finds correct header and start of data, and subsets the 
subsetCensus <- function (censusxl, header = 3, data_start = 4, census_label = 'CT2020') {
  #Get column names from second level of header
  names(censusxl) = as.character(censusxl[header,])
  
  #Slice data
  censusxl = censusxl[data_start:nrow(censusxl),]
  censusxl = censusxl %>% rename(index = `Orig Order`) %>% mutate(index = as.numeric(index))
  
  #Filter the census data
  census_subset = censusxl %>%
    filter(GeoType == census_label)
  
  return(census_subset)
}

parseGeoID <- function (censusdf, geoCol = NA) {
  if (is.na(geoCol)) {geoCol = censusdf$GeoID}
  df = censusdf %>% mutate(StateGID = substring(geoCol, 1,2),
                           CountyGID = substring(geoCol, 3,5),
                           TractGID = substring(geoCol, 6,11))
  return(df)
}

#Converts columns to numeric
census_num <- function (censusdf, omit_cols = c('GeoType','Borough')) {
  df = censusdf
  names.use <- names(df)[!(names(df) %in% omit_cols)]
  df[,names.use] = data.frame(sapply(df[,names.use], as.numeric))
  return(df)
}

#Split and subset census datasets
split_census <- function (splitdf, suffixes = c('_10', '_20', '_Ch')) {
  dflist = list()
  for (i in 1:length(suffixes)) {
    dflist[[i]]  = splitdf %>%
      select(index, Borough, TractGID, GeoID, ends_with(suffixes[i]))
    
    #From the geography section, only index, Borough, TractGID, and GeoID are retained
    #index is kept for reference
    #Borough, TractGID, and GeoID are retained for usefulness for merging dataframes
    #TStateGID is redundant, as it is coextensive with Borough in NYC. StateGID is always 36 (NY)
    #Some TractGIDs are identical for different rows, but they all occcur in distinct burroughs
    #Other dropped columns are null on the census subsets
  }
  names(dflist) = suffixes
  return(dflist)
}


parse_census2020 <- function(censuspath) {
  #Import Excel File
  xl = import_census2020(censuspath)
  
  #subset census data
  censusdf = subsetCensus(xl)
  
  #Parse the GeoID column
  censusdf = parseGeoID(censusdf)
  
  #Convert all to numeric except GeoType and Borough
  censusdf = census_num(censusdf, omit_cols = c('GeoType', 'Borough'))
  
  #split into separate censuses 
  census_list = split_census(censusdf)
  
  return(census_list)
  
}

import_income <- function(filepath) {
  income = read.csv(filepath)
  names(income) = c(income[1,])
  income = income[-1,]
  
  income = income %>%
    mutate(id = gsub(pattern = '1400000US', replacement = '', x = id)) %>%
    census_num(omit_cols = 'Geographic Area Name') %>%
    rename(GeoID = id)
  
  return(income)
}





















  


