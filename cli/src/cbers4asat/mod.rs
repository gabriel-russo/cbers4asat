use core::str::FromStr;
use geo::algorithm::bounding_rect::BoundingRect;
use geo::Polygon;
use geojson::{FeatureCollection, GeoJson};
use stac_query_builder::StacQueryBuilder;
use std::process;

pub mod stac_query_builder;

#[derive(Debug)]
pub struct Cbers4aAPI {
    pub user: String,
}

impl Cbers4aAPI {
    pub fn query(
        &self,
        location: &Polygon,
        initial_date: &String,
        end_date: &String,
        cloud: &u8,
        limit: &u16,
        collection: &String,
    ) -> FeatureCollection {
        let (minx, miny) = location.bounding_rect().unwrap().min().x_y();
        let (maxx, maxy) = location.bounding_rect().unwrap().max().x_y();

        let mut stac_request = StacQueryBuilder::new();
        stac_request.set_bbox([minx, miny, maxx, maxy]);
        stac_request.set_datetime(initial_date, end_date);
        stac_request.set_cloud_cover(cloud);
        stac_request.set_limit(*limit);
        stac_request.set_collections(collection);

        let client = reqwest::blocking::Client::new();

        let res = client
            .post("http://www.dgi.inpe.br/lgi-stac/search")
            .json(&stac_request)
            .send();

        let res_geojson: GeoJson = match res {
            Ok(v) => {
                let txt = &v.text().unwrap();
                GeoJson::from_str(txt).unwrap()
            }
            Err(err) => {
                eprintln!("Response error: {:?}", err);
                process::exit(1);
            }
        };

        let res_geojson: FeatureCollection = res_geojson.try_into().unwrap();

        res_geojson
    }
}
