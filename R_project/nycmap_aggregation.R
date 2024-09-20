library(tidyr)
library(dplyr)
library(ggplot2)
library(rjson)
library(geojsonio)
library(sp)
library(rgeos)
library(stringr)
source("./census_import.R") 

census_path = 'data/nyc_decennialcensusdata_2010_2020_change.xlsx'
census_list = parse_census2020(census_path)

census2010 = census_list[['_10']]
census2020 = census_list[['_20']]
census_ch = census_list[['_Ch']]

tract_spdf_data = geojson_read('data/census2020.json', what = 'sp')
tract_spdf = tract_spdf_data

census2020.spdf = merge(tract_spdf, census2020, by.x = 'GEOID', by.y = 'GeoID')

## Grouping procedure manually

# cols2group <- c("BoroName", "NTAName")
# summarize_statement <- 'pop = sum(Pop_20)'
# 
# 
# 
# group_spdf_data <- function (spdf, grp.names) {
#   grouped.df = group_by(spdf@data,spdf@data[,grp.names])
#   return(grouped.df)
# }
# 
# group_spdf_data(census2020.spdf, cols2group) 
# 

Workflow:
  
## Do grouping on the data part of spdf
  #Concatenate the values of the groups to make a single identifier for each group
  #Use this identifier as the row names of the aggregated table
grouped.df = census2020.spdf@data %>%
  group_by(BoroName, NTAName) %>%
  summarize(pop = sum(Pop_20), instpop = sum(InstGQ_20)) %>% ungroup()
row.names(grouped.df) = paste(grouped.df$BoroName,grouped.df$NTAName,sep = '|')

## Construct grouping identifier column for the same groups in the spdf
group.col = census2020.spdf@data %>%
  transmute(BoroName, NTAName, grouping = paste(BoroName, NTAName, sep = '|')) %>% unique()
flagged.spdf = merge(x = census2020.spdf, y = group.col, by = c('BoroName', 'NTAName'))

## Union the regions in the spdf by grouping identifier
  #Reconstruct spdf from unioned sp and grouped df components
grouped.sp = gUnaryUnion(flagged.spdf, id = flagged.spdf$grouping)
grouped.spdf = SpatialPolygonsDataFrame(grouped.sp, grouped.df)

grouped.spdf@data

spplot(grouped.spdf, zcol = 'pop')


#Cannot find way to make function simply since involves unpacking and using tidyr column conventions



