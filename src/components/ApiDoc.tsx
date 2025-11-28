'use client';

import SwaggerUI from 'swagger-ui-react';

type Props = {
    spec: Record<string, any>;
};

export default function ApiDoc({ spec }: Props) {
    return <SwaggerUI spec={spec} />;
}
