pub mod collections {
    use geojson::JsonObject;
    use serde::Deserialize;
    use std::process::exit;

    #[derive(Deserialize, Debug)]
    struct CollectionResponse {
        providers: [Collections; 1],
    }

    // http://www.dgi.inpe.br/stac-compose/collections/ -> Deserialize this data
    #[derive(Deserialize, Debug)]
    struct Collections {
        collections: Vec<JsonObject>,
    }

    pub fn get_all_collections() -> Vec<String> {
        let client = reqwest::blocking::Client::new();

        let resp = client
            .get("http://www.dgi.inpe.br/stac-compose/collections")
            .send();

        let response_json: CollectionResponse = match resp {
            Ok(r) => {
                if r.status().is_server_error() {
                    eprintln!("Server Error, try again later. Status: {}", r.status());
                    exit(1);
                } else if r.status().is_client_error() {
                    eprintln!("Client Error. Status: {}", r.status());
                    exit(1);
                }

                let txt = &r.text().unwrap();

                let json: CollectionResponse = serde_json::from_str(&txt).unwrap();

                json
            }
            Err(err) => {
                eprintln!("Response error: {:?}", err);
                exit(1);
            }
        };

        let mut all_collections: Vec<String> = vec![];

        for collection_metadata in &response_json.providers[0].collections {
            let collection_title: String =
                collection_metadata["title"].to_string().replace("\"", "");

            all_collections.push(collection_title);
        }

        all_collections
    }
}
