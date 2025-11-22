/**
 * ATON.js - Adaptive Token-Oriented Notation
 * JavaScript Implementation
 * 
 * @version 1.0.2
 * @author Stefano D'Agostino
 * @license MIT
 */

(function(global) {
    'use strict';

    /**
     * ATON Type Enum
     */
    const ATONType = {
        INT: 'int',
        FLOAT: 'float',
        STR: 'str',
        BOOL: 'bool',
        ARRAY: 'arr',
        OBJECT: 'obj',
        NULL: 'null',
        DATETIME: 'datetime',
        REF: 'ref'
    };

    /**
     * ATON Schema Class
     */
    class ATONSchema {
        constructor(fields = [], defaults = {}) {
            this.fields = fields; // Array of [fieldName, fieldType]
            this.defaults = defaults;
        }
    }

    /**
     * ATON Encoder Class
     * Converts JavaScript objects to ATON format
     */
    class ATONEncoder {
        constructor(options = {}) {
            this.optimize = options.optimize !== undefined ? options.optimize : true;
            this.includeSchema = options.includeSchema !== undefined ? options.includeSchema : true;
            this.includeDefaults = options.includeDefaults !== undefined ? options.includeDefaults : true;
            this.prettyPrint = options.prettyPrint !== undefined ? options.prettyPrint : false;
            this.minItemsForOptimization = options.minItemsForOptimization !== undefined ? options.minItemsForOptimization : 3;
        }

        /**
         * Encode a JavaScript object to ATON format
         * @param {Object} data - Data to encode
         * @param {string} name - Optional entity name
         * @returns {string} ATON formatted string
         */
        encode(data, name = 'data') {
            if (!data || typeof data !== 'object') {
                throw new Error('Data must be an object');
            }

            const result = [];

            // Handle single key with array value
            if (Object.keys(data).length === 1) {
                const [key, value] = Object.entries(data)[0];
                if (Array.isArray(value) && value.length > 0 && 
                    typeof value[0] === 'object') {
                    return this.encodeEntityArray(key, value);
                }
            }

            // Handle multiple keys
            for (const [key, value] of Object.entries(data)) {
                if (Array.isArray(value) && value.length > 0 && 
                    typeof value[0] === 'object') {
                    result.push(this.encodeEntityArray(key, value));
                }
            }

            return result.join('\n\n');
        }

        /**
         * Encode an array of homogeneous objects
         * @private
         */
        encodeEntityArray(name, items) {
            if (items.length === 0) return `${name}(0):`;

            const schema = this.inferSchema(items);
            const defaults = this.optimize && this.includeDefaults ? this.findDefaults(items) : {};
            const result = [];

            // Add schema header if enabled and items meet threshold
            if (this.includeSchema && items.length >= this.minItemsForOptimization) {
                const schemaLine = this.formatSchema(schema);
                result.push(schemaLine);
                
                // Add defaults if enabled and any were found
                if (this.includeDefaults && Object.keys(defaults).length > 0) {
                    const defaultsLine = this.formatDefaults(defaults);
                    result.push(defaultsLine);
                }
                
                // Add blank line for readability
                result.push('');
            }

            // Add entity header
            result.push(`${name}(${items.length}):`);

            // Add data rows
            for (const item of items) {
                const row = this.encodeRow(item, schema.fields, defaults);
                result.push(`  ${row}`);
            }

            return result.join('\n');
        }

        /**
         * Infer schema from data
         * @private
         */
        inferSchema(items) {
            if (items.length === 0) return new ATONSchema();

            const first = items[0];
            const fields = [];

            for (const [key, value] of Object.entries(first)) {
                const type = this.inferType(value);
                fields.push([key, type]);
            }

            return new ATONSchema(fields);
        }

        /**
         * Find common default values
         * @private
         */
        findDefaults(items) {
            if (items.length < 3) return {};

            const defaults = {};
            const first = items[0];

            for (const key of Object.keys(first)) {
                const values = items.map(item => JSON.stringify(item[key]));
                const uniqueValues = new Set(values);

                // If all values are the same, it's a default
                if (uniqueValues.size === 1) {
                    defaults[key] = first[key];
                }
            }

            return defaults;
        }

        /**
         * Infer ATON type from JavaScript value
         * @private
         */
        inferType(value) {
            if (value === null || value === undefined) return ATONType.NULL;
            if (typeof value === 'boolean') return ATONType.BOOL;
            if (typeof value === 'number') {
                return Number.isInteger(value) ? ATONType.INT : ATONType.FLOAT;
            }
            if (typeof value === 'string') {
                // Check for datetime
                if (value.match(/^\d{4}-\d{2}-\d{2}T/)) return ATONType.DATETIME;
                // Check for reference
                if (value.startsWith('->') || value.startsWith('<-')) return ATONType.REF;
                return ATONType.STR;
            }
            if (Array.isArray(value)) return ATONType.ARRAY;
            if (typeof value === 'object') return ATONType.OBJECT;
            return ATONType.STR;
        }

        /**
         * Format schema definition
         * @private
         */
        formatSchema(schema) {
            const fields = schema.fields.map(([name, type]) => `${name}:${type}`);
            return `@schema[${fields.join(', ')}]`;
        }

        /**
         * Format defaults definition
         * @private
         */
        formatDefaults(defaults) {
            const items = Object.entries(defaults).map(([k, v]) => 
                `${k}:${this.formatValue(v)}`
            );
            return `@defaults[${items.join(', ')}]`;
        }

        /**
         * Encode a single row
         * @private
         */
        encodeRow(item, fields, defaults) {
            const values = [];

            for (const [fieldName, fieldType] of fields) {
                const value = item[fieldName];

                // Skip if matches default
                if (this.optimize && defaults[fieldName] !== undefined) {
                    if (JSON.stringify(value) === JSON.stringify(defaults[fieldName])) {
                        continue;
                    }
                }

                values.push(this.formatValue(value));
            }

            return values.join(', ');
        }

        /**
         * Format a single value
         * @private
         */
        formatValue(value) {
            if (value === null || value === undefined) return 'null';
            if (typeof value === 'boolean') return value ? 'true' : 'false';
            if (typeof value === 'number') return String(value);
            if (typeof value === 'string') {
                // Don't quote references
                if (value.startsWith('->') || value.startsWith('<-')) return value;
                // Escape quotes in strings
                return `"${value.replace(/"/g, '\\"')}"`;
            }
            if (Array.isArray(value)) {
                const items = value.map(v => this.formatValue(v));
                return `[${items.join(',')}]`;
            }
            if (typeof value === 'object') {
                const items = Object.entries(value).map(([k, v]) => 
                    `${k}:${this.formatValue(v)}`
                );
                return `{${items.join(',')}}`;
            }
            return String(value);
        }

        /**
         * Estimate token count (rough approximation)
         * @param {string} text - Text to count
         * @returns {number} Estimated token count
         */
        estimateTokens(text) {
            // Rough estimation: ~4 characters per token
            return Math.ceil(text.length / 4);
        }
    }

    /**
     * ATON Decoder Class
     * Parses ATON format back to JavaScript objects
     */
    class ATONDecoder {
        constructor() {
            this.currentSchema = null;
            this.defaults = {};
        }

        /**
         * Decode ATON string to JavaScript object
         * @param {string} atonStr - ATON formatted string
         * @returns {Object} Parsed JavaScript object
         */
        decode(atonStr) {
            const result = {};
            const lines = atonStr.trim().split('\n');
            let i = 0;

            while (i < lines.length) {
                const line = lines[i].trim();

                if (!line || line.startsWith('#')) {
                    i++;
                    continue;
                }

                // Parse schema
                if (line.startsWith('@schema')) {
                    this.currentSchema = this.parseSchema(line);
                    i++;
                    continue;
                }

                // Parse defaults
                if (line.startsWith('@defaults')) {
                    this.defaults = this.parseDefaults(line);
                    i++;
                    continue;
                }

                // Parse entity
                if (line.includes('(') && line.endsWith(':')) {
                    const [entityName, count, dataLines] = this.parseEntity(lines, i);
                    result[entityName] = dataLines;
                    i += count + 1;
                    this.currentSchema = null;
                    this.defaults = {};
                    continue;
                }

                i++;
            }

            return result;
        }

        /**
         * Parse schema definition
         * @private
         */
        parseSchema(line) {
            const match = line.match(/@schema\[(.*?)\]/);
            if (!match) return new ATONSchema();

            const fieldsStr = match[1];
            const fields = [];

            for (const field of fieldsStr.split(',')) {
                const trimmed = field.trim();
                if (trimmed.includes(':')) {
                    const [name, type] = trimmed.split(':');
                    fields.push([name.trim(), type.trim()]);
                }
            }

            return new ATONSchema(fields);
        }

        /**
         * Parse defaults definition
         * @private
         */
        parseDefaults(line) {
            const match = line.match(/@defaults\[(.*?)\]/);
            if (!match) return {};

            const defaultsStr = match[1];
            const defaults = {};

            for (const item of defaultsStr.split(',')) {
                const trimmed = item.trim();
                if (trimmed.includes(':')) {
                    const [key, value] = trimmed.split(':', 2);
                    defaults[key.trim()] = this.parseValue(value.trim());
                }
            }

            return defaults;
        }

        /**
         * Parse entity block
         * @private
         */
        parseEntity(lines, startIdx) {
            const header = lines[startIdx].trim();
            const match = header.match(/(\w+)\((\d+)\):/);

            if (!match) return ['', 0, []];

            const entityName = match[1];
            const count = parseInt(match[2], 10);
            const data = [];
            let i = startIdx + 1;

            while (i < lines.length && data.length < count) {
                const line = lines[i].trim();
                if (line && !line.startsWith('#') && !line.startsWith('@')) {
                    const row = this.parseRow(line);
                    if (row) data.push(row);
                }
                i++;
            }

            return [entityName, i - startIdx, data];
        }

        /**
         * Parse a data row
         * @private
         */
        parseRow(line) {
            if (!this.currentSchema || !this.currentSchema.fields.length) {
                return { values: this.splitValues(line) };
            }

            const values = this.splitValues(line);
            const result = { ...this.defaults };

            for (let i = 0; i < this.currentSchema.fields.length; i++) {
                const [fieldName, fieldType] = this.currentSchema.fields[i];
                if (i < values.length) {
                    result[fieldName] = this.parseValue(values[i]);
                }
            }

            return result;
        }

        /**
         * Split line into values, respecting quotes and brackets
         * @private
         */
        splitValues(line) {
            const values = [];
            let current = [];
            let depth = 0;
            let inQuotes = false;

            for (let i = 0; i < line.length; i++) {
                const char = line[i];
                const prevChar = i > 0 ? line[i - 1] : '';

                if (char === '"' && prevChar !== '\\') {
                    inQuotes = !inQuotes;
                    current.push(char);
                } else if ((char === '[' || char === '{') && !inQuotes) {
                    depth++;
                    current.push(char);
                } else if ((char === ']' || char === '}') && !inQuotes) {
                    depth--;
                    current.push(char);
                } else if (char === ',' && depth === 0 && !inQuotes) {
                    values.push(current.join('').trim());
                    current = [];
                } else {
                    current.push(char);
                }
            }

            if (current.length > 0) {
                values.push(current.join('').trim());
            }

            return values;
        }

        /**
         * Parse a single value
         * @private
         */
        parseValue(valueStr) {
            valueStr = valueStr.trim();

            if (valueStr === 'null') return null;
            if (valueStr === 'true') return true;
            if (valueStr === 'false') return false;
            if (valueStr.startsWith('"') && valueStr.endsWith('"')) {
                return valueStr.slice(1, -1).replace(/\\"/g, '"');
            }
            if (valueStr.startsWith('[') && valueStr.endsWith(']')) {
                const inner = valueStr.slice(1, -1);
                if (!inner) return [];
                return this.splitValues(inner).map(v => this.parseValue(v));
            }
            if (valueStr.startsWith('{') && valueStr.endsWith('}')) {
                const inner = valueStr.slice(1, -1);
                if (!inner) return {};
                const obj = {};
                for (const item of this.splitValues(inner)) {
                    if (item.includes(':')) {
                        const [k, v] = item.split(':', 2);
                        obj[k.trim()] = this.parseValue(v.trim());
                    }
                }
                return obj;
            }
            if (valueStr.startsWith('->') || valueStr.startsWith('<-')) {
                return valueStr;
            }

            // Try to parse as number
            const num = Number(valueStr);
            if (!isNaN(num)) return num;

            return valueStr;
        }
    }

    /**
     * ATON Converter Class
     * High-level API for converting between formats
     */
    class ATONConverter {
        constructor(options = {}) {
            this.options = options;
            this.encoder = new ATONEncoder(options);
            this.decoder = new ATONDecoder();
        }

        /**
         * Recreate encoder with new options
         * @param {Object} newOptions - New encoder options
         */
        setOptions(newOptions) {
            this.options = { ...this.options, ...newOptions };
            this.encoder = new ATONEncoder(this.options);
        }

        /**
         * Convert JSON string to ATON
         * @param {string} jsonStr - JSON string
         * @returns {string} ATON string
         */
        jsonToAton(jsonStr) {
            const data = JSON.parse(jsonStr);
            return this.encoder.encode(data);
        }

        /**
         * Convert ATON string to JSON
         * @param {string} atonStr - ATON string
         * @returns {string} JSON string
         */
        atonToJson(atonStr) {
            const data = this.decoder.decode(atonStr);
            return JSON.stringify(data, null, 2);
        }

        /**
         * Estimate token count
         * @param {string} text - Text to count
         * @returns {number} Estimated tokens
         */
        countTokens(text) {
            return this.encoder.estimateTokens(text);
        }

        /**
         * Calculate savings
         * @param {string} jsonStr - Original JSON
         * @param {string} atonStr - Converted ATON
         * @returns {Object} Savings statistics
         */
        calculateSavings(jsonStr, atonStr) {
            const jsonTokens = this.countTokens(jsonStr);
            const atonTokens = this.countTokens(atonStr);
            const savedTokens = jsonTokens - atonTokens;
            const reduction = ((savedTokens / jsonTokens) * 100).toFixed(1);

            return {
                jsonTokens,
                atonTokens,
                savedTokens,
                reductionPercent: parseFloat(reduction),
                jsonSize: jsonStr.length,
                atonSize: atonStr.length,
                sizeSavings: jsonStr.length - atonStr.length
            };
        }
    }

    // Export for different module systems
    if (typeof module !== 'undefined' && module.exports) {
        // Node.js
        module.exports = {
            ATONEncoder,
            ATONDecoder,
            ATONConverter,
            ATONType,
            ATONSchema
        };
    } else if (typeof define === 'function' && define.amd) {
        // AMD
        define([], function() {
            return {
                ATONEncoder,
                ATONDecoder,
                ATONConverter,
                ATONType,
                ATONSchema
            };
        });
    } else {
        // Browser global
        global.ATON = {
            Encoder: ATONEncoder,
            Decoder: ATONDecoder,
            Converter: ATONConverter,
            Type: ATONType,
            Schema: ATONSchema
        };
    }

})(typeof window !== 'undefined' ? window : global);
