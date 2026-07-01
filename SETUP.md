# L181 Sales Dashboard — Claude Setup Guide

## 🔗 Links
- **Dashboard**: https://rakhi966.github.io/l181-dashboard
- **GitHub Repo**: https://github.com/Rakhi966/l181-dashboard

## 👤 Credentials (keep safe)
- **GitHub Username**: Rakhi966
- **GitHub Token**: YOUR_GITHUB_TOKEN_HERE
- **Repo**: l181-dashboard

## 📋 Naye Claude Session mein kya karna hai

Naya Claude session shuru karo aur ye message paste karo:

---

> Mera ek L181 Sales Dashboard hai jo GitHub Pages pe host hai.
> Repo: https://github.com/Rakhi966/l181-dashboard
> Dashboard: https://rakhi966.github.io/l181-dashboard
> GitHub Token: YOUR_GITHUB_TOKEN_HERE
>
> Is repo mein `process.py` script hai — use karke daily sales data add karna hai.
>
> Aaj ka kaam: [DATE] ka data add karna hai.
> Files: [ORDER ZIP FILES + PRICING FILE] attach kar raha hoon.
>
> process.py aur SETUP.md GitHub se padh ke kaam shuru karo.

---

## 📁 Report Rules
- **Sirf whl181_ prefix** wale SKUs
- **Status**: paid + partially_refunded (dono include)
- **Pricing file**: Dropshipper G column = Sales Price, Yellow column = Cost
- **SKU Mapping file**: `SKU_EDIT_IN_WHL181.xlsx` — old SKU ko new SKU se map karta hai for pricing

## 📊 Report Columns
`SKU | Sales Qty | Sales Price | Selling Value | Cost | Costing Value | Profit`

## ⚠️ Important Rules
1. Agar koi SKU ka cost na mile → pricing file maango, push mat karo
2. SKU mapping file `SKU_EDIT_IN_WHL181.xlsx` hamesha use karo
3. Repo/account kabhi delete mat karna
4. Repo **Public** hi rakhna

## 🗓️ Dates Already in Dashboard
- June 01 to June 29, 2026 (sabhi dates)

## 🔄 Daily Workflow
1. User deta hai: Date + Order ZIP files + Pricing file (agar nayi ho)
2. Claude: process.py logic se data extract karta hai
3. Claude: GitHub API se data.json update karta hai
4. Dashboard same link pe auto-update ho jata hai ✅
