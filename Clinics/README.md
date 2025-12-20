# API Summary



|Category      | Endpoint                     | Method|        Auth        |

|--------------------------------------------------------------------------|

|Clinics       | /clinics                     | POST  |        YES         |

|Clinics       | /clinics/{clinic\_id}         | GET   |        NO          |

|Clinics       | /clinics/by-name/{name}      | GET   |        NO          |

|Clinics       | /clinics/by-phone/{phone}    | GET   |        NO          |

|Clinics       | /clinics/owner/{owner\_id}    | GET   |        NO          |

|Clinics       | /clinics                     | GET   |        NO          |

|Clinics       | /clinics/{clinic\_id}         | PATCH |        YES(Owner)  |

|Clinics       | /clinics/{clinic\_id}         | DELETE|        YES(Owner)  |

|Images        | /images/clinics/{clinic\_id}  | POST  |        YES         |

|Images        | /images/clinics/{clinic\_id}  | GET   |        NO          |

|Images        | /images/{image\_id}           | GET   |        NO          |

|Images        | /images/{iamge\_id}           | PATCH |        YES         |

|Images        | /images/{image\_id}           | DELETE|        YES         |

|Areas         | /areas/areas                 | GET   |        NO          |

|Areas         | /areas/autocomplete          | GET   |        NO          |

|Areas         | /areas/{area\_id}             | GET   |        NO          |

|Areas         | /areas/admin                 | POST  |        Admin       |

|Areas         | /areas/admin/{area\_id}       | PATCH |        Admin       |

|Areas         | /areas/admin/{area\_id}/re-geocode| POST |     Admin       |

|Areas         | /areas/admin/{area\_id}       | DELETE|        Admin       |





----------------------------------------------------------------------------



# Create a Clinic



Create a new clinic owned by the authenticated user.

The backend validates phone numbers, optional coordinates and address.

If configured, geocoding may update formatted\_address, latitude and longitude.



##### URL

POST /clinics



##### Auth

Requires authentication.

Frontend must send: 

&nbsp;	Authorization: Bearer <jwt-token>



##### Headers

Content-Type : application/json

Authorization : Bearer <token>



##### Request Body

{

&nbsp; "owner\_id": 1,

&nbsp; "name": "Golden Vet",

&nbsp; "description": "Good clinic",

&nbsp; "phone": "0771234567",

&nbsp; "address": "Kurunegala",

&nbsp; "profile\_pic\_url": null,

&nbsp; "area\_id": null,

&nbsp; "latitude": null,

&nbsp; "longitude": null

}



##### Validation Rules



name: required, <= 100 chars

phone: auto-normalized to +94... format in backend

address: optional

latitude/longitude: Optional, but must be valid float if present

owner\_id: must match authenticated user(else 403)



##### Success Response(201 created)



{

&nbsp; "id": 23,

&nbsp; "owner\_id": 1,

&nbsp; "name": "Golden Vet",

&nbsp; "description": "Good clinic",

&nbsp; "phone": "+94771234567",

&nbsp; "address": "Kurunegala",

&nbsp; "formatted\_address": null,

&nbsp; "latitude": null,

&nbsp; "longitude": null,

&nbsp; "geocoded\_at": null,

&nbsp; "geocode\_source": null,

&nbsp; "profile\_pic\_url": null,

&nbsp; "area": null,

&nbsp; "images": \[],

&nbsp; "is\_active": true,

&nbsp; "created\_at": "2025-12-03T10:01:30Z",

&nbsp; "updated\_at": "2025-12-03T10:01:30Z"

}



##### cURL example



curl -X POST "http://localhost:8000/clinics" \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{"owner\_id":1,"name":"Golden Vet","description":"Good clinic","phone":"0771234567","address":"Kurunegala"}'



##### Error Response



###### 400 bad request



invalid phone number, invalid coordinates, Data constraint failure



###### 403 Forbidden



User is not owner



###### 404 not found



Area does not exist



----------------------------------------------------------------------------



# GET Clinic by Id



Retrieve a single clinic by its id



##### URL



GET /clinics/{clinic\_id}



##### Path parameters



|Name      | Type  | Required|        Description        |

|--------------------------------------------------------|

|clinic\_id | int   | Yes     | Id for the clinic to fetch|



