"""
L181 Sales Dashboard — Data Processing Script
==============================================
GITHUB REPO  : https://github.com/Rakhi966/l181-dashboard
DASHBOARD    : https://rakhi966.github.io/l181-dashboard
CREATED BY   : Sujal

HOW TO USE:
  1. Give this file + order zip files + pricing xlsx to Claude
  2. Tell Claude: "Add [date] data to dashboard"
  3. Claude will run this script and push to GitHub automatically

REQUIREMENTS:
  pip install pandas openpyxl pytz
"""

import pandas as pd, json, base64, urllib.request, urllib.error, pytz, datetime, sys, zipfile, io

# ─── CONFIG ──────────────────────────────────────────────────────────────────
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN_HERE"
GITHUB_USER  = "Rakhi966"
GITHUB_REPO  = "l181-dashboard"
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github.v3+json"
}

def gh(method, url, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def load_orders_from_zips(zip_paths):
    dfs = []
    for zpath in zip_paths:
        try:
            with zipfile.ZipFile(zpath) as z:
                for name in z.namelist():
                    if name.endswith('.csv'):
                        with z.open(name) as f:
                            dfs.append(pd.read_csv(f, dtype=str, low_memory=False))
        except:
            dfs.append(pd.read_csv(zpath, dtype=str, low_memory=False))
    return pd.concat(dfs, ignore_index=True)


def process_date(all_orders, target_date, pricing_df, sku_mapping=None):
    """
    Process orders for a single date.
    - target_date: datetime.date object
    - pricing_df: DataFrame with columns [SKU, Web Price, Cost]
    - sku_mapping: dict of {old_sku: new_sku} for SKU renames (optional)
    """
    df = all_orders.copy()
    df['Financial Status'] = df['Financial Status'].ffill()
    df['Created at'] = pd.to_datetime(df['Created at'], utc=True, errors='coerce').ffill()

    ist = pytz.timezone('Asia/Kolkata')
    df['Date_IST'] = df['Created at'].dt.tz_convert(ist).dt.date

    df_d = df[
        (df['Date_IST'] == target_date) &
        (df['Lineitem sku'].fillna('').str.startswith('whl181_')) &
        (df['Financial Status'].isin(['paid', 'partially_refunded']))
    ].copy()

    df_d['Lineitem quantity'] = pd.to_numeric(df_d['Lineitem quantity'], errors='coerce').fillna(0)
    df_d['Lineitem price']    = pd.to_numeric(df_d['Lineitem price'],    errors='coerce').fillna(0)
    df_d['Line Total']        = df_d['Lineitem quantity'] * df_d['Lineitem price']

    grouped = df_d.groupby('Lineitem sku').agg(
        Sales_Qty=('Lineitem quantity', 'sum'),
        Selling_Value=('Line Total', 'sum')
    ).reset_index()
    grouped.columns = ['SKU', 'Sales Qty', 'Selling Value']
    grouped['Sales Price']   = (grouped['Selling Value'] / grouped['Sales Qty']).round(2)
    grouped['Selling Value'] = grouped['Selling Value'].round(2)

    # SKU mapping for pricing lookup (old SKU -> new SKU)
    if sku_mapping:
        grouped['LookupSKU'] = grouped['SKU'].map(sku_mapping).fillna(grouped['SKU'])
    else:
        grouped['LookupSKU'] = grouped['SKU']

    final = grouped.merge(pricing_df[['SKU','Cost']], left_on='LookupSKU', right_on='SKU',
                          how='left', suffixes=('','_p'))
    final['Costing Value'] = (final['Cost'] * final['Sales Qty']).round(2)
    final['Profit']        = (final['Selling Value'] - final['Costing Value']).round(2)
    final = final.sort_values('SKU').reset_index(drop=True)

    rows = []
    for _, r in final.iterrows():
        rows.append({
            "sku": r['SKU'],
            "salesQty": int(r['Sales Qty']),
            "salesPrice": round(float(r['Sales Price']), 2),
            "sellingValue": round(float(r['Selling Value']), 2),
            "cost": round(float(r['Cost']), 2) if pd.notna(r['Cost']) else None,
            "costingValue": round(float(r['Costing Value']), 2) if pd.notna(r['Costing Value']) else None,
            "profit": round(float(r['Profit']), 2) if pd.notna(r['Profit']) else None
        })

    unmatched = [r['sku'] for r in rows if r['cost'] is None]
    print(f"  SKUs: {len(rows)} | Qty: {int(final['Sales Qty'].sum()):,} | "
          f"Sell: ₹{final['Selling Value'].sum():,.0f} | "
          f"Profit: ₹{final['Profit'].sum():,.0f} | Unmatched: {len(unmatched)}")
    if unmatched:
        print(f"  ⚠️  UNMATCHED SKUS (need pricing): {unmatched}")

    return rows, unmatched


def push_dates_to_github(date_data_dict, commit_msg):
    """
    date_data_dict: { 'YYYY-MM-DD': {'label': '...', 'rows': [...]} }
    Merges with existing data.json on GitHub and pushes.
    """
    base = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"
    current = gh("GET", f"{base}/data.json")
    sha = current['sha']
    current_data = json.loads(base64.b64decode(current['content'].replace('\n','')).decode())
    current_data['reports'].update(date_data_dict)

    print(f"\nDates in dashboard: {sorted(current_data['reports'].keys())}")
    new_content = base64.b64encode(json.dumps(current_data, separators=(',',':')).encode()).decode()
    result = gh("PUT", f"{base}/data.json", {
        "message": commit_msg,
        "content": new_content,
        "sha": sha
    })
    if "content" in result:
        print(f"✅ GitHub updated! Commit: {result['commit']['sha'][:7]}")
        print(f"🔗 https://rakhi966.github.io/l181-dashboard")
    else:
        print(f"❌ Failed: {result.get('message')}")


# ─── EXAMPLE USAGE (Claude will customize this each time) ─────────────────────
if __name__ == "__main__":
    # 1. Load pricing
    pricing = pd.read_excel('L181_Pricing.xlsx')
    pricing.columns = ['SKU', 'Web Price', 'Cost']

    # 2. Load SKU mapping (if needed for old→new SKU renames)
    # sku_map_df = pd.read_excel('SKU_EDIT_IN_WHL181.xlsx')
    # sku_mapping = dict(zip(sku_map_df['old Sku'], sku_map_df['NEW SKU']))
    sku_mapping = None   # or pass the dict above

    # 3. Load orders
    zip_files = ['orders_export_1.zip', 'orders_export_2.zip']   # add all zip files
    all_orders = load_orders_from_zips(zip_files)

    # 4. Process target date
    target = datetime.date(2026, 6, 30)   # change to desired date
    print(f"Processing {target}...")
    rows, unmatched = process_date(all_orders, target, pricing, sku_mapping)

    if unmatched:
        print("\n⚠️  Upload new pricing file first, then re-run!")
        sys.exit(1)

    # 5. Push to GitHub
    date_str = target.strftime('%Y-%m-%d')
    label    = target.strftime('%d %B %Y')
    push_dates_to_github(
        {date_str: {"label": label, "rows": rows}},
        commit_msg=f"Add {label} sales data"
    )
