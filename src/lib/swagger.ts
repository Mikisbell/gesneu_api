import { OAS3Definition } from 'swagger-jsdoc';

export const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'GesNeu API',
            version: '1.0.0',
            description: 'API documentation for GesNeu - Sistema de Gestión de Neumáticos',
            contact: {
                name: 'Soporte GesNeu',
                email: 'soporte@gesneu.com',
            },
        },
        servers: [
            {
                url: 'http://localhost:3000',
                description: 'Development server',
            },
        ],
        components: {
            securitySchemes: {
                bearerAuth: {
                    type: 'http',
                    scheme: 'bearer',
                    bearerFormat: 'JWT',
                },
            },
        },
        security: [
            {
                bearerAuth: [],
            },
        ],
    } as OAS3Definition,
    apis: ['./src/app/api/v1/**/*.ts', './src/app/api/docs/**/*.ts'], // Path to the API docs
};