##### Response: 200 OK





{

  "id": 23,

  "owner\_id": 1,

  "name": "Golden Vet",

  "description": "Good clinic",

  "phone": "+94771234567",

  "address": "Kurunegala",

  "formatted\_address": null,

  "latitude": null,

  "longitude": null,

  "geocoded\_at": null,

  "geocode\_source": null,

  "profile\_pic\_url": null,

  "area": null,

  "images": \[],

  "is\_active": true,

  "created\_at": "2025-12-03T10:01:30Z",

  "updated\_at": "2025-12-03T10:01:30Z"

}

##### &nbsp;

##### cURL Example



curl "http://localhost:8000/clinics/5"



&nbsp;

##### Error Response



###### 404 not found



Clinic does not exist with this id



-----------------------------------------------------------------------



# GET Clinic by Name



Retrieve a single clinic by its exact Name



##### URL



GET /clinics/by-name/{name}



##### Path parameters



|Name      | Type  | Required|        Description        |

|--------------------------------------------------------|

|name      | str   | Yes     | Name for the clinic to fetch|



##### Response: 200 OK





{

  "id": 23,

  "owner\_id": 1,

  "name": "Golden Vet",

  "description": "Good clinic",

  "phone": "+94771234567",

  "address": "Kurunegala",

  "formatted\_address": null,

  "latitude": null,

  "longitude": null,

  "geocoded\_at": null,

  "geocode\_source": null,

  "profile\_pic\_url": null,

  "area": null,

  "images": \[],

  "is\_active": true,

  "created\_at": "2025-12-03T10:01:30Z",

  "updated\_at": "2025-12-03T10:01:30Z"

}

##### 

##### cURL Example

curl "http://localhost:8000/clinics/by-name/Golden%20Vet"



##### Error Response



###### 404 not found



Clinic does not exist with this name



----------------------------------------------------------------------



# GET Clinic by phone



Retrieve a single clinic by its phone number



##### URL



GET /clinics/by-phone/{phone}



##### Path parameters



|Name      | Type  | Required|        Description        |

|--------------------------------------------------------|

|phone     | str   | Yes     | phone number for the clinic to fetch|



##### Response: 200 OK





{

  "id": 23,

  "owner\_id": 1,

  "name": "Golden Vet",

  "description": "Good clinic",

  "phone": "+94771234567",

  "address": "Kurunegala",

  "formatted\_address": null,

  "latitude": null,

  "longitude": null,

  "geocoded\_at": null,

  "geocode\_source": null,

  "profile\_pic\_url": null,

  "area": null,

  "images": \[],

  "is\_active": true,

  "created\_at": "2025-12-03T10:01:30Z",

  "updated\_at": "2025-12-03T10:01:30Z"

}



##### cURL Example

curl "http://localhost:8000/clinics/by-phone/0771234567"

#####  

##### Error Response



###### 404 not found



Clinic does not exist with this phone number



-------------------------------------------------------------------------------



# GET Clinic by Owner\_Id



Retrieve a single clinic by  owner\_id



##### URL



GET /clinics/owner/{owner\_id}



##### Path parameters



|Name      | Type  | Required|        Description        |

|--------------------------------------------------------|

|owner\_id | int   | Yes     | Owner\_Id for the clinic to fetch|



##### Response: 200 OK





{

  "id": 23,

  "owner\_id": 1,

  "name": "Golden Vet",

  "description": "Good clinic",

  "phone": "+94771234567",

  "address": "Kurunegala",

  "formatted\_address": null,

  "latitude": null,

  "longitude": null,

  "geocoded\_at": null,

  "geocode\_source": null,

  "profile\_pic\_url": null,

  "area": null,

  "images": \[],

  "is\_active": true,

  "created\_at": "2025-12-03T10:01:30Z",

  "updated\_at": "2025-12-03T10:01:30Z"

}

#####  

##### cURL Example

curl "http://localhost:8000/clinics/owner/1?limit=20\&offset=0"



##### Error Response



###### 404 not found



Clinic does not exist with this owner\_id



-------------------------------------------------------------------------------

# Update Clinic(patch)



Update one or more fields of an existing clinic.  

Only provided fields will be updated.



##### URL

