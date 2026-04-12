import nextPlugin from "@next/eslint-plugin-next";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";

/** @type {import('eslint').Linter.Config[]} */
export default [
    {
        files: ["src/**/*.{ts,tsx}"],
        plugins: {
            "@next/next": nextPlugin,
            "@typescript-eslint": tsPlugin,
        },
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                ecmaVersion: "latest",
                sourceType: "module",
                ecmaFeatures: { jsx: true },
            },
        },
        rules: {
            // Next.js rules
            ...nextPlugin.configs.recommended.rules,
            "@next/next/no-img-element": "off",

            // TypeScript rules (relaxed for existing codebase)
            "@typescript-eslint/no-explicit-any": "off",
            "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],

            // General
            "no-console": "off",
        },
    },
    {
        ignores: [
            "node_modules/**",
            ".next/**",
            "public/**",
            "prisma/**",
            "**/*.test.ts",
            "**/__tests__/**",
        ],
    },
];
