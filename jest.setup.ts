// Jest setup file
import dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

// Silence console logs during tests
jest.spyOn(global.console, 'log').mockImplementation(() => { });
jest.spyOn(global.console, 'error').mockImplementation(() => { });
jest.spyOn(global.console, 'warn').mockImplementation(() => { });
jest.spyOn(global.console, 'info').mockImplementation(() => { });
jest.spyOn(global.console, 'debug').mockImplementation(() => { });
import '@testing-library/jest-dom';
