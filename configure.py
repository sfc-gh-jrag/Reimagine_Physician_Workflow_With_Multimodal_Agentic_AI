#!/usr/bin/env python3
"""
Customize all project files for your Snowflake database, schema, account, and warehouse.

Usage:
    python3 configure.py                                    # Interactive prompts
    python3 configure.py --db MY_DB --schema MY_SCHEMA      # Direct
    python3 configure.py --db MY_DB --schema MY_SCHEMA --account myorg-myaccount --warehouse MY_WH
"""
import argparse
import os
import re

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

DEFAULTS = {
    "db": "DEMO_DB",
    "schema": "HIMSS_DEMO",
    "account": "myorg-myaccount",
    "warehouse": "DEMO_BUILD_WH",
}


def regex_replace_in_file(path, patterns):
    with open(path, "r") as f:
        content = f.read()
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    with open(path, "w") as f:
        f.write(content)


def configure(db, schema, account, warehouse):
    changes = []

    yaml_path = os.path.join(REPO_ROOT, "sql", "himss_patient_semantic_model.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r") as f:
            content = f.read()
        old_db = re.search(r"database: (\w+)", content)
        old_schema = re.search(r"schema: (\w+)", content)
        if old_db and old_schema:
            prev_db, prev_schema = old_db.group(1), old_schema.group(1)
            old_fqn = f"{prev_db}.{prev_schema}"
            new_fqn = f"{db}.{schema}"
            content = content.replace(f"database: {prev_db}", f"database: {db}")
            content = content.replace(f"schema: {prev_schema}", f"schema: {schema}")
            content = content.replace(f"{old_fqn}.", f"{new_fqn}.")
            with open(yaml_path, "w") as f:
                f.write(content)
            changes.append(f"  sql/himss_patient_semantic_model.yaml  ({old_fqn} -> {new_fqn})")

    setup_path = os.path.join(REPO_ROOT, "sql", "setup_data.sql")
    if os.path.exists(setup_path):
        regex_replace_in_file(setup_path, [
            (r"SET MY_DB = '[^']*';", f"SET MY_DB = '{db}';"),
            (r"SET MY_SCHEMA = '[^']*';", f"SET MY_SCHEMA = '{schema}';"),
            (r"SET MY_WAREHOUSE = '[^']*';", f"SET MY_WAREHOUSE = '{warehouse}';"),
        ])
        changes.append(f"  sql/setup_data.sql  (MY_DB={db}, MY_SCHEMA={schema}, MY_WAREHOUSE={warehouse})")

    deploy_path = os.path.join(REPO_ROOT, "sql", "deploy_medgemma.sql")
    if os.path.exists(deploy_path):
        regex_replace_in_file(deploy_path, [
            (r"SET MY_DB = '[^']*';", f"SET MY_DB = '{db}';"),
            (r"SET MY_SCHEMA = '[^']*';", f"SET MY_SCHEMA = '{schema}';"),
        ])
        changes.append(f"  sql/deploy_medgemma.sql  (MY_DB={db}, MY_SCHEMA={schema})")

    env_path = os.path.join(REPO_ROOT, "himss-physician-app", ".env.example")
    if os.path.exists(env_path):
        regex_replace_in_file(env_path, [
            (r"VITE_SNOWFLAKE_ACCOUNT=.*", f"VITE_SNOWFLAKE_ACCOUNT={account}"),
            (r"VITE_SNOWFLAKE_DATABASE=.*", f"VITE_SNOWFLAKE_DATABASE={db}"),
            (r"VITE_SNOWFLAKE_SCHEMA=.*", f"VITE_SNOWFLAKE_SCHEMA={schema}"),
        ])
        changes.append(f"  himss-physician-app/.env.example  (account={account}, db={db}, schema={schema})")

    return changes


def main():
    parser = argparse.ArgumentParser(description="Configure PhysicianAssist for your Snowflake environment")
    parser.add_argument("--db", help=f"Database name (default: {DEFAULTS['db']})")
    parser.add_argument("--schema", help=f"Schema name (default: {DEFAULTS['schema']})")
    parser.add_argument("--account", help=f"Snowflake account identifier (default: {DEFAULTS['account']})")
    parser.add_argument("--warehouse", help=f"Warehouse name (default: {DEFAULTS['warehouse']})")
    args = parser.parse_args()

    db = args.db or input(f"Database name [{DEFAULTS['db']}]: ").strip() or DEFAULTS["db"]
    schema = args.schema or input(f"Schema name [{DEFAULTS['schema']}]: ").strip() or DEFAULTS["schema"]
    account = args.account or input(f"Snowflake account [{DEFAULTS['account']}]: ").strip() or DEFAULTS["account"]
    warehouse = args.warehouse or input(f"Warehouse [{DEFAULTS['warehouse']}]: ").strip() or DEFAULTS["warehouse"]

    print(f"\nConfiguring for: {db}.{schema} on {account} (warehouse: {warehouse})\n")
    changes = configure(db, schema, account, warehouse)

    if changes:
        print("Updated files:")
        for c in changes:
            print(c)
        print(f"\nNext steps:")
        print(f"  1. cd himss-physician-app && cp .env.example .env.local")
        print(f"  2. Edit .env.local — add your Snowflake PAT")
        print(f"  3. Run sql/deploy_medgemma.sql in Snowflake")
        print(f"  4. Run sql/setup_data.sql in Snowflake")
    else:
        print("No files needed updating.")


if __name__ == "__main__":
    main()
