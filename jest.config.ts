import 'dotenv/config';
import type { Config } from 'jest';

const config: Config = {
    preset: 'ts-jest',
    testEnvironment: 'node',

    // Run tests sequentially to avoid DB connection conflicts
    maxWorkers: 1,

    // Global teardown to ensure DB connections are closed
    globalTeardown: '<rootDir>/jest.teardown.ts',

    // Root directory
    rootDir: '.',

    // Test match patterns
    testMatch: [
        '**/__tests__/**/*.test.ts',
        '**/__tests__/**/*.test.tsx'
    ],

    // Ignore integration tests by default (they need running database)
    testPathIgnorePatterns: [
        '/node_modules/'
    ],

    // Setup files
    setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],

    // Module name mapper for path aliases
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
    },

    // Transform TypeScript files
    transform: {
        '^.+\\.tsx?$': ['ts-jest', {
            tsconfig: {
                esModuleInterop: true,
                allowSyntheticDefaultImports: true,
            }
        }]
    },

    // Coverage configuration
    collectCoverageFrom: [
        'src/**/*.{ts,tsx}',
        '!src/**/*.d.ts',
        '!src/**/*.config.ts',
        '!src/__tests__/**'
    ],

    // Coverage thresholds
    coverageThreshold: {
        global: {
            branches: 70,
            functions: 70,
            lines: 70,
            statements: 70
        }
    },

    // Clear mocks between tests
    clearMocks: true,

    // Timeout for tests (30s for remote DB latency)
    testTimeout: 30000,

    // Force exit after tests complete (handles async DB connections)
    forceExit: true,

    // Verbose output
    verbose: true
};

export default config;
