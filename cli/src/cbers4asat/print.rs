use geojson::{FeatureCollection, JsonObject};

pub fn print_stac_feature_collection(feat_collection: &FeatureCollection) {
    println!("{} scenes found", feat_collection.features.len());
    println!("---");

    for feat in feat_collection {
        let feat = feat.clone();

        let id: String = match feat.id {
            Some(id) => match id {
                geojson::feature::Id::String(v) => v,
                geojson::feature::Id::Number(n) => n.to_string(),
            },
            _ => String::default(),
        };

        let foreign_props: JsonObject = feat.foreign_members.unwrap();

        let props: JsonObject = feat.properties.unwrap();

        let datetime = props.get("datetime").unwrap();
        let sensor = props.get("sensor").unwrap();
        let satellite = props.get("satellite").unwrap();
        let cloud_cover = props.get("cloud_cover").unwrap();
        let path = props.get("path").unwrap();
        let row = props.get("row").unwrap();
        let collection = foreign_props.get("collection").unwrap();

        println!(
            "Product {} - Date: {}, Sensor: {}, Satellite: {}, Cloud: {}%, Path: {}, Row: {}, Collection: {}",
            id, datetime, sensor, satellite, cloud_cover, path, row, collection
        );
    }
}
