- Go to: https://kroki.io/
- Select ERD
- Copy the below
- Or view at: https://kroki.io/erd/svg/eNqdkTFuwzAMRXefwsiYIEPXLNm69AhBQdAS4RCQZZWkBift3SMbbtzB8dBN1H-kvj4vDsXrZ7VnX41HsCFRfQ_YUDjVO4dKoJb98P2VSQbgCJ6SXeeypUiCYfdTGVv406gmHNty74TQyAPaIhp3pIZduhVAc7Paey5akt6RaqmAAiYtczoOrOR0wTnayFYXIU19VJq_MzlccfSL_ctsn8URvDQ86wlbgpi7hmSDek7eYLKErXdyU9K4gi-u1xyP6GFaK_tFf_8Y45oWX78dj_v6GdwDalu_Pw==

```
[cards]
*id
card_type {label: "case_study|query_in_depth|query_general"}
title {label: "string"}
created_at {label: "timestampz"}
subtitle {label: "string?"}
processing_elapsed_milisecs {label: "int?"}

[responses]
*id
query {label: "string"}
response {label: "string"}
created_at {label: "timestampz"}
source_title {label: "string?"}
source_page_number {label: "string?"}
source_timestamp {label: "string?"}
source_url {label: "string?"}
source_publish_date {label: "timestampz?"}
+card_id {label: "FK"}

cards 1--* responses
```