pub mod request {
    use reqwest::blocking::Response;
    use std::process::exit;

    pub fn is_request_with_error(r: &Response) {
        if r.status().is_server_error() {
            eprintln!("Server Error, try again later. Status: {}", r.status());
            exit(1);
        } else if r.status().is_client_error() {
            eprintln!("Client Error. Status: {}", r.status());
            exit(1);
        }
    }
}
