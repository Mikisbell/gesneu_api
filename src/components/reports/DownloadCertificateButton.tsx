import { Button } from '@/components/ui/button';
import { FileText } from 'lucide-react';

interface DownloadCertificateButtonProps {
    vehicleId: string;
}

export const DownloadCertificateButton = ({ vehicleId }: DownloadCertificateButtonProps) => {
    const handleDownload = () => {
        // Abrir en nueva pestaña que disparará la descarga
        window.open(`/api/v1/reports/certificate/${vehicleId}`, '_blank');
    };

    return (
        <Button variant="outline" size="sm" onClick={handleDownload} className="gap-2">
            <FileText className="h-4 w-4" />
            Certificado
        </Button>
    );
};
