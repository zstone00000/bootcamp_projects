library(sp)

make.fort <- function(spdf) {
  fortified = spdf
  
  # Set IDs
  fortified@data$id <- rownames(fortified@data)
  # fortify 
  fortifieddata <- fortify(fortified, region = "id")
  # merge rotified data with the data from spdf
  fort <- merge(fortifieddata, fortified@data,
                      by = "id")
  return(fort)
}

