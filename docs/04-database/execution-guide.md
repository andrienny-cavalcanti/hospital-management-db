# Database Execution Guide

## Create database

```sql
CREATE DATABASE hospital_management_db;
```

## Execute scripts

```bash
psql -U postgres -d hospital_management_db -f database/schema/01-create-tables.sql
psql -U postgres -d hospital_management_db -f database/seeds/02-seed-data.sql
psql -U postgres -d hospital_management_db -f database/queries/03-crud-queries.sql
psql -U postgres -d hospital_management_db -f database/queries/04-analytical-queries.sql
```

## Recommended order

1. Create tables
2. Insert test data
3. Run CRUD queries
4. Run analytical queries
