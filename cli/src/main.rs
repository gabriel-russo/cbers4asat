pub mod cbers4asat;

use crate::cbers4asat::Cbers4aAPI;
use cbers4asat::print::print_stac_feature_collection;
use chrono::Local;
use clap::Parser;
use core::str::FromStr;
use geo::Polygon;
use geojson::FeatureCollection;
use std::convert::{From, TryInto};
use std::env::current_dir;
use std::fs::{read_to_string, write};
use std::path::{Path, PathBuf};
use std::process::exit;

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

    /// Save the STAC response as GeoJSON
    #[arg(long)]
    save: bool,

    /// Specify where to save the GeoJSON with STAC response (Requires --save)
    #[arg(short, long, requires = "save", value_name = "PATH")]
    output: Option<String>,
}

fn main() {
    let args: Args = Args::parse();

    let api: Cbers4aAPI = Cbers4aAPI {
        user: args.user.unwrap_or_default(),
    };

    if args.id.is_some() {
        let products: FeatureCollection = api.query_by_id(args.id.unwrap_or_default());
        print_stac_feature_collection(&products);
        return;
    }

    let geojson_string: String = match read_to_string(args.geometry.unwrap_or_default()) {
        Ok(content) => content,
        Err(_) => {
            eprintln!("GeoJSON file not found");
            exit(1)
        }
    };

    let geojson: FeatureCollection = match FeatureCollection::from_str(&geojson_string) {
        Ok(feature_collection) => feature_collection,
        Err(_) => {
            eprintln!("Invalid GeoJSON");
            exit(1)
        }
    };

    let mut products: FeatureCollection = FeatureCollection {
        bbox: None,
        features: vec![],
        foreign_members: None,
    };

    for feature in geojson.features {
        let geom: Polygon = match feature.geometry {
            Some(geometry) => {
                let poly: Polygon = match geometry.try_into() {
                    Ok(parsed_geom) => parsed_geom,
                    Err(_) => {
                        eprintln!("Only polygons are allowed");
                        exit(1);
                    }
                };
                poly
            }
            _ => {
                eprintln!("Some geometry in GeoJSON is not a valid.");
                exit(1);
            }
        };

        let response_geojson: FeatureCollection = api.query(
            geom,
            args.collections.clone(),
            args.start.clone(),
            args.end.clone(),
            args.cloud,
            args.limit,
        );

        for feat in response_geojson {
            products.features.push(feat);
        }
    }

    if args.save {
        if !products.features.is_empty() {
            let now: String = Local::now().format("%Y-%m-%d-%Hh%Mm%Ss").to_string();

            let outfile: String = format!("cbers4asat-{now}.geojson");

            let output: PathBuf = match args.output {
                Some(path) => Path::new(&path).join(&outfile),
                None => {
                    let pwd: PathBuf =
                        current_dir().expect("Error while trying to read your directory");

                    pwd.join(&outfile)
                }
            };

            match write(output, products.to_string()) {
                Ok(_) => {
                    println!("---");
                    println!("Output file saved - {}", outfile);
                }
                Err(err) => eprintln!("Error while saving output! Error: {}", err),
            }
        } else {
            println!("Nothing to save.");
        }
    }

    print_stac_feature_collection(&products);
}
