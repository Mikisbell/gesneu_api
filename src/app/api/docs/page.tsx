import dynamic from 'next/dynamic';
import { getApiDocs } from '@/lib/swagger-helper';
import 'swagger-ui-react/swagger-ui.css';
import ApiDoc from '@/components/ApiDoc';

export default async function ApiDocsPage() {
    const spec = await getApiDocs();
    return (
        <div className="container mx-auto p-4 bg-white min-h-screen">
            <ApiDoc spec={spec} />
        </div>
    );
}
