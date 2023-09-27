mod stac;

use core::str::FromStr;
use geo::algorithm::bounding_rect::BoundingRect;
use geo::Polygon;
use geojson::{FeatureCollection, GeoJson};
use stac::query::StacQuery;
use std::process::exit;

#[derive(Debug)]
pub struct Cbers4aAPI {
    pub user: String,
}

impl Cbers4aAPI {
    pub fn query(
        &self,
        location: &Polygon,
        collections: Option<Vec<String>>,
        initial_date: Option<String>,
        end_date: Option<String>,
        cloud: Option<u8>,
        limit: Option<u16>,
    ) -> FeatureCollection {
        let (minx, miny) = location.bounding_rect().unwrap().min().x_y();
        let (maxx, maxy) = location.bounding_rect().unwrap().max().x_y();

        let mut stac_request = StacQuery::new([minx, miny, maxx, maxy]);

        if collections.is_some() {
            stac_request.with_collections(collections.unwrap());
        }

        if initial_date.is_some() {
            stac_request.with_initial_date(initial_date.unwrap());
        };

        if end_date.is_some() {
            stac_request.with_end_date(end_date.unwrap());
        }

        if cloud.is_some() {
            stac_request.with_cloud_cover(cloud.unwrap());
        }

        if limit.is_some() {
            stac_request.with_limit(limit.unwrap());
        }

        let stac_request = stac_request.build();

        let client = reqwest::blocking::Client::new();

        let res = client
            .post("http://www.dgi.inpe.br/lgi-stac/search")
            .json(&stac_request)
            .send();

        let res_geojson: GeoJson = match res {
            Ok(v) => {
                if v.status().is_server_error() {
                    eprintln!("Server Error, try again later. Status: {}", v.status());
                    exit(1);
                } else if v.status().is_client_error() {
                    eprintln!("Client Error. Status: {}", v.status());
                    exit(1);
                }

                let txt = &v.text().unwrap();
                GeoJson::from_str(txt).unwrap()
            }
            Err(err) => {
                eprintln!("Response error: {:?}", err);
                exit(1);
            }
        };

        let res_geojson: FeatureCollection = res_geojson.try_into().unwrap();

        res_geojson
    }

    pub fn query_by_id(&self, scene_id: String) {
        todo!()
    }
}
