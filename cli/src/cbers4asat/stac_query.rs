use chrono::{DateTime, Duration, Local};
use geojson::{JsonObject, JsonValue};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct StacQuery {
    bbox: [f64; 4],
    datetime: String,
    limit: u16,
    query: JsonObject,
    collections: Vec<String>,
}

impl StacQuery {
    pub fn new(bbox: [f64; 4], collections: Vec<String>) -> StacQueryBuilder {
        StacQueryBuilder {
            bbox,
            collections,
            initial_date: None,
            end_date: None,
            limit: None,
            cloud_cover: None,
        }
    }
}

#[derive(Debug, Default)]
pub struct StacQueryBuilder {
    bbox: [f64; 4],
    collections: Vec<String>,
    initial_date: Option<String>,
    end_date: Option<String>,
    limit: Option<u16>,
    cloud_cover: Option<u8>,
}

// https://rust-unofficial.github.io/patterns/patterns/creational/builder.html
impl StacQueryBuilder {
    pub fn with_initial_date(&mut self, initial_date: String) -> &mut Self {
        self.initial_date = Some(initial_date);
        self
    }

    pub fn with_end_date(&mut self, end_date: String) -> &mut Self {
        self.end_date = Some(end_date);
        self
    }

    pub fn with_limit(&mut self, limit: u16) -> &mut Self {
        self.limit = Some(limit);
        self
    }

    pub fn with_cloud_cover(&mut self, cloud_cover: u8) -> &mut Self {
        self.cloud_cover = Some(cloud_cover);
        self
    }

    pub fn build(&mut self) -> StacQuery {
        let query = {
            let mut q = JsonObject::new();
            let mut q_cloud_cover = JsonObject::new();

            q_cloud_cover.insert(
                String::from("lte"),
                JsonValue::from(self.cloud_cover.unwrap_or(100)),
            );
            q.insert("cloud_cover".to_string(), JsonValue::from(q_cloud_cover));

            q
        };

        let datetime = {
            let local: DateTime<Local> = Local::now();
            let last_week: DateTime<Local> = local - Duration::weeks(1);

            let initial_date = self
                .initial_date
                .clone()
                .unwrap_or(last_week.format("%Y-%m-%d").to_string());
            let end_date = self
                .end_date
                .clone()
                .unwrap_or(local.format("%Y-%m-%d").to_string());

            format!("{initial_date}T00:00:00/{end_date}T23:59:00")
        };

        StacQuery {
            bbox: self.bbox,
            collections: self.collections.clone(),
            datetime,
            limit: self.limit.unwrap_or(25),
            query,
        }
    }
}
