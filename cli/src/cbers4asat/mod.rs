pub mod print;
mod stac;

use core::str::FromStr;
use geo::algorithm::bounding_rect::BoundingRect;
use geo::Polygon;
use geojson::{Feature, FeatureCollection, GeoJson};
use stac::query::StacQuery;
use stac::utils::request::is_request_with_error;
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
            Ok(r) => {
                is_request_with_error(&r);

                let txt = &r.text().unwrap();
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

    pub fn query_by_id(&self, scene_id: String) -> FeatureCollection {
        let client = reqwest::blocking::Client::new();

        let collections = stac::metadata::collections::get_all_collections();

        let mut to_search_collection_l2: String = String::new();
        let mut to_search_collection_l4: String = String::new();

        for collection in collections {
            let collection_str_split: Vec<&str> = collection.split('_').collect();
            let collection_satellite: &str = collection_str_split[0];
            let collection_sensor: &str = collection_str_split[1];

            let scene_id_str_split: Vec<&str> = scene_id.split('_').collect();
            let scene_id_satellite: &str = scene_id_str_split[0];
            let scene_id_sensor: &str = scene_id_str_split[1];

            if scene_id_satellite.contains(collection_satellite)
                && scene_id_sensor.contains(collection_sensor)
            {
                to_search_collection_l2 =
                    format!("{collection_satellite}_{collection_sensor}_L2_DN");
                to_search_collection_l4 =
                    format!("{collection_satellite}_{collection_sensor}_L4_DN");
                break;
            }
        }

        let search_link_in_l2 = format!("http://www.dgi.inpe.br/lgi-stac/collections/{to_search_collection_l2}/items/{scene_id}");
        let search_link_in_l4 = format!("http://www.dgi.inpe.br/lgi-stac/collections/{to_search_collection_l4}/items/{scene_id}");

        let mut scene_data: FeatureCollection = FeatureCollection {
            bbox: None,
            features: vec![],
            foreign_members: None,
        };

        for link in [search_link_in_l2, search_link_in_l4] {
            let res = client.get(link).send();

            match res {
                Ok(r) => {
                    is_request_with_error(&r);

                    let txt = &r.text().unwrap();

                    match GeoJson::from_str(txt) {
                        Ok(g) => {
                            match Feature::try_from(g) {
                                Ok(f) => scene_data.features.push(f),
                                Err(_) => continue,
                            };
                        }
                        Err(_) => continue,
                    };
                }
                Err(err) => {
                    eprintln!("Response error: {:?}", err);
                    exit(1);
                }
            };
        }

        scene_data
    }
}
