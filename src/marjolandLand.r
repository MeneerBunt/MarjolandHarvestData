


library(readxl)
library(sf)
library(dplyr)
library(tidyr)
library(mapview)
library(raster)
library(tmap)

tb <- read_excel("C:/Users/602956/Downloads/indeling_marjoland.xlsx", sheet = "Blad3") %>% 
  
  group_by(kas, sectie, rij) %>% gather("point", "value", -kas, -sectie, -rij) %>% 
  separate(point, c("punt", "cor" ), sep = "_" ) %>%
  spread(cor, value) %>% 
  st_as_sf(coords = c("lon", "lat"), crs = 4326) %>%
  summarise(geometry = st_combine(geometry)) %>%
  st_cast("POLYGON")
  
  #st_as_sf(., coords=c("x","y"),crs =4326  ) %>%
  #dplyr::summarise() %>%
  #st_cast( "POLYGON") %>% 
  #st_convex_hull(.) 

p <- mapview( tb, zcol = "kas", alpha.region = 0.4, alpha = 0.3 )
mapshot(p, file = "D:/p13_Marjoland/MarjoLand.html")
#plot(tb)

############
tmap_mode("view")

m <- tm_shape(tb) +
  tm_fill(col="kas", title="Kas",
          popup.vars=c("kas"="kas", "sectie"="sectie", "rij" = "rij")
          
          )+
  tm_borders("gray", lwd = .5) 

tmap_save(m, "D:/p13_Marjoland/MarjoLand.html")













