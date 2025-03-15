# Milestone 1: API Tool Implementation

## Overview
Implementation of a lightweight, standalone API Tool that can handle different types of API calls (REST, GraphQL, etc.) based on YAML pipeline definitions.

## Core Components

### 1. Pipeline YAML Structure
```yaml
version: '1.0'
pipeline:
  name: sample-pipeline
  nodes:
    - id: node1
      name: fetch-user-data
      tool:
        type: api
        config:
          protocol: rest  # rest, graphql, grpc
          method: GET    # GET, POST, PUT, DELETE
          url: https://api.example.com/users
          headers:
            Content-Type: application/json
            Authorization: Bearer ${env.API_TOKEN}
          payload:
            user_id: 123
      retry:
        max_attempts: 3
        delay: 1000  # milliseconds
      timeout: 5000  # milliseconds

    - id: node2
      name: create-ticket
      tool:
        type: api
        config:
          protocol: graphql
          url: https://api.example.com/graphql
          headers:
            Content-Type: application/json
          payload:
            query: |
              mutation CreateTicket($input: TicketInput!) {
                createTicket(input: $input) {
                  id
                  status
                }
              }
            variables:
              input:
                title: "New Issue"
                description: "Description"
```

### 2. Tool Input JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["protocol", "url"],
  "properties": {
    "protocol": {
      "type": "string",
      "enum": ["rest", "graphql", "grpc"]
    },
    "method": {
      "type": "string",
      "enum": ["GET", "POST", "PUT", "DELETE"]
    },
    "url": {
      "type": "string",
      "format": "uri"
    },
    "headers": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    },
    "payload": {
      "type": "object"
    },
    "timeout": {
      "type": "integer",
      "minimum": 0
    },
    "retry": {
      "type": "object",
      "properties": {
        "max_attempts": {
          "type": "integer",
          "minimum": 1
        },
        "delay": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  }
}
```

## Implementation Plan

### 1. Core API Tool (`src/tools/api/`)
```
src/tools/api/
├── __init__.py
├── base.py           # Base tool interface
├── clients/
│   ├── __init__.py
│   ├── rest.py      # REST client implementation
│   ├── graphql.py   # GraphQL client implementation
│   └── grpc.py      # gRPC client stub
├── models/
│   ├── __init__.py
│   └── config.py    # Pydantic models for configuration
└── factory.py       # Client factory based on protocol
```

### 2. FastAPI Service (`src/service/`)
```
src/service/
├── __init__.py
├── main.py          # FastAPI application
├── routes/
│   ├── __init__.py
│   └── api.py       # API endpoints
└── models/
    ├── __init__.py
    └── requests.py  # Request/Response models
```

### 3. Docker Setup
```
docker/
├── Dockerfile
└── docker-compose.yml
```

## API Endpoints

### Execute Tool
```
POST /v1/tools/api/execute
Content-Type: application/json

{
  "protocol": "rest",
  "method": "GET",
  "url": "https://api.example.com/users",
  "headers": {
    "Authorization": "Bearer token"
  },
  "payload": {
    "user_id": 123
  }
}
```

Response:
```json
{
  "status": "success",
  "data": {
    "result": {},     // API response
    "metadata": {
      "status_code": 200,
      "headers": {},
      "timing": 123   // ms
    }
  }
}
```

## Testing Strategy

### Unit Tests
1. Client implementations
2. Factory pattern
3. Configuration validation
4. Error handling

### Integration Tests
1. End-to-end API calls
2. Retry mechanism
3. Timeout handling
4. Protocol switching

## Success Criteria
1. Successfully execute REST API calls
2. Handle GraphQL queries/mutations
3. Proper error handling and retries
4. Clean separation of protocols
5. Comprehensive test coverage
6. Docker-based execution

## Dependencies
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
httpx = "^0.26.0"
pydantic = "^2.6.0"
gql = "^3.5.0"
grpcio = "^1.60.0"
pyyaml = "^6.0.1"
