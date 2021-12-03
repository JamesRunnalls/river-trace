from rivertrace.main import trace

file = "data/20210720/L2NDWI_S2B_MSIL1C_20210720T083559_N0301_R064_T34LDQ_20210720T112210.SAFE.nc"
out_file = "data/20210720/path.json"
water_parameter = "swi"
river = "data/river.geojson"
direction = "N"

trace(file, water_parameter, river, direction, threshold=0, start_jump=0, plots=False, out_file=out_file)















