import arcpy
import os

# === User Inputs ===
input_folder = r'C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\AdvancedRemoteSensing\FinalProject\AdvancedRS_FinalProject\DEMs'
output_raster = r'C:\Users\benlj\OneDrive\Documents\School\SpringSemester2025\AdvancedRemoteSensing\FinalProject\Mosaics\All9.tif'
target_sr = arcpy.SpatialReference(32613)  # UTM Zone 13N
target_res = 1  # 1 meter

# === Build raster list ===
raster_list = []

for f in os.listdir(input_folder):
    if f.startswith("CWCB_PARK_") and f.lower().endswith('.img'):
        try:
            # Extract the numeric ID: CWCB_PARK_01001.img → 1001
            file_id = int(f.split('_')[-1].split('.')[0])
            if 1001 <= file_id <= 1500:
                raster_list.append(os.path.join(input_folder, f))
        except ValueError:
            continue  # Skip files that don't match the pattern

if not raster_list:
    raise Exception("No rasters found between CWCB_PARK_01001 and CWCB_PARK_01500.")

print(f"🧩 Mosaicking {len(raster_list)} rasters...")

# === Mosaic directly with projection & resolution set ===
arcpy.MosaicToNewRaster_management(
    input_rasters=raster_list,
    output_location=os.path.dirname(output_raster),
    raster_dataset_name_with_extension=os.path.basename(output_raster),
    coordinate_system_for_the_raster=target_sr,
    pixel_type="32_BIT_FLOAT",
    cellsize=target_res,
    number_of_bands=1,
    mosaic_method="MEAN",
    mosaic_colormap_mode="MATCH"
)

print(f"✅ Mosaic complete: {output_raster}")
