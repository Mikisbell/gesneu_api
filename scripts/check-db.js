const { prisma } = require('./src/lib/prisma.ts');

(async () => {
    try {
        const emp = await p.empresa.findFirst({ orderBy: { creado_en: 'asc' } });
        console.log('First empresa:', emp?.id, emp?.nombre, emp?.ruc);
        
        // Count centroCosto
        const ccCount = await p.centroCosto.count();
        console.log('CentroCosto count:', ccCount);
        
        // Check if empresa_id exists
        if (emp) {
            const ccWithEmpresa = await p.centroCosto.count({ where: { empresa_id: emp.id } });
            console.log('CentroCosto for this empresa:', ccWithEmpresa);
        }
    } catch (e) {
        console.log('ERR:', e.message);
    }
    await p.$disconnect();
})();