PATCH /clinics/{clinic\_id}



##### Auth

\- Required: Yes  

\- Must be the owner of the clinic.



##### Path Parameters



| Name        | Type | Required | Description |

|-------------|------|----------|-------------|

| clinic\_id   | int  | Yes      | Clinic ID |



##### Request Body (any field optional)

```json



{

&nbsp; "name": "Updated Name",

&nbsp; "description": "New description",

&nbsp; "phone": "0771234567",

&nbsp; "address": "New Road",

&nbsp; "profile\_pic\_url": "http://example.com/pic.jpg",

&nbsp; "area\_id": 3,

&nbsp; "latitude": 6.9,

&nbsp; "longitude": 79.8

}

# 

##### Response: 200 Ok



{

  "id": 23,

  "owner\_id": 1,

  "name": "Golden Vet",

  "description": "Good clinic",

  "phone": "+94771234567",

  "address": "Kurunegala",

  "formatted\_address": null,

  "latitude": null,

  "longitude": null,

  "geocoded\_at": null,

  "geocode\_source": null,

  "profile\_pic\_url": null,

  "area": null,

  "images": \[],

  "is\_active": true,

  "created\_at": "2025-12-03T10:01:30Z",

  "updated\_at": "2025-12-03T10:01:30Z"

}





##### 

##### cURL Example

&nbsp;curl -X PATCH "http://localhost:8000/clinics/10" \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{ "name": "New Clinic Name" }'





##### Error Response



###### 400 bad request



invalid field or validation error



###### 403 Forbidden



User is not the owner of the clinic 



###### 404 not found



Clinic does not exist with this id





--------------------------------------------------------------------------



# Delete a clinic





Delete a clinic permanently.



##### URL

DELETE /clinics/{clinic\_id}



##### Auth

\- Required: Yes  

\- Only the clinic owner can delete it.



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|

| clinic\_id | int  | Yes      | Clinic to delete |



##### Response: 204 No Content

No response body.



##### cURL Example

curl -X DELETE "http://localhost:8000/clinics/10"



##### Error Responses



###### &nbsp;404 Not Found

&nbsp;Clinic does not exist 



###### &nbsp;403 Forbidden 

&nbsp;User is not the owner 



###### &nbsp;401 Unauthorized

&nbsp;Authentication required 



-----------------------------------------------------------------------------



# List of Clinics



Retrieve a list of clinics.  

Supports pagination and multiple optional filters.



##### URL

GET /clinics



##### Auth

Required: No



##### Query Parameters



| Name          | Type      | Required | Default | Description |

|---------------|-----------|----------|---------|-------------|

| limit         | int       | No       | 20      | Max items to return (1–100) |

| offset        | int       | No       | 0       | Number of items to skip |

| owner\_id      | int       | No       | null    | Filter by clinic owner |

| area\_id       | int       | No       | null    | Filter by area |

| name          | string    | No       | null    | Filter by clinic name  |

| phone         | string    | No       | null    | Filter by phone number |

| is\_active     | bool      | No       | null    | Filter by activation status |

| with\_related  | bool      | No       | true    | Include related models (area, owner, images) |



##### Example Requests



1\) Get all clinics

&nbsp; GET/clinics/



2\) Pagination (10 results, skip 20)

&nbsp; GET/clinics/?limit=10\&offset=20



3\) Filter by owner

&nbsp; GET/clinics/owner\_id=1



4\) Filter by name

&nbsp; GET/clinics/?name=bawbaw



5\) Multiple Filters

&nbsp; GET/clinics/?area\_id=5\&is\_active=true\&limit=50



##### Response: 200 Ok



{

  "id": 23,

  "owner\_id": 1,

  "name": "Golden Vet",

  "description": "Good clinic",

  "phone": "+94771234567",

  "address": "Kurunegala",

  "formatted\_address": null,

  "latitude": null,

  "longitude": null,

  "geocoded\_at": null,

  "geocode\_source": null,

  "profile\_pic\_url": null,

  "area": null,

  "images": \[],

  "is\_active": true,

  "created\_at": "2025-12-03T10:01:30Z",

  "updated\_at": "2025-12-03T10:01:30Z"

}



##### cURL Example

curl "http://localhost:8000/clinics?limit=20\&offset=0\&with\_related=true"



-------------------------------------------------------------------------------------

# Upload Image for a Clinic



Upload a new image for the given clinic



##### URL



POST /images/clinic/{clinic\_id}



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|

| clinic\_id | int  | Yes      | id for upload image |\\



##### Body

**multipart/form-data** with the single file field **file**



##### Form fields

file(required) - the image file



##### Validation Rules

* Allowed MIME types : image/jpeg, image/png, image/webp
* Max size: 5MB (5 \* 1024 \* 1024)
* The file must be a valid image(PIL verification)



##### Success Response : 201 Created



{

&nbsp; "id": 42,

&nbsp; "clinic\_id": 123,

&nbsp; "filename": "9a0a5149d9f1451e9a3d5f288947d5c8.png",

&nbsp; "original\_filename": "photo.png",

&nbsp; "url": "https://cdn.example.com/clinic-images/9a0a5...png",

&nbsp; "content\_type": "image/png",

&nbsp; "uploaded\_at": "2025-07-29T12:34:56Z"

}





##### cURL example

curl -X POST http://localhost:8000/images/clinics/5 \\

&nbsp; -F "file=@photo.png"





##### Error Responses



###### 404 Not Found

 Clinic does not exist



###### 500 Internal server error

&nbsp;Storage upload failed



###### 400 Bad Request

&nbsp;Unsupported file type, file too large, invalid/corrupted image





----------------------------------------------------------------------------------------

# 

# List images for a clinic



Return a list of images associated with a clinic



##### URL



GET /images/clinics/{clinic\_id}



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|

| clinic\_id | int  | Yes      | id for list images |



##### Success Response: 200 OK



\[

&nbsp; {

&nbsp;   "id": 42,

&nbsp;   "clinic\_id": 123,

&nbsp;   "filename": "9a0a5149d9f1451e9a3d5f288947d5c8.png",

&nbsp;   "original\_filename": "photo.png",

&nbsp;   "url": "https://cdn.example.com/clinic-images/9a0a5...png",

&nbsp;   "content\_type": "image/png",

&nbsp;   "uploaded\_at": "2025-07-29T12:34:56Z"

&nbsp; },

&nbsp; {

&nbsp;   "id": 43,

&nbsp;   "clinic\_id": 123,

&nbsp;   "filename": "b2c3d4e5f6.png",

&nbsp;   "original\_filename": "other.jpg",

&nbsp;   "url": "https://cdn.example.com/clinic-images/b2c3...png",

&nbsp;   "content\_type": "image/jpeg",

&nbsp;   "uploaded\_at": "2025-07-28T09:10:11Z"

&nbsp; }

]



##### cURL example

curl "http://localhost:8000/images/clinics/5"



##### Error Responses



###### 404 Not Found

 Clinic does not exist





---------------------------------------------------------------------------------



# Get a single image record



Return metadata for an image record by id



##### URL



GET /images/{image\_id}



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|

| image\_id | int  | Yes      | id for return image metadata |





##### Success Response : 200 OK



{

  "id": 42,

  "clinic\_id": 123,

  "filename": "9a0a5149d9f1451e9a3d5f288947d5c8.png",

  "original\_filename": "photo.png",

  "url": "https://cdn.example.com/clinic-images/9a0a5...png",

  "content\_type": "image/png",

  "uploaded\_at": "2025-07-29T12:34:56Z"

}



##### cURL example

curl "http://localhost:8000/images/12"



##### Error Responses



###### 404 Not Found

 image not found

--------------------------------------------------------------------------------------

# Update image metadata or replace file



Partially update an image. 



Two modes:



1\. Provide a new file (multipart) - will upload new file, remove the old one from storage, and update filename, URL, content\_type, original\_filename.



2\. Provide form fields for URL, content\_type, original\_filename when not uploading a new file (useful for linking external URLs or changing metadata).





##### URL



PATCH /images/{image\_id}



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|

| image\_id | int  | Yes      | id for update image metadata |



If replacing file: multipart/form-data with file (and optional original\_filename form field)



• If updating metadata only: use multipart/form-data with url, content\_type, original\_filename form fields.



##### Validation Rules

* Allowed MIME types : image/jpeg, image/png, image/webp
* Max size: 5MB (5 \* 1024 \* 1024)
* The file must be a valid image(PIL verification)
* If file is provided, url must not be provided



##### Success Response : 200 OK

Returns the updated ClinicImage object



{

  "id": 42,

  "clinic\_id": 123,

  "filename": "9a0a5149d9f1451e9a3d5f288947d5c8.png",

  "original\_filename": "photo.png",

  "url": "https://cdn.example.com/clinic-images/9a0a5...png",

  "content\_type": "image/png",

  "uploaded\_at": "2025-07-29T12:34:56Z"

}



##### cURL example



Update only metadata:
curl -X PATCH "http://localhost:8000/images/12" \\

&nbsp; -F "original\_filename=newname.png"



###### Replace the file:

curl -X PATCH "http://localhost:8000/images/12" \\

&nbsp; -F "file=@new\_photo.png"



##### Error Responses



###### 404 Not Found

 image not found



###### 500 Internal server error

 Storage failure when replacing file



###### 400 Bad Request

 Unsupported file type, file too large, invalid/corrupted image, url provided together with file



-------------------------------------------------------------------------------------



# Delete image



Delete an image by id.

The endpoint removes the storage object and the DB record.



##### URL



DELETE /images/{image\_id}



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|8

| image\_id | int  | Yes      | id for delete an image |



##### Success Response: 204 No Content



##### cURL example

curl -X DELETE "http://localhost:8000/images/12"



##### Error Responses



###### 403 Forbidden

&nbsp;Current user is not the owner of the clinic



###### 404 Not Found

 image not found



###### 500 Internal server error

 failed to delete from storage or DB



-------------------------------------------------------------------------------------------



# List areas



Returns a paginated list of areas, optionally filtered by name or region



##### URL

GET /areas/areas





##### Query Parameters



| Name          | Type      | Required | Default | Description |

|---------------|-----------|----------|---------|-------------|

| limit         | int       | No       | 50      | Max number of results(1–200) |

| offset        | int       | No       | 0       | Number of items to skip |

| name          | string    | No       | -       | Filter areas by substring(case-insensitive)  |

|main\_region    | string    | No       | -       |Filter by region |





##### Success Response : 200 OK



\[

&nbsp; {

&nbsp;   "id": 1,

&nbsp;   "name": "Colombo",

&nbsp;   "normalized\_name": "colombo",

&nbsp;   "main\_region": "Western",

&nbsp;   "formatted\_address": "Colombo, Sri Lanka",

&nbsp;   "latitude": 6.9271,

&nbsp;   "longitude": 79.8612,

&nbsp;   "geocoded\_at": "2024-01-01T10:00:00Z",

&nbsp;   "geocode\_source": "opencage",

&nbsp;   "created\_at": "2024-01-01T10:00:00Z"

&nbsp; }

]



##### cURL example

curl "http://localhost:8000/areas?limit=50\&offset=0"



-------------------------------------------------------------------------------------------

# &nbsp;Autocomplete areas



Returns quick suggestions for dropdowns/search bars



##### URL

GET /areas/autocomplete



##### Query Parameters



| Name          | Type      | Required | Description |

|---------------|-----------|----------|-------------|

| limit         | int       | No       |10 suggestions default |

| q             | string    | Yes      | Number of items to skip |



##### Example Request



GET /areas/autocomplete/?q=col



##### Success Response : 200 OK



\[

  {

    "id": 1,

    "name": "Colombo",

    "normalized\_name": "colombo",

    "main\_region": "Western",

    "formatted\_address": "Colombo, Sri Lanka",

    "latitude": 6.9271,

    "longitude": 79.8612,

    "geocoded\_at": "2024-01-01T10:00:00Z",

    "geocode\_source": "opencage",

    "created\_at": "2024-01-01T10:00:00Z"

  }

]



##### cURL example

curl "http://localhost:8000/areas/autocomplete?q=col"



----------------------------------------------------------------------------------------





# Get area by id





##### URL



GET /areas/{area\_id}



##### Path parameters



|Name      | Type  | Required|        Description        |

|--------------------------------------------------------|

|area\_id | int   | Yes     | area\_Id for the area to fetch|



##### Response: 200 OK



{

    "id": 1,

    "name": "Colombo",

    "normalized\_name": "colombo",

    "main\_region": "Western",

    "formatted\_address": "Colombo, Sri Lanka",

    "latitude": 6.9271,

    "longitude": 79.8612,

    "geocoded\_at": "2024-01-01T10:00:00Z",

    "geocode\_source": "opencage",

    "created\_at": "2024-01-01T10:00:00Z"

  }



##### cURL example

curl "http://localhost:8000/areas/5"

#####  

##### Error Response



###### 404 not found



Area does not exist 



-------------------------------------------------------------------------------------

# Create area



##### URL



POST /areas/admin



##### Request Body(AreaCreate)



{

&nbsp; "name": "Gampaha",

&nbsp; "normalized\_name": "gampaha",

&nbsp; "main\_region": "Western",

&nbsp; "formatted\_address": "Gampaha, Sri Lanka",

&nbsp; "latitude": 7.084,

&nbsp; "longitude": 80.009"

}



##### Response: 201 Created



{

    "id": 1,

    "name": "Colombo",

    "normalized\_name": "colombo",

    "main\_region": "Western",

    "formatted\_address": "Colombo, Sri Lanka",

    "latitude": 6.9271,

    "longitude": 79.8612,

    "geocoded\_at": "2024-01-01T10:00:00Z",

    "geocode\_source": "opencage",

    "created\_at": "2024-01-01T10:00:00Z"

  }



##### cURL example

 curl -X POST http://localhost:8000/areas/admin \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{

&nbsp;   "name": "Kurunegala",

&nbsp;   "normalized\_name": "kurunegala",

&nbsp;   "main\_region": "North Western"

&nbsp; }'



##### Error Response



###### 400 Bad request





--------------------------------------------------------------------------------

# Update area



Only provided fields are updated.



##### URL

PATCH /areas/admin/{area\_id}



##### Path Parameters



| Name        | Type | Required | Description |

|-------------|------|----------|-------------|

| area\_id     | int  | Yes      | Area ID     |





##### Request Body(AreaUpdate)



{

&nbsp; "name": "New Gampaha",

&nbsp; "formatted\_address": "Updated Address"

}





##### Special Behaviors



* If both latitude + longitude are provided → treated as user-pinned location.



• If name/address changed but no coordinates → backend attempts re-geocoding automatically.



##### Response: 200 OK



{

    "id": 1,

    "name": "Colombo",

    "normalized\_name": "colombo",

    "main\_region": "Western",

    "formatted\_address": "Colombo, Sri Lanka",

    "latitude": 6.9271,

    "longitude": 79.8612,

    "geocoded\_at": "2024-01-01T10:00:00Z",

    "geocode\_source": "opencage",

    "created\_at": "2024-01-01T10:00:00Z"

  }



##### cURL example

curl -X PATCH http://localhost:8000/areas/admin/4 \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{ "name": "New Name" }'

#####  

##### Error Response



###### 404 not found

area not found



###### 400 Bad request



-----------------------------------------------------------------------------------





# Re\_geocode area



##### URL



POST /areas/admin/{area\_id}/re-geocode





##### Response: 200 ok



{

    "id": 1,

    "name": "Colombo",

    "normalized\_name": "colombo",

    "main\_region": "Western",

    "formatted\_address": "Colombo, Sri Lanka",

    "latitude": 6.9271,

    "longitude": 79.8612,

    "geocoded\_at": "2024-01-01T10:00:00Z",

    "geocode\_source": "opencage",

    "created\_at": "2024-01-01T10:00:00Z"

  }

#####  

##### cURL example

curl -X POST "http://localhost:8000/areas/admin/4/re-geocode"



##### Error Response



###### 404 not found

area not found



###### 400 Bad request



----------------------------------------------------------------------------------



# Delete Area



Delete an area by id.



##### URL



DELETE /areas/admin/{area\_id}



##### Path Parameters

| Name      | Type | Required | Description |

|-----------|------|----------|-------------|

| area\_id   | int  | Yes      | id for delete an area |



##### Success Response: 204 No Content



##### cURL example

curl -X DELETE "http://localhost:8000/areas/admin/4"



##### Error Responses



###### 500 Internal Server Error

 

###### 404 Not Found

 area not found



---------------------------------------------------------------------------------













