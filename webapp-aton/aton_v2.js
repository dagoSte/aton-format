/**
 * ATON.js v2.0.0 - Adaptive Token-Oriented Notation
 * JavaScript/TypeScript Implementation - Production Grade
 * 
 * Features:
 * - Compression Modes (Fast, Balanced, Ultra, Adaptive)
 * - Query Language (SQL-like with AST parser)
 * - Streaming Encoder
 * - Full error handling
 * - Zero compromises
 * 
 * @version 2.0.0
 * @author Stefano D'Agostino
 * @license MIT
 */

(function(global) {
    'use strict';

    // ========================================================================
    // ENUMS & CONSTANTS
    // ========================================================================

    /**
     * Compression modes
     */
    const CompressionMode = {
        FAST: 'fast',
        BALANCED: 'balanced',
        ULTRA: 'ultra',
        ADAPTIVE: 'adaptive'
    };

    /**
     * Query operators
     */
    const QueryOperator = {
        EQ: '=',
        NEQ: '!=',
        LT: '<',
        GT: '>',
        LTE: '<=',
        GTE: '>=',
        LIKE: 'LIKE',
        IN: 'IN',
        NOT_IN: 'NOT IN',
        BETWEEN: 'BETWEEN'
    };

    /**
     * Logical operators
     */
    const LogicalOperator = {
        AND: 'AND',
        OR: 'OR',
        NOT: 'NOT'
    };

    /**
     * Sort order
     */
    const SortOrder = {
        ASC: 'ASC',
        DESC: 'DESC'
    };

    /**
     * ATON types
     */
    const ATONType = {
        INT: 'int',
        FLOAT: 'float',
        STR: 'str',
        BOOL: 'bool',
        ARRAY: 'array',
        OBJECT: 'object',
        NULL: 'null'
    };

    // ========================================================================
    // EXCEPTIONS
    // ========================================================================

    class ATONError extends Error {
        constructor(message) {
            super(message);
            this.name = 'ATONError';
        }
    }

    class ATONEncodingError extends ATONError {
        constructor(message) {
            super(message);
            this.name = 'ATONEncodingError';
        }
    }

    class ATONDecodingError extends ATONError {
        constructor(message) {
            super(message);
            this.name = 'ATONDecodingError';
        }
    }

    class ATONQueryError extends ATONError {
        constructor(message) {
            super(message);
            this.name = 'ATONQueryError';
        }
    }

    // ========================================================================
    // QUERY LANGUAGE - TOKENIZER
    // ========================================================================

    class QueryTokenizer {
        constructor() {
            this.patterns = [
                ['SELECT', /\bSELECT\b/i],
                ['FROM', /\bFROM\b/i],
                ['WHERE', /\bWHERE\b/i],
                ['ORDER', /\bORDER\s+BY\b/i],
                ['LIMIT', /\bLIMIT\b/i],
                ['OFFSET', /\bOFFSET\b/i],
                ['AND', /\bAND\b/i],
                ['OR', /\bOR\b/i],
                ['NOT', /\bNOT\b/i],
                ['IN', /\bIN\b/i],
                ['LIKE', /\bLIKE\b/i],
                ['BETWEEN', /\bBETWEEN\b/i],
                ['ASC', /\bASC\b/i],
                ['DESC', /\bDESC\b/i],
                ['IDENTIFIER', /[a-zA-Z_][a-zA-Z0-9_]*/],
                ['NUMBER', /-?\d+\.?\d*/],
                ['STRING', /'[^']*'|"[^"]*"/],
                ['OPERATOR', /<=|>=|!=|<>|=|<|>/],
                ['COMMA', /,/],
                ['LPAREN', /\(/],
                ['RPAREN', /\)/],
                ['WHITESPACE', /\s+/]
            ];
        }

        tokenize(query) {
            const tokens = [];
            let pos = 0;

            while (pos < query.length) {
                let matched = false;

                for (const [name, pattern] of this.patterns) {
                    const regex = new RegExp('^' + pattern.source, pattern.flags);
                    const match = query.slice(pos).match(regex);

                    if (match) {
                        if (name !== 'WHITESPACE') {
                            tokens.push({ type: name, value: match[0] });
                        }
                        pos += match[0].length;
                        matched = true;
                        break;
                    }
                }

                if (!matched) {
                    throw new ATONQueryError(`Invalid character at position ${pos}: '${query[pos]}'`);
                }
            }

            return tokens;
        }
    }

    // ========================================================================
    // QUERY LANGUAGE - PARSER
    // ========================================================================

    class QueryCondition {
        constructor(field, operator, value, value2 = null) {
            this.field = field;
            this.operator = operator;
            this.value = value;
            this.value2 = value2; // For BETWEEN
        }

        evaluate(record) {
            if (!(this.field in record)) {
                return false;
            }

            const recordValue = record[this.field];

            switch (this.operator) {
                case QueryOperator.EQ:
                    return recordValue === this.value;
                case QueryOperator.NEQ:
                    return recordValue !== this.value;
                case QueryOperator.LT:
                    return recordValue < this.value;
                case QueryOperator.GT:
                    return recordValue > this.value;
                case QueryOperator.LTE:
                    return recordValue <= this.value;
                case QueryOperator.GTE:
                    return recordValue >= this.value;
                case QueryOperator.LIKE:
                    const pattern = this.value.replace(/%/g, '.*').replace(/_/g, '.');
                    return new RegExp(`^${pattern}$`, 'i').test(String(recordValue));
                case QueryOperator.IN:
                    return this.value.includes(recordValue);
                case QueryOperator.NOT_IN:
                    return !this.value.includes(recordValue);
                case QueryOperator.BETWEEN:
                    return recordValue >= this.value && recordValue <= this.value2;
                default:
                    return false;
            }
        }
    }

    class QueryExpression {
        constructor(conditions, logicalOp = LogicalOperator.AND) {
            this.conditions = conditions;
            this.logicalOp = logicalOp;
        }

        evaluate(record) {
            const results = this.conditions.map(item => {
                if (item instanceof QueryCondition) {
                    return item.evaluate(record);
                } else {
                    return item.evaluate(record); // Nested expression
                }
            });

            if (this.logicalOp === LogicalOperator.AND) {
                return results.every(r => r);
            } else if (this.logicalOp === LogicalOperator.OR) {
                return results.some(r => r);
            } else { // NOT
                return !results[0];
            }
        }
    }

    class QueryParser {
        constructor() {
            this.tokenizer = new QueryTokenizer();
            this.tokens = [];
            this.pos = 0;
        }

        parse(queryString) {
            // Extract from @query[...] if present
            const match = queryString.match(/@query\[(.*)\]/is);
            if (match) {
                queryString = match[1];
            }

            this.tokens = this.tokenizer.tokenize(queryString);
            this.pos = 0;

            const table = this.parseTable();
            const selectFields = this.peek('SELECT') ? this.parseSelect() : null;
            const whereExpr = this.peek('WHERE') ? this.parseWhere() : null;
            const [orderBy, orderDir] = this.peek('ORDER') ? this.parseOrderBy() : [null, SortOrder.ASC];
            const limit = this.peek('LIMIT') ? this.parseLimit() : null;
            const offset = this.peek('OFFSET') ? this.parseOffset() : 0;

            return {
                table,
                selectFields,
                whereExpression: whereExpr,
                orderBy,
                orderDirection: orderDir,
                limit,
                offset
            };
        }

        current() {
            return this.pos < this.tokens.length ? this.tokens[this.pos] : null;
        }

        peek(type) {
            const token = this.current();
            return token && token.type === type;
        }

        consume(type) {
            const token = this.current();
            if (!token || token.type !== type) {
                throw new ATONQueryError(`Expected ${type}, got ${token ? token.type : 'EOF'}`);
            }
            this.pos++;
            return token.value;
        }

        parseTable() {
            return this.consume('IDENTIFIER');
        }

        parseSelect() {
            this.consume('SELECT');
            const fields = [this.consume('IDENTIFIER')];

            while (this.peek('COMMA')) {
                this.consume('COMMA');
                fields.push(this.consume('IDENTIFIER'));
            }

            return fields;
        }

        parseWhere() {
            this.consume('WHERE');
            return this.parseOrExpression();
        }

        parseOrExpression() {
            const left = this.parseAndExpression();

            if (this.peek('OR')) {
                const conditions = [left];
                while (this.peek('OR')) {
                    this.consume('OR');
                    conditions.push(this.parseAndExpression());
                }
                return new QueryExpression(conditions, LogicalOperator.OR);
            }

            return left;
        }

        parseAndExpression() {
            const conditions = [this.parseCondition()];

            while (this.peek('AND')) {
                this.consume('AND');
                conditions.push(this.parseCondition());
            }

            return conditions.length === 1 
                ? new QueryExpression(conditions, LogicalOperator.AND)
                : new QueryExpression(conditions, LogicalOperator.AND);
        }

        parseCondition() {
            // Handle parentheses
            if (this.peek('LPAREN')) {
                this.consume('LPAREN');
                const expr = this.parseOrExpression();
                this.consume('RPAREN');
                return expr;
            }

            // Handle NOT
            if (this.peek('NOT')) {
                this.consume('NOT');
                const inner = this.parseCondition();
                return new QueryExpression([inner], LogicalOperator.NOT);
            }

            // Parse field
            const field = this.consume('IDENTIFIER');

            // Special operators
            if (this.peek('IN') || this.peek('LIKE') || this.peek('BETWEEN')) {
                return this.parseSpecialCondition(field);
            }

            // Standard operator
            const opStr = this.consume('OPERATOR');
            const opMap = {
                '=': QueryOperator.EQ,
                '!=': QueryOperator.NEQ,
                '<>': QueryOperator.NEQ,
                '<': QueryOperator.LT,
                '>': QueryOperator.GT,
                '<=': QueryOperator.LTE,
                '>=': QueryOperator.GTE
            };

            const operator = opMap[opStr];
            if (!operator) {
                throw new ATONQueryError(`Unknown operator: ${opStr}`);
            }

            const value = this.parseValue();
            return new QueryCondition(field, operator, value);
        }

        parseSpecialCondition(field) {
            if (this.peek('IN')) {
                this.consume('IN');
                this.consume('LPAREN');

                const values = [this.parseValue()];
                while (this.peek('COMMA')) {
                    this.consume('COMMA');
                    values.push(this.parseValue());
                }

                this.consume('RPAREN');
                return new QueryCondition(field, QueryOperator.IN, values);
            } else if (this.peek('LIKE')) {
                this.consume('LIKE');
                const pattern = this.parseValue();
                return new QueryCondition(field, QueryOperator.LIKE, pattern);
            } else if (this.peek('BETWEEN')) {
                this.consume('BETWEEN');
                const val1 = this.parseValue();
                this.consume('AND');
                const val2 = this.parseValue();
                return new QueryCondition(field, QueryOperator.BETWEEN, val1, val2);
            }

            throw new ATONQueryError('Invalid special condition');
        }

        parseValue() {
            if (this.peek('STRING')) {
                const value = this.consume('STRING');
                return value.slice(1, -1); // Remove quotes
            } else if (this.peek('NUMBER')) {
                const value = this.consume('NUMBER');
                return value.includes('.') ? parseFloat(value) : parseInt(value);
            } else if (this.peek('IDENTIFIER')) {
                const value = this.consume('IDENTIFIER');
                const upper = value.toUpperCase();
                if (upper === 'TRUE') return true;
                if (upper === 'FALSE') return false;
                if (upper === 'NULL') return null;
                return value;
            }

            throw new ATONQueryError('Expected value');
        }

        parseOrderBy() {
            this.consume('ORDER');
            const field = this.consume('IDENTIFIER');

            let direction = SortOrder.ASC;
            if (this.peek('ASC')) {
                this.consume('ASC');
            } else if (this.peek('DESC')) {
                this.consume('DESC');
                direction = SortOrder.DESC;
            }

            return [field, direction];
        }

        parseLimit() {
            this.consume('LIMIT');
            return parseInt(this.consume('NUMBER'));
        }

        parseOffset() {
            this.consume('OFFSET');
            return parseInt(this.consume('NUMBER'));
        }
    }

    // ========================================================================
    // QUERY ENGINE
    // ========================================================================

    class ATONQueryEngine {
        constructor() {
            this.parser = new QueryParser();
        }

        parse(queryString) {
            return this.parser.parse(queryString);
        }

        execute(data, query) {
            if (!(query.table in data)) {
                throw new ATONQueryError(`Table '${query.table}' not found`);
            }

            let records = data[query.table];

            // WHERE filtering
            if (query.whereExpression) {
                records = records.filter(r => query.whereExpression.evaluate(r));
            }

            // SELECT projection
            if (query.selectFields) {
                records = records.map(record => {
                    const projected = {};
                    for (const field of query.selectFields) {
                        if (field in record) {
                            projected[field] = record[field];
                        }
                    }
                    return projected;
                });
            }

            // ORDER BY
            if (query.orderBy) {
                const reverse = query.orderDirection === SortOrder.DESC;
                records.sort((a, b) => {
                    const aVal = a[query.orderBy] || 0;
                    const bVal = b[query.orderBy] || 0;
                    return reverse ? bVal - aVal : aVal - bVal;
                });
            }

            // OFFSET
            if (query.offset) {
                records = records.slice(query.offset);
            }

            // LIMIT
            if (query.limit) {
                records = records.slice(0, query.limit);
            }

            return records;
        }
    }

    // ========================================================================
    // COMPRESSION ENGINE
    // ========================================================================

    class DictionaryCompression {
        constructor(minLength = 5, minOccurrences = 3) {
            this.minLength = minLength;
            this.minOccurrences = minOccurrences;
            this.dictionary = {};
            this.refCounter = 0;
        }

        compress(data) {
            const strings = this.extractStrings(data);
            const stringCounts = this.countOccurrences(strings);

            // Build dictionary
            this.dictionary = {};
            for (const [string, count] of Object.entries(stringCounts)) {
                if (string.length >= this.minLength && 
                    count >= this.minOccurrences &&
                    !string.startsWith('#')) {
                    const ref = `#${this.refCounter++}`;
                    this.dictionary[ref] = string;
                }
            }

            // Create reverse map
            const reverseDict = {};
            for (const [ref, string] of Object.entries(this.dictionary)) {
                reverseDict[string] = ref;
            }

            // Replace strings
            const compressed = this.replaceStrings(data, reverseDict);

            return { compressed, dictionary: this.dictionary };
        }

        extractStrings(obj, strings = []) {
            if (typeof obj === 'string') {
                strings.push(obj);
            } else if (Array.isArray(obj)) {
                for (const item of obj) {
                    this.extractStrings(item, strings);
                }
            } else if (obj && typeof obj === 'object') {
                for (const value of Object.values(obj)) {
                    this.extractStrings(value, strings);
                }
            }
            return strings;
        }

        countOccurrences(strings) {
            const counts = {};
            for (const str of strings) {
                counts[str] = (counts[str] || 0) + 1;
            }
            return counts;
        }

        replaceStrings(obj, refMap) {
            if (typeof obj === 'string' && obj in refMap) {
                return refMap[obj];
            } else if (Array.isArray(obj)) {
                return obj.map(item => this.replaceStrings(item, refMap));
            } else if (obj && typeof obj === 'object') {
                const result = {};
                for (const [key, value] of Object.entries(obj)) {
                    result[key] = this.replaceStrings(value, refMap);
                }
                return result;
            }
            return obj;
        }
    }

    class ATONCompressionEngine {
        constructor(mode = CompressionMode.BALANCED) {
            this.mode = mode;
        }

        compress(data) {
            const startTime = Date.now();

            let compressed, metadata;

            switch (this.mode) {
                case CompressionMode.FAST:
                    ({ compressed, metadata } = this.compressFast(data));
                    break;
                case CompressionMode.BALANCED:
                    ({ compressed, metadata } = this.compressBalanced(data));
                    break;
                case CompressionMode.ULTRA:
                    ({ compressed, metadata } = this.compressUltra(data));
                    break;
                case CompressionMode.ADAPTIVE:
                    ({ compressed, metadata } = this.compressAdaptive(data));
                    break;
                default:
                    compressed = data;
                    metadata = {};
            }

            metadata.encodingTimeMs = Date.now() - startTime;
            return { compressed, metadata };
        }

        compressFast(data) {
            // Minimal compression
            return { compressed: data, metadata: { dictionary: {} } };
        }

        compressBalanced(data) {
            const algo = new DictionaryCompression(5, 3);
            const { compressed, dictionary } = algo.compress(data);
            return { compressed, metadata: { dictionary } };
        }

        compressUltra(data) {
            const algo = new DictionaryCompression(3, 2);
            const { compressed, dictionary } = algo.compress(data);
            return { compressed, metadata: { dictionary } };
        }

        compressAdaptive(data) {
            const dataStr = JSON.stringify(data);
            const size = dataStr.length;

            if (size < 1000) {
                return this.compressFast(data);
            } else if (size < 10000) {
                return this.compressBalanced(data);
            } else {
                return this.compressUltra(data);
            }
        }
    }

    // ========================================================================
    // STREAMING ENCODER
    // ========================================================================

    class ATONStreamEncoder {
        constructor(chunkSize = 100, compression = CompressionMode.BALANCED) {
            this.chunkSize = chunkSize;
            this.compressionMode = compression;
            this.baseEncoder = new ATONEncoder({ compression });
        }

        *streamEncode(data, tableName = null) {
            if (!tableName) {
                const keys = Object.keys(data);
                if (keys.length !== 1) {
                    throw new ATONEncodingError('Multiple tables, specify tableName');
                }
                tableName = keys[0];
            }

            const records = data[tableName];
            if (!Array.isArray(records)) {
                throw new ATONEncodingError(`Table '${tableName}' must be an array`);
            }

            const totalRecords = records.length;
            const totalChunks = Math.ceil(totalRecords / this.chunkSize);

            const schema = records.length > 0 ? this.inferSchema(records[0]) : [];
            const defaults = this.inferDefaults(records);

            for (let chunkId = 0; chunkId < totalChunks; chunkId++) {
                const startIdx = chunkId * this.chunkSize;
                const endIdx = Math.min(startIdx + this.chunkSize, totalRecords);
                const chunkRecords = records.slice(startIdx, endIdx);

                let atonChunk;
                if (chunkId === 0) {
                    const chunkData = { [tableName]: chunkRecords };
                    atonChunk = this.baseEncoder.encode(chunkData);
                } else {
                    atonChunk = this.encodeRowsOnly(chunkRecords, schema, defaults, tableName);
                }

                yield {
                    chunkId,
                    totalChunks,
                    data: atonChunk,
                    isFirst: chunkId === 0,
                    isLast: chunkId === totalChunks - 1,
                    metadata: {
                        table: tableName,
                        recordsInChunk: chunkRecords.length,
                        startIdx,
                        endIdx,
                        totalRecords,
                        progress: (chunkId + 1) / totalChunks
                    }
                };
            }
        }

        inferSchema(record) {
            const schema = [];
            for (const [key, value] of Object.entries(record)) {
                schema.push([key, this.inferType(value)]);
            }
            return schema;
        }

        inferDefaults(records) {
            if (records.length === 0) return {};

            const defaults = {};
            const sampleSize = Math.min(100, records.length);
            const fieldValues = {};

            for (const record of records.slice(0, sampleSize)) {
                for (const [key, value] of Object.entries(record)) {
                    if (!fieldValues[key]) fieldValues[key] = [];
                    fieldValues[key].push(value);
                }
            }

            for (const [field, values] of Object.entries(fieldValues)) {
                const valueCounts = {};
                for (const val of values) {
                    const key = JSON.stringify(val);
                    valueCounts[key] = (valueCounts[key] || 0) + 1;
                }

                let maxCount = 0;
                let mostCommon = null;
                for (const [val, count] of Object.entries(valueCounts)) {
                    if (count > maxCount) {
                        maxCount = count;
                        mostCommon = JSON.parse(val);
                    }
                }

                if (maxCount / values.length > 0.6) {
                    defaults[field] = mostCommon;
                }
            }

            return defaults;
        }

        inferType(value) {
            if (value === null) return ATONType.NULL;
            if (typeof value === 'boolean') return ATONType.BOOL;
            if (typeof value === 'number') {
                return Number.isInteger(value) ? ATONType.INT : ATONType.FLOAT;
            }
            if (typeof value === 'string') return ATONType.STR;
            if (Array.isArray(value)) return ATONType.ARRAY;
            if (typeof value === 'object') return ATONType.OBJECT;
            return ATONType.STR;
        }

        encodeRowsOnly(records, schema, defaults, tableName) {
            const lines = [`\n${tableName}+(${records.length}):`];

            for (const record of records) {
                const values = [];
                for (const [fieldName, fieldType] of schema) {
                    const value = record[fieldName];
                    if (fieldName in defaults && value === defaults[fieldName]) {
                        continue;
                    }
                    values.push(this.formatValue(value, fieldType));
                }
                if (values.length > 0) {
                    lines.push('  ' + values.join(', '));
                }
            }

            return lines.join('\n');
        }

        formatValue(value, typeHint) {
            if (value === null) return 'null';
            if (typeof value === 'boolean') return value ? 'true' : 'false';
            if (typeof value === 'string') {
                const escaped = value.replace(/"/g, '\\"');
                return `"${escaped}"`;
            }
            return String(value);
        }
    }

    // ========================================================================
    // MAIN ENCODER
    // ========================================================================

    class ATONEncoder {
        constructor(options = {}) {
            this.optimize = options.optimize !== false;
            this.compression = options.compression || CompressionMode.BALANCED;
            this.queryable = options.queryable || false;
            this.validate = options.validate !== false;

            this.compressionEngine = new ATONCompressionEngine(this.compression);
            this.queryEngine = new ATONQueryEngine();
        }

        encode(data, compress = true) {
            try {
                if (this.validate) {
                    this.validateData(data);
                }

                // Apply compression
                let compressedData = data;
                let dictionary = {};

                if (compress && this.compression !== CompressionMode.FAST) {
                    const result = this.compressionEngine.compress(data);
                    compressedData = result.compressed;
                    dictionary = result.metadata.dictionary || {};
                }

                // Build ATON string
                const parts = [];

                // Add dictionary
                if (Object.keys(dictionary).length > 0) {
                    parts.push(this.formatDictionary(dictionary));
                    parts.push('');
                }

                // Encode tables
                for (const [tableName, records] of Object.entries(compressedData)) {
                    if (!Array.isArray(records)) continue;

                    const schema = records.length > 0 ? this.inferSchema(records[0]) : [];
                    const defaults = this.optimize ? this.inferDefaults(records) : {};

                    // Schema
                    parts.push(this.formatSchema(schema));

                    // Defaults
                    if (Object.keys(defaults).length > 0) {
                        parts.push(this.formatDefaults(defaults));
                    }

                    // Queryable marker
                    if (this.queryable) {
                        parts.push(`@queryable[${tableName}]`);
                    }

                    // Table header
                    parts.push('');
                    parts.push(`${tableName}(${records.length}):`);

                    // Records
                    for (const record of records) {
                        const row = this.formatRecord(record, schema, defaults);
                        parts.push('  ' + row);
                    }
                }

                return parts.join('\n');

            } catch (error) {
                throw new ATONEncodingError(`Encoding failed: ${error.message}`);
            }
        }

        encodeWithQuery(data, queryString) {
            try {
                const query = this.queryEngine.parse(`@query[${queryString}]`);
                const filteredRecords = this.queryEngine.execute(data, query);
                const filteredData = { [query.table]: filteredRecords };

                const aton = this.encode(filteredData);
                return `@query[${queryString}]\n\n${aton}`;

            } catch (error) {
                throw new ATONQueryError(`Query encoding failed: ${error.message}`);
            }
        }

        estimateTokens(text) {
            const words = text.split(/\s+/).length;
            const chars = text.length;
            const punctuation = (text.match(/[,.;:()[\]{}]/g) || []).length;

            return Math.floor(chars / 4 + punctuation / 2 + words / 3);
        }

        getCompressionStats(originalData) {
            const startTime = Date.now();

            const originalAton = this.encode(originalData, false);
            const originalTokens = this.estimateTokens(originalAton);

            const result = this.compressionEngine.compress(originalData);
            const compressedAton = this.encode(result.compressed, true);
            const compressedTokens = this.estimateTokens(compressedAton);

            return {
                originalTokens,
                compressedTokens,
                compressionRatio: compressedTokens / originalTokens,
                modeUsed: this.compression,
                dictionarySize: Object.keys(result.metadata.dictionary || {}).length,
                encodingTimeMs: Date.now() - startTime,
                savingsPercent: ((originalTokens - compressedTokens) / originalTokens) * 100
            };
        }

        validateData(data) {
            if (!data || typeof data !== 'object') {
                throw new ATONEncodingError('Data must be an object');
            }

            for (const [tableName, records] of Object.entries(data)) {
                if (typeof tableName !== 'string') {
                    throw new ATONEncodingError('Table names must be strings');
                }
                if (!Array.isArray(records)) {
                    throw new ATONEncodingError(`Table '${tableName}' must be an array`);
                }
                for (let i = 0; i < records.length; i++) {
                    if (!records[i] || typeof records[i] !== 'object') {
                        throw new ATONEncodingError(`Record ${i} in '${tableName}' must be an object`);
                    }
                }
            }
        }

        formatDictionary(dictionary) {
            const entries = [];
            for (const [key, value] of Object.entries(dictionary).sort()) {
                const escaped = value.replace(/"/g, '\\"');
                entries.push(`${key}:"${escaped}"`);
            }
            return `@dict[${entries.join(', ')}]`;
        }

        formatSchema(schema) {
            const fields = schema.map(([name, type]) => `${name}:${type}`);
            return `@schema[${fields.join(', ')}]`;
        }

        formatDefaults(defaults) {
            const entries = [];
            for (const [key, value] of Object.entries(defaults).sort()) {
                if (typeof value === 'string') {
                    const escaped = value.replace(/"/g, '\\"');
                    entries.push(`${key}:"${escaped}"`);
                } else if (typeof value === 'boolean') {
                    entries.push(`${key}:${value ? 'true' : 'false'}`);
                } else if (value === null) {
                    entries.push(`${key}:null`);
                } else {
                    entries.push(`${key}:${value}`);
                }
            }
            return `@defaults[${entries.join(', ')}]`;
        }

        formatRecord(record, schema, defaults) {
            const values = [];

            for (const [fieldName, fieldType] of schema) {
                const value = record[fieldName];

                if (fieldName in defaults && value === defaults[fieldName]) {
                    continue;
                }

                if (value === null) {
                    values.push('null');
                } else if (typeof value === 'boolean') {
                    values.push(value ? 'true' : 'false');
                } else if (typeof value === 'string') {
                    if (value.startsWith('#')) {
                        values.push(value);
                    } else {
                        const escaped = value.replace(/"/g, '\\"');
                        values.push(`"${escaped}"`);
                    }
                } else {
                    values.push(String(value));
                }
            }

            return values.join(', ');
        }

        inferSchema(record) {
            const schema = [];
            for (const [key, value] of Object.entries(record)) {
                schema.push([key, this.inferType(value)]);
            }
            return schema;
        }

        inferDefaults(records) {
            if (records.length === 0) return {};

            const defaults = {};
            const sampleSize = Math.min(100, records.length);
            const fieldValues = {};

            for (const record of records.slice(0, sampleSize)) {
                for (const [key, value] of Object.entries(record)) {
                    if (!fieldValues[key]) fieldValues[key] = [];
                    fieldValues[key].push(value);
                }
            }

            for (const [field, values] of Object.entries(fieldValues)) {
                const valueCounts = {};
                for (const val of values) {
                    const key = JSON.stringify(val);
                    valueCounts[key] = (valueCounts[key] || 0) + 1;
                }

                let maxCount = 0;
                let mostCommon = null;
                for (const [val, count] of Object.entries(valueCounts)) {
                    if (count > maxCount) {
                        maxCount = count;
                        mostCommon = JSON.parse(val);
                    }
                }

                if (maxCount / values.length > 0.6) {
                    defaults[field] = mostCommon;
                }
            }

            return defaults;
        }

        inferType(value) {
            if (value === null) return ATONType.NULL;
            if (typeof value === 'boolean') return ATONType.BOOL;
            if (typeof value === 'number') {
                return Number.isInteger(value) ? ATONType.INT : ATONType.FLOAT;
            }
            if (typeof value === 'string') return ATONType.STR;
            if (Array.isArray(value)) return ATONType.ARRAY;
            if (typeof value === 'object') return ATONType.OBJECT;
            return ATONType.STR;
        }
    }

    // ========================================================================
    // DECODER
    // ========================================================================

    class ATONDecoder {
        constructor(options = {}) {
            this.validate = options.validate !== false;
            this.dictionary = {};
        }

        decode(atonString) {
            try {
                const lines = atonString.trim().split('\n');
                const result = {};
                let currentTable = null;
                let schema = [];
                let defaults = {};

                for (let i = 0; i < lines.length; i++) {
                    const line = lines[i].trim();

                    if (!line) continue;

                    if (line.startsWith('@dict')) {
                        this.dictionary = this.parseDictionary(line);
                    } else if (line.startsWith('@schema')) {
                        schema = this.parseSchema(line);
                    } else if (line.startsWith('@defaults')) {
                        defaults = this.parseDefaults(line);
                    } else if (line.startsWith('@query') || line.startsWith('@queryable')) {
                        continue;
                    } else if (line.includes('(') && line.endsWith('):')) {
                        const tableName = line.split('(')[0].trim();
                        currentTable = tableName;
                        result[tableName] = [];
                    } else if (line.includes('+(') && line.endsWith('):')) {
                        continue; // Continuation
                    } else if (line && currentTable && !line.startsWith('@')) {
                        const record = this.parseRecord(line, schema, defaults);
                        if (record) {
                            result[currentTable].push(record);
                        }
                    }
                }

                if (this.validate) {
                    this.validateDecoded(result);
                }

                return result;

            } catch (error) {
                throw new ATONDecodingError(`Decoding failed: ${error.message}`);
            }
        }

        parseDictionary(line) {
            const content = this.extractBrackets(line, '@dict');
            const dictionary = {};
            const entries = this.smartSplit(content, ',');

            for (const entry of entries) {
                if (entry.includes(':')) {
                    const [key, value] = entry.split(':', 2);
                    const unquoted = value.trim().replace(/^"|"$/g, '').replace(/\\"/g, '"');
                    dictionary[key.trim()] = unquoted;
                }
            }

            return dictionary;
        }

        parseSchema(line) {
            const content = this.extractBrackets(line, '@schema');
            const schema = [];
            const fields = this.smartSplit(content, ',');

            for (const field of fields) {
                if (field.includes(':')) {
                    const [name, type] = field.split(':', 2);
                    schema.push([name.trim(), type.trim()]);
                }
            }

            return schema;
        }

        parseDefaults(line) {
            const content = this.extractBrackets(line, '@defaults');
            const defaults = {};
            const entries = this.smartSplit(content, ',');

            for (const entry of entries) {
                if (entry.includes(':')) {
                    const [key, value] = entry.split(':', 2);
                    defaults[key.trim()] = this.parseValue(value.trim());
                }
            }

            return defaults;
        }

        parseRecord(line, schema, defaults) {
            const values = this.smartSplit(line.trim(), ',');
            const record = {};

            // Apply defaults
            for (const [fieldName] of schema) {
                if (fieldName in defaults) {
                    record[fieldName] = defaults[fieldName];
                }
            }

            // Parse values
            let valueIdx = 0;
            for (const [fieldName] of schema) {
                if (valueIdx < values.length) {
                    let parsedValue = this.parseValue(values[valueIdx].trim());

                    // Resolve dictionary reference
                    if (typeof parsedValue === 'string' && 
                        parsedValue.startsWith('#') && 
                        parsedValue in this.dictionary) {
                        parsedValue = this.dictionary[parsedValue];
                    }

                    record[fieldName] = parsedValue;
                    valueIdx++;
                }
            }

            return record;
        }

        parseValue(value) {
            if (value === 'null') return null;
            if (value === 'true') return true;
            if (value === 'false') return false;

            if (value.startsWith('"') && value.endsWith('"')) {
                return value.slice(1, -1).replace(/\\"/g, '"');
            }

            if (value.startsWith('#')) {
                return value;
            }

            if (!isNaN(value)) {
                return value.includes('.') ? parseFloat(value) : parseInt(value);
            }

            return value;
        }

        extractBrackets(line, directive) {
            const start = line.indexOf('[') + 1;
            const end = line.lastIndexOf(']');
            return line.substring(start, end);
        }

        smartSplit(text, delimiter) {
            const parts = [];
            let current = '';
            let inQuotes = false;

            for (const char of text) {
                if (char === '"') {
                    inQuotes = !inQuotes;
                    current += char;
                } else if (char === delimiter && !inQuotes) {
                    if (current.trim()) {
                        parts.push(current.trim());
                    }
                    current = '';
                } else {
                    current += char;
                }
            }

            if (current.trim()) {
                parts.push(current.trim());
            }

            return parts;
        }

        validateDecoded(data) {
            if (!data || typeof data !== 'object') {
                throw new ATONDecodingError('Decoded data must be an object');
            }

            for (const [tableName, records] of Object.entries(data)) {
                if (!Array.isArray(records)) {
                    throw new ATONDecodingError(`Table '${tableName}' must be an array`);
                }
                for (const record of records) {
                    if (!record || typeof record !== 'object') {
                        throw new ATONDecodingError(`Invalid record in '${tableName}'`);
                    }
                }
            }
        }
    }

    // ========================================================================
    // EXPORTS
    // ========================================================================

    const ATON = {
        // Core classes
        Encoder: ATONEncoder,
        Decoder: ATONDecoder,
        StreamEncoder: ATONStreamEncoder,
        QueryEngine: ATONQueryEngine,

        // Enums
        CompressionMode,
        QueryOperator,
        LogicalOperator,
        SortOrder,
        ATONType,

        // Exceptions
        ATONError,
        ATONEncodingError,
        ATONDecodingError,
        ATONQueryError,

        // Version
        version: '2.0.0'
    };

    // Export for different environments
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = ATON;
    } else if (typeof define === 'function' && define.amd) {
        define([], function() { return ATON; });
    } else {
        global.ATON = ATON;
    }

})(typeof window !== 'undefined' ? window : global);
