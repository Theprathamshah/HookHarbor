CREATE TABLE delivery_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    endpoint_id UUID NOT NULL REFERENCES endpoints(id) ON DELETE CASCADE,
    request_payload TEXT NOT NULL,
    request_headers JSONB NOT NULL,
    response_code INTEGER,
    response_body TEXT,
    status VARCHAR(20) NOT NULL,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    duration_ms INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_delivery_logs_endpoint_id ON delivery_logs(endpoint_id);
CREATE INDEX idx_delivery_logs_status ON delivery_logs(status);
