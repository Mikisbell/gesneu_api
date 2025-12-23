import { createSwaggerSpec } from 'next-swagger-doc';
import { swaggerOptions } from './swagger';

export const getApiDocs = async () => {
    const spec = createSwaggerSpec({
        apiFolder: 'src/app/api', // Needed for next-swagger-doc to scan files
        definition: swaggerOptions.definition,
    });
    return spec;
};
