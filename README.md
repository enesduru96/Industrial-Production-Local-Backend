# Industrial Production Local Backend

A factory backend project that was used as the server to communicate with the local computers and related softwares

Although there are other desktop apps communicating with this backend (warehouse, human resources etc.) written in electron-js and c#,
I am unable to share them due to privacy of the company I worked with.
All the features were added by me exactly as the company requested.
---

This backend program provided services to the other apps such as:
- Adding/editing employees and personnel files
- Adding/editing departments and sub-departments
- Adding/editing workshifts with break times
- Adding/editing sub-companies
- Creating attendance data using a face recognition terminal connected to the entry of the company building
- Calculating salaries depending on the created attendance data, also including the workers' shifts (day/night) including edge cases where some employees worked randomly day and night shifts switching between each other
- Calculating, editing, saving advance payments
- Adding/editing special holidays and salary multipliers
- Adding/editing paid or unpaid leaves
- Printing attendance data with signature fields
- Printing calculated salaries with signature fields
- Printing general expense reports with signature fields
- Defining new materials and product components
- Adding/editing products and its components
- Generating shipments and detailed information
- Adding/editing material provider companies and crucial information
- Adding/editing customers and related information
- Generating material delivery to authorized employees sheets and reports with signature fields
- Getting CNC production information form another company building using google drive syncing methods (specifically requested by the company owner)
and so on.

---

The program also regularly syncs itself to the cloud-deployed version of itself, which is used by the authorized admins to access the databases and all applications from outside the company building.