import logging
import arcpy
import os
import yaml
from etl.Assignment11_SpatialEtl import GSheetEtl

#setup
def setup():
    with open('config/wnvoutbreak.yaml') as f:
        config = yaml.safe_load(f)

    # Configure logging — writes to your project directory
    log_path = os.path.join(config['proj_dir'], 'wnv.log')
    logging.basicConfig(
        filename=log_path,
        filemode="w",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.debug("Entered setup function")
    logging.debug("Exited setup function")
    return config

#Buffer Analysis
def buffer_layer(layer_name, distance_ft, config_dict):
    logging.debug(f'Entered buffer_layer for {layer_name}')
    # Define output name and path
    output_name = f"{layer_name}_buffer"
    output_path = os.path.join(config_dict['destination'], output_name)
    distance_str = f"{distance_ft} Feet"

    # Buffer analysis
    arcpy.Buffer_analysis(
        in_features=layer_name,
        out_feature_class=output_path,
        buffer_distance_or_field=distance_str,
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option="ALL"
    )

    logging.info(f"Buffer created for {layer_name}")
    logging.debug(f'Exiting buffer_layer for {layer_name}')

    return output_path

#Loop through layers
def buffer_loop(config_dict):
    layers = [
        "Mosquito_Larval_Sites",
        "Wetlands",
        "Lakes_and_Reservoirs___Boulder_County",
        "OSMP_Properties"
    ]

    while True:
        try:
            distance = float(input("Enter buffer distance in feet for all layers: "))
            break
        except ValueError:
            print("Please enter a valid number.")

    buffer_outputs = []

    for layer in layers:
        output_path = buffer_layer(layer, distance, config_dict)
        buffer_outputs.append(output_path)

    logging.debug(f'Entered buffer_loop')

    return buffer_outputs

#Intersect Analysis
def intersect_buffers(buffer_outputs, config_dict):

    #response = input('Would you like to intersect the buffered layers?(yes/no): ').strip().lower()

    #if response not in ['yes', 'y']:
     #   print ('Okie dokie pardner!')
      #  exit()

    output_name = input("Enter name for the intersect output layer: ")
    output_path = os.path.join(config_dict['destination'], output_name)

    logging.info("Running intersect on buffer layers...")
    arcpy.Intersect_analysis(in_features=buffer_outputs, out_feature_class=output_path)

    logging.info(f"Intersect complete: {output_path}")
    logging.debug(f"Exiting Intersect")
    return output_path

#Spatial Join Intersect and Addresses
def spatial_join(intersect_layer, config_dict):
    address_layer = 'Addresses'
    output_name = "Addresses_At_Risk"
    output_path = os.path.join(config_dict['destination'], output_name)

    logging.debug("Running spatial join between addresses and intersected risk zone...")

    arcpy.analysis.SpatialJoin(
        target_features=address_layer,
        join_features=intersect_layer,
        out_feature_class=output_path,
        join_type="KEEP_COMMON",          # Keep all addresses
        match_option="INTERSECT"
    )

    logging.info(f"Spatial join complete: {output_path}")
    logging.debug(f'Exiting Spatial Join')
    return output_path

def count_at_risk_addresses(joined_fc):
    count = 0
    with arcpy.da.SearchCursor(joined_fc, ["Join_Count"]) as cursor:
        for row in cursor:
            if row[0] and row[0] >= 1:
                count += 1
    logging.info(f"Number of addresses within the risk zone: {count}")

#ETL Function
def etl(config_dict):
    logging.debug('Start etl process...')

    etl_instance = GSheetEtl(config_dict)

    etl_instance.process()

#Erase Function
def erase_avoid_zones(intersect_fc, config_dict):
    avoid_buffer = os.path.join(config_dict['destination'],'Avoid_Points_buffer')
    output_name = 'Risk_Zone_Cleaned'
    output_path = os.path.join(config_dict['destination'], output_name)

    arcpy.analysis.Erase(
        in_features=intersect_fc,
        erase_features=avoid_buffer,
        out_feature_class=output_path
    )
    logging.info(f"Erase complete")
    logging.debug('Analysis Complete!')
    return output_path

def exportMap(config_dict):
    logging.debug("Entered exportMap function")

    # Get project
    aprx_path = os.path.join(config_dict['proj_dir'], 'Programming_Lab1.aprx')
    aprx = arcpy.mp.ArcGISProject(aprx_path)

    # Get layout
    lyt = aprx.listLayouts()[0]

    # Ask for user subtitle
    subtitle = input("Enter a subtitle for your map layout: ")

    # Update the title element
    for el in lyt.listElements("TEXT_ELEMENT"):
        if "Text" in el.name:
            logging.debug(f"Found title element: {el.name}")
            el.text += f"\n{subtitle}"
            logging.info(f"Updated map title with subtitle: {subtitle}")

    # Export the layout to a PDF
    output_pdf = os.path.join(config_dict['proj_dir'], 'WestNileOutbreakMap.pdf')
    lyt.exportToPDF(output_pdf)

    logging.info(f"Exported map to PDF at: {output_pdf}")
    logging.debug("Exiting exportMap function")

def main(config_dict):
    logging.info("Starting West Nile Virus Simulation")

    # Set workspace
    arcpy.env.workspace = config_dict['destination']
    arcpy.env.overwriteOutput = True

    # Load map
    project_path = os.path.join(config_dict['proj_dir'], 'Programming_Lab1.aprx')
    project = arcpy.mp.ArcGISProject(project_path)
    map_obj = project.listMaps()[0]

    # Run geoprocessing
    buffer_outputs = buffer_loop(config_dict)
    intersect_result = intersect_buffers(buffer_outputs, config_dict)
    cleaned_result = erase_avoid_zones(intersect_result, config_dict)
    joined_result = spatial_join(cleaned_result, config_dict)
    count_at_risk_addresses(joined_result)

    map_obj.addDataFromPath(intersect_result)
    map_obj.addDataFromPath(joined_result)
    project.save()

if __name__ == '__main__':
    config_dict = setup()
    print(config_dict)
    etl(config_dict)
    exportMap(config_dict)
    main(config_dict)




