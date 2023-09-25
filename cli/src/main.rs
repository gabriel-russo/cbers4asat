use crate::cbers4asat::Cbers4aAPI;
use clap::Parser;
use core::str::FromStr;
use geojson::{FeatureCollection, JsonObject};
use std::convert::From;
use std::fs::read_to_string;
use std::path::PathBuf;
use std::process;

pub mod cbers4asat;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about)]
struct Args {
    /// E-mail registered in dgi INPE explore (required)
    #[arg(short, long, required = true)]
    user: String,

    /// Search area geometry as GeoJSON file (required)
    #[arg(short, long, value_name = "FILE")]
    geometry: PathBuf,

    /// Collection(s) name(s) (Optional) (Default: All collections)
    #[arg(long, required = true, num_args = 1..=16)]
    collection: Vec<String>,

    /// Start date of the query in the format YYYY-MM-DD (Optional) (Default: TODAY - 1 WEEK)
    #[arg(short, long, default_value = None , required = false)]
    start: Option<String>,

    /// End date of the query in the format YYYY-MM-DD (Optional) (Default: TODAY)
    #[arg(short, long, default_value = None , required = false)]
    end: Option<String>,

    /// Maximum cloud cover in percent. (Optional) (Default: 100)
    #[arg(short, long, default_value = None , required = false)]
    cloud: Option<u8>,

    /// Maximum number of results to return. (Optional) (Default: 25)
    #[arg(short, long, default_value = None , required = false)]
    limit: Option<u16>,

    /// Search scene by id  (Optional) (This argument must be used alone)
    #[arg(short, long, exclusive = true, required = false)]
    id: Option<String>,
}

fn main() {
    let args = Args::parse();

    let api: Cbers4aAPI = Cbers4aAPI { user: args.user };

    let geojson_string: String = match read_to_string(args.geometry) {
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
            args.collection.clone(),
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

        println!(
            "Product {} - Date: {}, Sensor: {}, Satellite: {}",
            id, datetime, sensor, satellite
        );
    }
}
