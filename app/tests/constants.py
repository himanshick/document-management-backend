# API base URL for tests
API_BASE_URL = "http://localhost:8000/api/v1"

# Common test authorization token
TEST_TOKEN = "fake-token"

# Authorization header template
AUTH_HEADER_TEMPLATE = "Bearer {}"

# Endpoint paths
INGESTION_TRIGGER_ENDPOINT = "/ingestion/trigger"

# Sample request payloads for ingestion tests
REQUEST_DATA_INGESTION_TRIGGER = {
    "document_id": "test-doc-id"
}

REQUEST_DATA_INGESTION_TRIGGER_FAILURE = {
    "document_id": "dummy"
}

# Mock token decoded payload for authentication
MOCK_DECODED_TOKEN_PAYLOAD = {
    "sub": "test-user-id"
}

# Expected HTTP status codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_401_UNAUTHORIZED = 401
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Common test user data for user-related tests
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"
TEST_USER_ROLE = "admin"

# User login data for tests
TEST_LOGIN_DATA = {
    "username": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
}

# User registration data for tests
TEST_REGISTRATION_DATA = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
    "role": TEST_USER_ROLE,
}

# Mocked DB responses
MOCK_USER_DB_ENTRY = {
    "email": TEST_USER_EMAIL,
    "password": "hashed_pw",
}

# Mocked authentication response
MOCK_AUTH_RESPONSE = {
    "access_token": "testtoken",
    "token_type": "bearer"
}

#  Constants for testing document-related functionality

TEST_USER_ID = "683337ebf4fe8b0890700604"
TEST_DOCUMENT_ID = "doc123"

TEST_DOCUMENT = {
    "_id": TEST_DOCUMENT_ID,
    "title": "Test Document",
    "content": "This is a test document.",
    "owner_id": TEST_USER_ID,
}

UPDATED_DOCUMENT_DATA = {
    "title": "Updated Title",
    "content": "Updated content"
}
