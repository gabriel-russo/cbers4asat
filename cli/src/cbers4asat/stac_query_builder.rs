use geojson::{JsonObject, JsonValue};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct StacQueryBuilder {
    bbox: [f64; 4],
    datetime: String,
    limit: u16,
    query: JsonObject,
    collections: Vec<String>,
}

impl StacQueryBuilder {
    pub fn new() -> StacQueryBuilder {
        StacQueryBuilder {
            bbox: [0.0, 0.0, 0.0, 0.0],
            datetime: String::from(""),
            limit: 100_u16,
            query: JsonObject::new(),
            collections: vec![],
        }
    }

    pub fn set_bbox(&mut self, bbox: [f64; 4]) {
        self.bbox = bbox;
    }

    pub fn set_datetime(&mut self, initial_date: &String, end_date: &String) {
        self.datetime = format!("{initial_date}T00:00:00/{end_date}T23:59:00");
    }

    pub fn set_limit(&mut self, limit: u16) {
        self.limit = limit;
    }

    pub fn set_cloud_cover(&mut self, cloud_cover: &u8) {
        let cloud_cover_param = {
            let mut obj = JsonObject::new();
            obj.insert(String::from("lte"), JsonValue::from(*cloud_cover));
            obj
        };

        self.query.insert(
            "cloud_cover".to_string(),
            JsonValue::from(cloud_cover_param),
        );
    }

    pub fn set_collections(&mut self, collection: &String) {
        self.collections.push(collection.clone());
    }
}

impl Default for StacQueryBuilder {
    fn default() -> Self {
        StacQueryBuilder::new()
    }
}
