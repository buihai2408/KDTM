#!/usr/bin/env python3
"""
Apache Superset Bootstrap Script
Personal Finance BI System - Phase 3

This script initializes Superset with:
1. Database connection to PostgreSQL
2. Datasets from BI Views
3. Pre-built charts and dashboards
"""

import requests
import json
import time
import os
import sys

# Configuration
SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')

# PostgreSQL connection
PG_HOST = os.environ.get('PG_HOST', 'postgres')
PG_PORT = os.environ.get('PG_PORT', '5432')
PG_USER = os.environ.get('PG_USER', 'superset_readonly')
PG_PASSWORD = os.environ.get('PG_PASSWORD', 'superset_pass')
PG_DATABASE = os.environ.get('PG_DATABASE', 'finance_db')

class SupersetBootstrap:
    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.access_token = None
        self.database_id = None
        self.datasets = {}
        self.charts = {}
        
    def wait_for_superset(self, max_retries=30, delay=10):
        """Wait for Superset to be ready"""
        print("⏳ Waiting for Superset to be ready...")
        for i in range(max_retries):
            try:
                response = self.session.get(f"{SUPERSET_URL}/health")
                if response.status_code == 200:
                    print("✅ Superset is ready!")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            print(f"   Attempt {i+1}/{max_retries}...")
            time.sleep(delay)
        print("❌ Superset did not become ready in time")
        return False
    
    def login(self):
        """Login to Superset and get access token"""
        print("🔐 Logging in to Superset...")
        
        # Get CSRF token
        response = self.session.get(f"{SUPERSET_URL}/login/")
        
        # Login
        login_data = {
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD,
            'provider': 'db',
            'refresh': True
        }
        
        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/security/login",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
            print("✅ Login successful!")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    
    def get_csrf_token(self):
        """Get CSRF token for mutations"""
        response = self.session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
        if response.status_code == 200:
            self.csrf_token = response.json().get('result')
            self.session.headers.update({'X-CSRFToken': self.csrf_token})
            return True
        return False
    
    def create_database_connection(self):
        """Create PostgreSQL database connection"""
        print("🔗 Creating database connection...")
        
        sqlalchemy_uri = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
        
        database_data = {
            "database_name": "Finance Database",
            "engine": "postgresql",
            "configuration_method": "sqlalchemy_form",
            "sqlalchemy_uri": sqlalchemy_uri,
            "expose_in_sqllab": True,
            "allow_ctas": False,
            "allow_cvas": False,
            "allow_dml": False,
            "allow_run_async": True,
            "cache_timeout": 300,
            "extra": json.dumps({
                "metadata_params": {},
                "engine_params": {},
                "metadata_cache_timeout": {},
                "schemas_allowed_for_file_upload": []
            })
        }
        
        # Check if database already exists
        response = self.session.get(f"{SUPERSET_URL}/api/v1/database/")
        if response.status_code == 200:
            databases = response.json().get('result', [])
            for db in databases:
                if db.get('database_name') == 'Finance Database':
                    self.database_id = db.get('id')
                    print(f"✅ Database connection already exists (ID: {self.database_id})")
                    return True
        
        # Create new database connection
        self.get_csrf_token()
        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/database/",
            json=database_data
        )
        
        if response.status_code in [200, 201]:
            self.database_id = response.json().get('id')
            print(f"✅ Database connection created (ID: {self.database_id})")
            return True
        else:
            print(f"❌ Failed to create database: {response.text}")
            return False
    
    def create_dataset(self, table_name, schema='public'):
        """Create a dataset from a table/view"""
        print(f"   Creating dataset: {table_name}...")
        
        dataset_data = {
            "database": self.database_id,
            "table_name": table_name,
            "schema": schema,
            "owners": []
        }
        
        self.get_csrf_token()
        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/dataset/",
            json=dataset_data
        )
        
        if response.status_code in [200, 201]:
            dataset_id = response.json().get('id')
            self.datasets[table_name] = dataset_id
            print(f"      ✅ Created (ID: {dataset_id})")
            return dataset_id
        elif response.status_code == 422:
            # Dataset might already exist, try to find it
            response = self.session.get(f"{SUPERSET_URL}/api/v1/dataset/")
            if response.status_code == 200:
                for ds in response.json().get('result', []):
                    if ds.get('table_name') == table_name:
                        self.datasets[table_name] = ds.get('id')
                        print(f"      ✅ Already exists (ID: {ds.get('id')})")
                        return ds.get('id')
        
        print(f"      ❌ Failed: {response.text}")
        return None
    
    def create_all_datasets(self):
        """Create datasets for all BI views"""
        print("📊 Creating datasets...")
        
        views = [
            # Core views
            'transactions',
            'categories', 
            'wallets',
            'budgets',
            'users',
            
            # Basic BI views
            'v_daily_summary',
            'v_monthly_summary',
            'v_category_breakdown',
            'v_income_vs_expense',
            'v_budget_vs_actual',
            'v_wallet_balance',
            'v_recent_transactions',
            
            # Advanced BI views (Phase 3)
            'dim_date',
            'v_fact_transactions',
            'v_weekly_trends',
            'v_spending_by_day_of_week',
            'v_spending_by_hour',
            'v_monthly_cashflow',
            'v_category_growth',
            'v_top_categories',
            'v_budget_performance',
            'v_savings_rate',
            'v_wallet_analytics',
            'v_user_financial_health',
            'v_expense_forecast',
            'v_kpi_summary',
            'v_transaction_comparison'
        ]
        
        for view in views:
            self.create_dataset(view)
        
        print("✅ All datasets created!")
    
    def create_chart(self, chart_config):
        """Create a chart"""
        self.get_csrf_token()
        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/chart/",
            json=chart_config
        )
        
        if response.status_code in [200, 201]:
            chart_id = response.json().get('id')
            self.charts[chart_config['slice_name']] = chart_id
            return chart_id
        return None
    
    def create_dashboard_charts(self):
        """Create all dashboard charts"""
        print("📈 Creating charts...")
        
        # Get dataset IDs
        kpi_summary_id = self.datasets.get('v_kpi_summary')
        monthly_cashflow_id = self.datasets.get('v_monthly_cashflow')
        category_breakdown_id = self.datasets.get('v_category_breakdown')
        budget_performance_id = self.datasets.get('v_budget_performance')
        weekly_trends_id = self.datasets.get('v_weekly_trends')
        savings_rate_id = self.datasets.get('v_savings_rate')
        top_categories_id = self.datasets.get('v_top_categories')
        spending_day_id = self.datasets.get('v_spending_by_day_of_week')
        wallet_analytics_id = self.datasets.get('v_wallet_analytics')
        
        charts = [
            # KPI Cards
            {
                "slice_name": "Total Income (MTD)",
                "viz_type": "big_number_total",
                "datasource_id": kpi_summary_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "mtd_income", "expressionType": "SIMPLE", "column": {"column_name": "mtd_income"}, "aggregate": "SUM"},
                    "subheader": "Month to Date",
                    "y_axis_format": ",.0f",
                    "header_font_size": 0.4,
                    "subheader_font_size": 0.15
                })
            },
            {
                "slice_name": "Total Expense (MTD)",
                "viz_type": "big_number_total",
                "datasource_id": kpi_summary_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "mtd_expense", "expressionType": "SIMPLE", "column": {"column_name": "mtd_expense"}, "aggregate": "SUM"},
                    "subheader": "Month to Date",
                    "y_axis_format": ",.0f"
                })
            },
            {
                "slice_name": "Net Savings (MTD)",
                "viz_type": "big_number_total",
                "datasource_id": kpi_summary_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "metric": {"label": "mtd_savings", "expressionType": "SIMPLE", "column": {"column_name": "mtd_savings"}, "aggregate": "SUM"},
                    "subheader": "Month to Date",
                    "y_axis_format": ",.0f"
                })
            },
            
            # Monthly Cashflow Line Chart
            {
                "slice_name": "Monthly Cashflow Trend",
                "viz_type": "echarts_timeseries_line",
                "datasource_id": monthly_cashflow_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "month_start",
                    "metrics": [
                        {"label": "Income", "expressionType": "SIMPLE", "column": {"column_name": "total_income"}, "aggregate": "SUM"},
                        {"label": "Expense", "expressionType": "SIMPLE", "column": {"column_name": "total_expense"}, "aggregate": "SUM"}
                    ],
                    "groupby": [],
                    "row_limit": 12,
                    "order_desc": False,
                    "show_legend": True,
                    "rich_tooltip": True,
                    "y_axis_format": ",.0f"
                })
            },
            
            # Category Breakdown Pie Chart
            {
                "slice_name": "Expense by Category",
                "viz_type": "pie",
                "datasource_id": category_breakdown_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["category_name"],
                    "metric": {"label": "total_amount", "expressionType": "SIMPLE", "column": {"column_name": "total_amount"}, "aggregate": "SUM"},
                    "adhoc_filters": [{"clause": "WHERE", "comparator": "expense", "expressionType": "SIMPLE", "operator": "==", "subject": "type"}],
                    "row_limit": 10,
                    "show_legend": True,
                    "show_labels": True,
                    "label_type": "key_percent"
                })
            },
            
            # Budget Performance Bar Chart
            {
                "slice_name": "Budget vs Actual",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": budget_performance_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "category_name",
                    "metrics": [
                        {"label": "Budget", "expressionType": "SIMPLE", "column": {"column_name": "budget_amount"}, "aggregate": "SUM"},
                        {"label": "Actual", "expressionType": "SIMPLE", "column": {"column_name": "actual_spent"}, "aggregate": "SUM"}
                    ],
                    "groupby": [],
                    "row_limit": 10,
                    "show_legend": True,
                    "y_axis_format": ",.0f"
                })
            },
            
            # Savings Rate Gauge
            {
                "slice_name": "Savings Rate Trend",
                "viz_type": "echarts_timeseries_line",
                "datasource_id": savings_rate_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "month_start",
                    "metrics": [{"label": "Savings Rate %", "expressionType": "SIMPLE", "column": {"column_name": "savings_rate"}, "aggregate": "AVG"}],
                    "groupby": [],
                    "row_limit": 12,
                    "show_legend": True,
                    "y_axis_format": ".1%"
                })
            },
            
            # Top Categories Table
            {
                "slice_name": "Top Spending Categories",
                "viz_type": "table",
                "datasource_id": top_categories_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["category_name"],
                    "metrics": [
                        {"label": "Total", "expressionType": "SIMPLE", "column": {"column_name": "total_amount"}, "aggregate": "SUM"},
                        {"label": "Count", "expressionType": "SIMPLE", "column": {"column_name": "transaction_count"}, "aggregate": "SUM"}
                    ],
                    "adhoc_filters": [{"clause": "WHERE", "comparator": "expense", "expressionType": "SIMPLE", "operator": "==", "subject": "type"}],
                    "row_limit": 10,
                    "order_desc": True,
                    "include_time": False,
                    "page_length": 10
                })
            },
            
            # Spending by Day of Week Heatmap
            {
                "slice_name": "Spending by Day of Week",
                "viz_type": "echarts_timeseries_bar",
                "datasource_id": spending_day_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "x_axis": "day_name",
                    "metrics": [{"label": "Amount", "expressionType": "SIMPLE", "column": {"column_name": "total_amount"}, "aggregate": "SUM"}],
                    "adhoc_filters": [{"clause": "WHERE", "comparator": "expense", "expressionType": "SIMPLE", "operator": "==", "subject": "type"}],
                    "groupby": [],
                    "row_limit": 7,
                    "show_legend": False,
                    "y_axis_format": ",.0f"
                })
            },
            
            # Wallet Balance Overview
            {
                "slice_name": "Wallet Balances",
                "viz_type": "pie",
                "datasource_id": wallet_analytics_id,
                "datasource_type": "table",
                "params": json.dumps({
                    "groupby": ["wallet_name"],
                    "metric": {"label": "Balance", "expressionType": "SIMPLE", "column": {"column_name": "current_balance"}, "aggregate": "SUM"},
                    "row_limit": 10,
                    "show_legend": True,
                    "show_labels": True,
                    "label_type": "key_value"
                })
            }
        ]
        
        for chart_config in charts:
            if chart_config.get('datasource_id'):
                chart_id = self.create_chart(chart_config)
                if chart_id:
                    print(f"   ✅ Created chart: {chart_config['slice_name']} (ID: {chart_id})")
                else:
                    print(f"   ❌ Failed to create chart: {chart_config['slice_name']}")
            else:
                print(f"   ⚠️ Skipped chart (no dataset): {chart_config['slice_name']}")
        
        print("✅ Charts created!")
    
    def create_dashboard(self):
        """Create the main dashboard"""
        print("🎨 Creating dashboard...")
        
        # Build position JSON for dashboard layout
        chart_ids = list(self.charts.values())
        
        position_json = {
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"children": ["GRID_ID"], "id": "ROOT_ID", "type": "ROOT"},
            "GRID_ID": {
                "children": [],
                "id": "GRID_ID",
                "type": "GRID",
                "parents": ["ROOT_ID"]
            },
            "HEADER_ID": {
                "id": "HEADER_ID",
                "type": "HEADER",
                "meta": {"text": "Personal Finance Dashboard"}
            }
        }
        
        # Add charts to grid
        row_index = 0
        col_index = 0
        for i, (chart_name, chart_id) in enumerate(self.charts.items()):
            chart_component_id = f"CHART-{chart_id}"
            position_json[chart_component_id] = {
                "children": [],
                "id": chart_component_id,
                "meta": {
                    "chartId": chart_id,
                    "width": 4,
                    "height": 50
                },
                "type": "CHART",
                "parents": ["ROOT_ID", "GRID_ID"]
            }
            position_json["GRID_ID"]["children"].append(chart_component_id)
        
        dashboard_data = {
            "dashboard_title": "Personal Finance Dashboard",
            "slug": "finance-dashboard",
            "owners": [],
            "position_json": json.dumps(position_json),
            "json_metadata": json.dumps({
                "timed_refresh_immune_slices": [],
                "expanded_slices": {},
                "refresh_frequency": 0,
                "default_filters": "{}",
                "color_scheme": "financeTheme",
                "label_colors": {},
                "shared_label_colors": {},
                "cross_filters_enabled": True
            }),
            "published": True
        }
        
        self.get_csrf_token()
        response = self.session.post(
            f"{SUPERSET_URL}/api/v1/dashboard/",
            json=dashboard_data
        )
        
        if response.status_code in [200, 201]:
            dashboard_id = response.json().get('id')
            print(f"✅ Dashboard created (ID: {dashboard_id})")
            print(f"   🔗 URL: {SUPERSET_URL}/superset/dashboard/{dashboard_id}/")
            return dashboard_id
        else:
            print(f"❌ Failed to create dashboard: {response.text}")
            return None
    
    def run(self):
        """Main bootstrap process"""
        print("=" * 50)
        print("🚀 Superset Bootstrap - Personal Finance BI")
        print("=" * 50)
        
        if not self.wait_for_superset():
            sys.exit(1)
        
        if not self.login():
            sys.exit(1)
        
        if not self.create_database_connection():
            sys.exit(1)
        
        self.create_all_datasets()
        self.create_dashboard_charts()
        self.create_dashboard()
        
        print("=" * 50)
        print("✅ Bootstrap complete!")
        print(f"   🔗 Superset URL: {SUPERSET_URL}")
        print(f"   👤 Username: {ADMIN_USERNAME}")
        print(f"   🔑 Password: {ADMIN_PASSWORD}")
        print("=" * 50)


if __name__ == "__main__":
    bootstrap = SupersetBootstrap()
    bootstrap.run()
