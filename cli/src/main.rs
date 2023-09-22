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
#[command(
    author = "Gabriel Russo",
    version,
    about = "Command line interface to query data from CBERS-04A catalog",
    long_about = None
)]
struct Args {
    /// email registered in inpe explore
    #[arg(short, long)]
    user: String,

    /// Search area geometry as GeoJSON file
    #[arg(short, long, value_name = "FILE")]
    geometry: PathBuf,

    /// Collection name
    #[arg(short = None, long)]
    collection: String,

    /// Start date of the query in the format YYYY-MM-DD
    #[arg(short, long)]
    start: String,

    /// End date of the query in the format YYYY-MM-DD
    #[arg(short, long)]
    end: String,

    /// Maximum cloud cover in percent.
    #[arg(short, long)]
    cloud: u8,

    /// Maximum number of results to return. Defaults to 10.
    #[arg(short, long)]
    limit: u16,
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
            &args.start,
            &args.end,
            &args.cloud,
            &args.limit,
            &args.collection,
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
