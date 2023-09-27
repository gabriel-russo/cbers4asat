pub mod cbers4asat;

use crate::cbers4asat::Cbers4aAPI;
use clap::Parser;
use core::str::FromStr;
use geojson::{FeatureCollection, JsonObject};
use std::convert::From;
use std::fs::read_to_string;
use std::path::PathBuf;
use std::process;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about)]
struct Args {
    /// E-mail registered in dgi INPE explore
    #[arg(short, long, required = false)]
    user: Option<String>,

    /// Search area geometry as GeoJSON file.
    #[arg(short, long, required_unless_present = "id", value_name = "FILE")]
    geometry: Option<PathBuf>,

    /// Collection(s) name(s). (Default: All collections)
    #[arg(long, default_value = None, required = false, num_args = 1..=16)]
    collections: Option<Vec<String>>,

    /// Start date of the query in the format YYYY-MM-DD. (Default: TODAY - 1 WEEK)
    #[arg(short, long, default_value = None)]
    start: Option<String>,

    /// End date of the query in the format YYYY-MM-DD. (Default: TODAY)
    #[arg(short, long, default_value = None)]
    end: Option<String>,

    /// Maximum cloud cover in percent. (Default: 100)
    #[arg(short, long, default_value = None)]
    cloud: Option<u8>,

    /// Maximum number of results to return. (Default: 25)
    #[arg(short, long, default_value = None)]
    limit: Option<u16>,

    /// Search scene by id. (This argument must be used alone)
    #[arg(short, long, exclusive = true)]
    id: Option<String>,

    /// Download all returned scenes from query. (Requires --user)
    #[arg(short, long, requires = "user")]
    download: bool,
}

fn main() {
    let args = Args::parse();

    let api: Cbers4aAPI = Cbers4aAPI {
        user: args.user.unwrap_or("".to_string()),
    };

    if args.id.is_some() {
        api.query_by_id(args.id.unwrap());
        return;
    }

    let geojson_string: String = match read_to_string(args.geometry.unwrap()) {
        Ok(res) => res,
        Err(_) => {
            eprintln!("GeoJSON file not found");
            process::exit(1)
        }
    };

    let geojson = match FeatureCollection::from_str(geojson_string.as_str()) {
        Ok(fc) => fc,
        Err(_) => {
            eprintln!("Invalid GeoJSON");
            process::exit(1)
        }
    };

    let mut all_products: FeatureCollection = FeatureCollection {
        bbox: None,
        features: vec![],
        foreign_members: None,
    };

    for feat in geojson.features {
        let geom: geo::Polygon = match feat.geometry.unwrap().try_into() {
            Ok(poly) => poly,
            Err(_) => {
                eprintln!("Some geometry in GeoJSON is not a valid Polygon.");
                process::exit(1);
            }
        };

        let res_geojson = api.query(
            &geom,
            args.collections.clone(),
            args.start.clone(),
            args.end.clone(),
            args.cloud,
            args.limit,
        );

        for feat in res_geojson {
            all_products.features.push(feat);
        }
    }

    println!("{} scenes found", all_products.features.len());
    println!("---");

    for feat in all_products {
        let id = match feat.id.unwrap() {
            geojson::feature::Id::String(v) => v,
            geojson::feature::Id::Number(n) => n.to_string(),
        };

        let props: JsonObject = feat.properties.unwrap();

        let datetime = props.get("datetime").unwrap();
        let sensor = props.get("sensor").unwrap();
        let satellite = props.get("satellite").unwrap();
        let cloud_cover = props.get("cloud_cover").unwrap();
        let path = props.get("path").unwrap();
        let row = props.get("row").unwrap();

        println!(
            "Product {} - Date: {}, Sensor: {}, Satellite: {}, Cloud: {}%, Path: {}, Row: {}",
            id, datetime, sensor, satellite, cloud_cover, path, row
        );
    }
}
