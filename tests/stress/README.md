# GesNeu API - Stress Tests

Authenticated load testing suite for the GesNeu Fleet Management API.

## 🚀 Quick Start

```bash
# Run professional stress test (INSPECCION events)
node tests/stress/professional_stress.js

# Run purchase stress test (create Neumaticos)
node tests/stress/purchase_stress.js

# Run advanced stress test (INSPECCION events - high volume)
node tests/stress/advanced_stress.js
```

## 📋 Requirements

- **Running dev server**: `AUTH_TRUST_HOST=true npm run dev -- -p 3005`
- **Database**: PostgreSQL with valid test data
- **User credentials**: Valid `admin` user in database

## ⚙️ Configuration

### Environment Variables

```bash
# Optional - customize test behavior
export BASE_URL="http://localhost:3005"
export STRESS_DURATION="30"        # Test duration in seconds
export STRESS_CONCURRENCY="5"      # Concurrent connections
export STRESS_USER="admin"         # Test user username
export STRESS_PASSWORD="admin123"  # Test user password
```

### Database Connection Limits

The tests are configured to avoid database pool exhaustion:

- **Application pool**: 10 max connections (`src/lib/prisma.ts`)
- **Script pool**: 5 max connections (each test script)
- **Recommended concurrency**: 5 simultaneous requests

## 📊 Test Scenarios

### 1. Professional Stress Test
**File**: `professional_stress.js`

**Purpose**: Load test the event creation endpoint with INSPECCION events.

**Endpoint**: `POST /api/v1/neumaticos/eventos`

**Payload**: Random inspection data (depth, pressure, mileage)

**Use case**: Simulates fleet inspections at scale

```bash
node tests/stress/professional_stress.js
```

**Expected Results**:
- 2xx: 100% success rate
- Avg latency: 2-5 seconds
- Throughput: ~1-2 req/sec

---

### 2. Purchase Stress Test
**File**: `purchase_stress.js`

**Purpose**: Load test tire creation endpoint (COMPRA scenario).

**Endpoint**: `POST /api/v1/neumaticos`

**Payload**: New tire records with valid modelo, proveedor, almacen

**Use case**: Simulates bulk tire purchases

```bash
node tests/stress/purchase_stress.js
```

**Expected Results**:
- 2xx: 100% success rate
- Avg latency: 3-6 seconds
- Throughput: ~1 req/sec

---

### 3. Advanced Stress Test
**File**: `advanced_stress.js`

**Purpose**: Extended load test with INSPECCION events.

**Endpoint**: `POST /api/v1/neumaticos/eventos`

**Payload**: Similar to professional, optimized for high volume

**Use case**: Stress testing with sustained high load

```bash
node tests/stress/advanced_stress.js
```

**Expected Results**:
- 2xx: 100% success rate
- Avg latency: 2-4 seconds
- Throughput: ~1-2 req/sec

## 🔍 Understanding Results

### AutoCannon Output

```bash
┌─────────┬─────────┬─────────┬─────────┬─────────┬───────────┬────────────┬─────────┐
│ Stat    │ 2.5%    │ 50%     │ 97.5%   │ 99%     │ Avg       │ Stdev      │ Max     │
├─────────┼─────────┼─────────┼─────────┼─────────┼───────────┼────────────┼─────────┤
│ Latency │ 3560 ms │ 4292 ms │ 7429 ms │ 7429 ms │ 4636.9 ms │ 1253.13 ms │ 7429 ms │
└─────────┴─────────┴─────────┴─────────┴─────────┴───────────┴────────────┴─────────┘

2xx: 30 | 4xx: 0 | 5xx: 0
```

**Key Metrics**:
- **Latency Avg**: Average response time (goal: < 5000ms)
- **2xx Responses**: Successful requests (goal: 100%)
- **5xx Responses**: Server errors (goal: 0)
- **Throughput**: Requests per second

### Success Criteria

✅ **Passing Test**:
- 2xx ≥ 95% of total requests
- 5xx = 0
- No database connection errors

❌ **Failing Test**:
- 5xx > 0
- Database errors: `MaxClientsInSessionMode`
- Authentication failures

## 🐛 Troubleshooting

### Error: `MaxClientsInSessionMode`

**Cause**: Database connection pool exhausted

**Solution**:
1. Reduce concurrency: `export STRESS_CONCURRENCY="2"`
2. Check application pool size in `src/lib/prisma.ts` (max: 10)
3. Ensure script pool is limited (max: 5)

---

### Error: `No session cookies received!`

**Cause**: Authentication failed or redirect not handled

**Solution**:
1. Verify test user exists: `psql -c "SELECT * FROM usuarios WHERE username='admin';"`
2. Check `AUTH_TRUST_HOST=true` is set
3. Confirm password is correct in credentials

---

### Error: `EADDRINUSE: address already in use :::3005`

**Cause**: Dev server already running or zombie process

**Solution**:
```bash
fuser -k 3005/tcp
AUTH_TRUST_HOST=true npm run dev -- -p 3005
```

---

### Slow Server Startup (~90s)

**Expected behavior**: Next.js cold start compilation

**Solution**: Wait for "✓ Ready in Xs" message before running tests

## 🏗️ Architecture

### Authentication Flow

1. **Fetch CSRF token**: `GET /api/auth/csrf`
2. **Login**: `POST /api/auth/callback/credentials`
3. **Extract cookies**: Parse `authjs.session-token` from response
4. **Authenticated requests**: Include session cookie in headers

### Data Seeding

Tests automatically create required entities if missing:
- Modelo Neumático
- Proveedor
- Almacén
- Neumático (for event tests)

### Connection Pooling

```javascript
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
    max: 5  // Critical: Prevents pool exhaustion
});
```

## 📝 Maintenance

### Adding New Tests

1. Copy existing test as template
2. Update endpoint and payload generator
3. Configure pool with `max: 5`
4. Add to this README

### Updating Concurrency Limits

**Before increasing concurrency:**
1. Check database plan limits (Supabase Free: ~20 connections)
2. Calculate: `app_pool (10) + script_pool (5) + concurrency (X) ≤ db_limit`
3. Update `STRESS_CONCURRENCY` accordingly

## 🔐 Security Notes

- **Credentials**: Use test-only credentials, never production
- **Environment**: Run only in development/staging
- **Database**: Use dedicated test database or tenant
- **Rate limiting**: Tests may trigger rate limits in production

## 📚 Related Documentation

- [NextAuth.js Authentication](https://next-auth.js.org/)
- [AutoCannon Load Testing](https://github.com/mcollina/autocannon)
- [Prisma Connection Pooling](https://www.prisma.io/docs/guides/performance-and-optimization/connection-management)

---

**Last Updated**: 2026-02-05  
**Maintainer**: DevOps Team
