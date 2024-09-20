library(stringr)

text = 'UHF NEIGHBORHOOD ZIP CODES
101 Kingsbridge-Riverdale 10463,10471
102 NE Bronx 10464,10466,10469,10470,10475
103 Fordham-Bronx Park 10458,10467,10468
104 Pelham-Throgs Neck 10461,10462,10465,10472,10473
105 Crotona-Tremont 10453,10457,10460
106 High-Bridge-Morisania 10451,10452,10456
107 Hunts Point-Mott Haven 10454,10455,10459,10474
201 Greenpoint 11211,11222
202 Downtown Heightts-Slope 11201,11205,11215,11217,11231
203 Bedford Stuyvesant-Crown Heights 11212,11213,11216,11233,11238
204 East New York 11207,11208
205 Sunset Park 11220,11232
206 Borough Park 11204,11218,11219,11230
207 East Flatbush-Flatbush 11203,11210,11225,11226
208 Canarsie-Flatlands 11234,11236,11239
209 Bensonhurst-Bay Ridge 11209,11214,11228
210 Coney Island-Sheepshead Bay 11223,11224,11229,11235
211 Williamsburg-Bushwick 11206,11221,11237
301 Washington Heights-Inwood 10031,10032,10033,10034,10040
302 Central Harlem-Morningside Heights 10026,10027,10030,10037,10039
303 East Harlem 10029,10035
304 Upper West Side 10023,10024,10025
305 Upper East Side 10021,10028,10044,10128
306 Chelsea-Clinton 10001,10011,10018,10019,10020,10036
307 Gramercy Park-Murray 10010,10016,10017,10022
308 Greenwich Village-Soho 10012,10013,10014
309 Union Square-Lower East Side 10002,10003,10009
310 Lower Manhattan 10004,10005,10006,10007,10038,10280
401 Long Island City-Astoria 11101,11102,11103,11104,11105,11106
402 West Queens 11368,11369,11370,11372,11373,11377,11378
403 Flushing-Clearview 11354,11355,11356,11357,11358,11359,11360
404 Bayside-Littleneck 11361,11362,11363,11364
405 Ridgewood-Forest Hills 11374,11375,11379,11385
406 Fresh Meadows 11365,11366,11367
407 SW Queens 11414,11415,11416,11417,11418,11419,11420,11421
408 Jamaica 11412,11423,11430,11432,11433,11434,11435,11436,11001
409 SE Queens 11004,11005,11411,11413,11422,11426,11427,11428,11429
410 Rockaway 11691,11692,11693,11694,11695,11697
501 Port Richmond 10302,10303,10310
502 Stapleton St. George 10301,10304,10305
503 Willowbrook 10314
504 South Beach-Tottenville 10306,10307,10308,10309,10312'

vect = unlist(strsplit(text, '\n'))

#Extract UHF GeoJoinID
get_geojoin <- function(UHFrow) {
  return(regmatches(UHFrow,regexpr("[0-9]{3}",UHFrow)))
}

#Extract Zipcodes
get_zips <- function(UHFrow) {
  return(str_extract_all(UHFrow, '[0-9]{5}'))
}

#Vector of codes; insert NA for header col
codes = c(NA,get_geojoin(vect))

#Places UHF code next to each zip it covers
unpack_UHF <- function(index) {cbind(rep(codes[index],length(get_zips(vect)[[index]])), get_zips(vect)[[index]])}

#Create table with all conversions
conversion_table = matrix(ncol = 2)

for (index in 2:length(vect)) {
  conversion_table = rbind(conversion_table, unpack_UHF(index))
}

#Convert to df
conversion_table = conversion_table[-1,]
conversion = data.frame(conversion_table)
names(conversion) = c('Geo.Join.ID', 'zip')

write.csv(conversion, file = './data/UHF_zip_conversion.csv')

