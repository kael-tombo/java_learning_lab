# Lab 04: REST Data Sources — Mini Project

## Goal
Build an APEX page that calls an external REST API securely, handles file
upload and download, and processes a bulk CSV — in 90 minutes.

## Requirements
- R1: A Web Credential holding an API key, created through the builder.
- R2: A Web Source Module with parameters, referencing the credential.
- R3: A page process calling the module and handling success and error paths.
- R4: Explicit checks on both HTTP status and response body content.
- R5: A file upload validating extension, size, and that it is actually a CSV.
- R6: A file download serving a stored blob with the correct content type.
- R7: An ORDS endpoint exposing two tables with a restricted privilege.
- R8: A bulk CSV processor with row validation and a partial-success report.

## Steps
1. Create a Web Credential for an external sandbox API.
2. Create a Web Source Module with two bindable parameters.
3. Call it from a page process and display the parsed response.
4. Force a 401 and a 500 and confirm both are handled cleanly.
5. Build the upload page with type, size, and content validation.
6. Build the download and verify the file arrives intact.
7. Enable ORDS auto-REST for two tables and restrict privileges.
8. Upload a 5,000-row CSV with deliberate defects and process it.
9. Produce the success/failure report with row-level detail.

## Acceptance criteria
- No secret appears in any page process body.
- Both HTTP error paths produce a clear message, not a stack trace.
- A non-CSV renamed to `.csv` is rejected on content inspection.
- The download returns the correct bytes and content type.
- ORDS access without the required privilege is denied.
- The bulk report distinguishes valid rows, rejected rows, and reasons.

## Stretch
- Add OAuth2 token refresh handling to the Web Source Module.
- Compare a single bulk request against 5,000 individual calls.