# SarkariBot Test Coverage

This document outlines the comprehensive test coverage implementation for SarkariBot, ensuring reliability and preventing regressions across the entire codebase.

## Coverage Targets

- **Backend**: ≥85% test coverage
- **Frontend**: ≥80% test coverage  
- **Critical Paths**: ≥95% test coverage

## Test Infrastructure

### Backend Testing

**Framework**: pytest with pytest-django and pytest-cov
**Database**: SQLite in-memory for fast test execution
**Factories**: factory-boy for realistic test data generation
**Mocking**: unittest.mock for external service isolation

```bash
# Run backend tests
cd sarkaribot/backend
pytest --cov=apps --cov-report=html --cov-fail-under=85

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m critical      # Critical path tests (95% coverage)
```

### Frontend Testing

**Framework**: Jest with React Testing Library
**Coverage**: Built-in Jest coverage reporting
**Mocking**: MSW (Mock Service Worker) for API mocking

```bash
# Run frontend tests
cd sarkaribot/frontend
npm run test:coverage

# Run tests in watch mode
npm test

# Run tests for CI
npm run test:ci
```

## Test Structure

### Backend Tests

```
sarkaribot/backend/tests/
├── __init__.py
├── conftest.py                 # Global fixtures and configuration
├── factories.py               # Test data factories
├── test_models_jobs.py         # Job model tests
├── test_models_sources.py      # Government source model tests
├── test_api_jobs.py           # API endpoint tests
├── test_scraping.py           # Scraping system tests
└── test_critical_paths.py     # Critical path integration tests
```

### Frontend Tests

```
sarkaribot/frontend/src/
├── test-utils.js              # Testing utilities and mocks
└── __tests__/
    ├── JobCard.test.js        # JobCard component tests
    ├── HomePage.test.js       # HomePage component tests
    ├── apiService.test.js     # API service tests
    └── hooks.test.js          # Custom hooks tests
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation:
- Model field validation and constraints
- Serializer data transformation
- Utility function behavior
- Component rendering and props

### Integration Tests (`@pytest.mark.integration`)

Test interactions between components:
- API endpoint workflows
- Database relationships
- Service integrations
- Component interactions

### Critical Path Tests (`@pytest.mark.critical`)

Test core business workflows with 95% coverage requirement:
- Job posting lifecycle (announced → admit_card → answer_key → result)
- End-to-end scraping workflow
- SEO automation pipeline
- Complete user journeys
- API performance and security

## Running Tests

### Local Development

```bash
# Run all tests with coverage
./scripts/run_tests.sh

# Run specific test suites
cd sarkaribot/backend
pytest tests/test_models_jobs.py -v

# Run with coverage report
pytest --cov=apps --cov-report=html
```

### Continuous Integration

The GitHub Actions workflow (`.github/workflows/test-coverage.yml`) runs:

1. **Backend Tests**: Full test suite with PostgreSQL
2. **Frontend Tests**: Jest tests with coverage reporting
3. **Integration Tests**: Critical path validation
4. **Security Tests**: Bandit and Safety checks
5. **Performance Tests**: Load testing on PRs

### Coverage Reports

After running tests, coverage reports are generated:

- **Backend HTML**: `sarkaribot/backend/htmlcov/index.html`
- **Backend XML**: `sarkaribot/backend/coverage.xml`
- **Frontend HTML**: `sarkaribot/frontend/coverage/lcov-report/index.html`

## Test Data Management

### Factories

Test data is generated using factory-boy factories:

```python
from tests.factories import JobPostingFactory, GovernmentSourceFactory

# Create realistic test data
job = JobPostingFactory(
    title='Software Engineer Government Job 2024',
    status='announced'
)
source = GovernmentSourceFactory(name='SSC')
```

### Fixtures

Common test fixtures are defined in `conftest.py`:

```python
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
```

## Mocking Strategy

### Backend Mocking

External services are mocked to ensure test isolation:

```python
@patch('apps.scraping.tasks.get_scraper')
def test_scraping_workflow(self, mock_scraper):
    mock_scraper.return_value.scrape.return_value = [test_data]
    # Test logic here
```

### Frontend Mocking

API services are mocked using jest.mock:

```javascript
jest.mock('../services/apiService', () => ({
  getLatestJobs: jest.fn().mockResolvedValue(mockData),
  getJobById: jest.fn().mockResolvedValue(mockJob)
}));
```

## Performance Testing

Performance tests validate:
- API response times under load
- Database query efficiency
- Frontend rendering performance
- Memory usage patterns

## Security Testing

Security tests include:
- Bandit static analysis for Python code
- Safety dependency vulnerability scanning
- API permission and authentication testing
- Input validation and injection prevention

## Coverage Monitoring

### GitHub Actions Integration

Coverage reports are automatically:
- Generated on every push and PR
- Uploaded to Codecov for tracking
- Failed if below threshold requirements
- Commented on PRs with coverage changes

### Local Monitoring

Use the test script to monitor coverage locally:

```bash
./scripts/run_tests.sh
```

This provides:
- Real-time coverage feedback
- HTML reports for detailed analysis
- Failure notifications with specific thresholds

## Best Practices

### Writing Tests

1. **Arrange-Act-Assert**: Structure tests clearly
2. **Single Responsibility**: One assertion per test
3. **Descriptive Names**: Test names explain the scenario
4. **Independent Tests**: No dependencies between tests
5. **Realistic Data**: Use factories for consistent test data

### Maintaining Coverage

1. **Test-Driven Development**: Write tests before implementation
2. **Coverage Gaps**: Regularly review coverage reports
3. **Critical Paths**: Ensure 95% coverage for core workflows
4. **Regression Tests**: Add tests for every bug fix
5. **Documentation**: Keep test documentation up to date

## Troubleshooting

### Common Issues

**Tests fail locally but pass in CI**:
- Check environment variables and settings
- Ensure proper test database configuration
- Verify dependency versions match

**Coverage below threshold**:
- Review coverage report to identify gaps
- Add tests for uncovered code paths
- Consider if code is actually testable

**Slow test execution**:
- Use in-memory databases for tests
- Mock external services appropriately
- Parallelize test execution where possible

### Getting Help

1. Check test output for specific error messages
2. Review coverage reports for missed areas
3. Use `pytest --pdb` for debugging failed tests
4. Check CI logs for environment-specific issues

## Future Enhancements

- [ ] Visual regression testing for UI components
- [ ] End-to-end testing with Playwright
- [ ] Performance regression testing
- [ ] Mutation testing for test quality assessment
- [ ] Coverage trending and reporting dashboard