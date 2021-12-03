from rivertrace.main import trace

file = "data/20210725/L2NDWI_S2A_MSIL1C_20210725T083601_N0301_R064_T34LDQ_20210725T104936.SAFE.nc"
out_file = "data/20210725/path.json"
water_parameter = "swi"
river = "data/river.geojson"
direction = "N"

trace(file, water_parameter, river, direction, threshold=0, start_jump=0, plots=True, out_file=out_file)







