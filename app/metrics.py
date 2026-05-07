from prometheus_client import Counter, Histogram, Gauge, Summary

# --- Counters ---

# Keeping track of every request that hits the API. 
# Crucial for figuring out overall traffic and error rates.
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "How many requests we've handled so far",
    ["method", "endpoint", "status_code"]
)

# This is specifically for catching spikes in 4xx/5xx responses.
# Used for the 'HighErrorRate' alert.
HTTP_ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Count of failed requests (client vs server errors)",
    ["method", "endpoint", "error_type"]
)

# Tracks database activity. Helps us pinpoint if a specific table or 
# operation (like 'insert') is causing trouble.
DB_QUERIES_TOTAL = Counter(
    "db_queries_total",
    "Total DB operations attempted and their final outcome",
    ["operation", "table", "status"]
)

# --- Histograms ---

# Latency tracking. We use these buckets to calculate P95/P99 speeds.
# If a request falls into the >1s bucket too often, an alert will fire.
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "How long it takes to process a request from start to finish",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
)

# Database timing. Helps us see if the DB is becoming a bottleneck.
DB_QUERY_DURATION_SECONDS = Histogram(
    "db_query_duration_seconds",
    "Latency of simulated database queries",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1]
)

# --- Gauges ---

# Current load. This goes up when a request starts and down when it ends.
# Good for spotting "hung" requests that never finish.
HTTP_ACTIVE_REQUESTS = Gauge(
    "http_active_requests",
    "Number of requests currently being processed",
    ["method", "endpoint"]
)

# Basic service metadata. We set this to 1 at startup just so Prometheus 
# can verify the version and environment.
APP_INFO = Gauge(
    "app_info",
    "Static metadata about the running app",
    ["version", "environment", "service"]
)

# --- Summaries ---

# Monitoring payload sizes. If we see a massive spike in request size, 
# it might indicate someone is trying to overwhelm our ingress.
HTTP_REQUEST_SIZE_BYTES = Summary(
    "http_request_size_bytes",
    "Size of incoming request bodies",
    ["method", "endpoint"]
)

# Tracking how much data we're sending back to clients.
HTTP_RESPONSE_SIZE_BYTES = Summary(
    "http_response_size_bytes",
    "Size of outgoing response bodies",
    ["method", "endpoint"]
)
