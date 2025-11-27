import { PrismaClient } from '@prisma/client';
import { prisma } from '@/lib/prisma';

export interface IBaseRepository<T, CreateInput, UpdateInput> {
    findAll(params?: any): Promise<T[]>;
    findById(id: string): Promise<T | null>;
    create(data: CreateInput): Promise<T>;
    update(id: string, data: UpdateInput): Promise<T>;
    delete(id: string): Promise<T>;
    count(params?: any): Promise<number>;
}

export abstract class BaseRepository<T, CreateInput, UpdateInput> implements IBaseRepository<T, CreateInput, UpdateInput> {
    protected db: PrismaClient;
    protected abstract model: any;

    constructor() {
        this.db = prisma;
    }

    async findAll(params: any = {}): Promise<T[]> {
        try {
            return await this.model.findMany(params);
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    async findById(id: string): Promise<T | null> {
        try {
            return await this.model.findUnique({
                where: { id },
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    async create(data: CreateInput): Promise<T> {
        try {
            return await this.model.create({
                data,
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    async update(id: string, data: UpdateInput): Promise<T> {
        try {
            return await this.model.update({
                where: { id },
                data,
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    async delete(id: string): Promise<T> {
        try {
            return await this.model.delete({
                where: { id },
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    async count(params: any = {}): Promise<number> {
        try {
            return await this.model.count({
                where: params.where,
            });
        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    protected handleError(error: any): void {
        console.error('Database Error:', error);
        // Aquí podríamos implementar lógica de logging centralizado o transformación de errores
    }
}
