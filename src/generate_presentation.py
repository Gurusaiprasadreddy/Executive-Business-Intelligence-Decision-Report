"""
Final Executive Decision Report & Capstone Presentation Generator.
Stage 5 Deliverable Module.

Generates:
1. outputs/Executive_Decision_Report_Final.pdf (ReportLab, 16:9 widescreen landscape 960x540pt, 15 slides)
2. outputs/Executive_Decision_Report_Final.pptx (python-pptx, 16:9 widescreen 13.333x7.5in, 15 slides)

Strictly adheres to audited numbers from Stage 4 and Stage 4.1.
Protected baseline files remain 100% untouched.
"""

import json
import os
import sys
import hashlib
import pandas as pd
import numpy as np

# Matplotlib headless backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ReportLab
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

# python-pptx
import pptx
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE


def compute_sha256(filepath: str) -> str:
    """Compute SHA256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class PresentationGenerator:
    """Enterprise-grade generator for Executive Decision Report PDF & PPTX deliverables."""

    def __init__(self, output_dir: str = "outputs", charts_dir: str = "outputs/charts"):
        self.output_dir = output_dir
        self.charts_dir = charts_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)

        # Load authoritative data
        self.load_authoritative_data()

    def load_authoritative_data(self):
        """Load and verify all authoritative metrics and scenario data."""
        with open(os.path.join(self.output_dir, "metrics.json"), "r") as f:
            self.metrics = json.load(f)

        self.reconciliation_df = pd.read_csv(os.path.join(self.output_dir, "financial_reconciliation.csv"))
        self.roi_scenarios_df = pd.read_csv(os.path.join(self.output_dir, "roi_scenarios.csv"))
        self.cash_flow_df = pd.read_csv(os.path.join(self.output_dir, "monthly_cash_flow.csv"))
        self.break_even_df = pd.read_csv(os.path.join(self.output_dir, "break_even_analysis.csv"))
        self.sensitivity_df = pd.read_csv(os.path.join(self.output_dir, "sensitivity_analysis.csv"))

        # Reconciled base numbers
        self.base_uplift = 102997.42
        self.base_total_cost = 86249.88
        self.base_net_benefit = 200722.56
        self.base_roi = 232.72
        self.base_npv = 168399.10
        self.base_payback = 8
        self.rec3_deficit = -18794.58

    def generate_all_charts(self):
        """Generate high-resolution 300 DPI analytical charts with modern executive styling."""
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

        self.chart_paths = {}

        # -------------------------------------------------------------
        # Chart 1: Financial Reconciliation Waterfall (Slide 5)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=300)
        stages = ['Raw Sales', 'Duplicates', 'Outliers', 'Clean Sales', 'COGS & Fees', 'Clean Profit']
        amounts = [4112.4, -185.3, -553.5, 3373.6, -2915.6, 458.1]
        colors = ['#1E3A8A', '#DC2626', '#EA580C', '#2563EB', '#64748B', '#059669']
        
        bars = ax.bar(stages, amounts, color=colors, width=0.55, edgecolor='none', zorder=3)
        ax.axhline(0, color='#94A3B8', linewidth=0.8, linestyle='--')
        ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=0)
        ax.set_title('Financial Reconciliation: Raw Sales to Clean Profit ($k)', fontsize=11, fontweight='bold', pad=10, color='#0F172A')
        ax.set_ylabel('Amount ($ Thousands)', fontsize=9, color='#475569')
        ax.tick_params(axis='x', rotation=18, labelsize=8.5)
        ax.tick_params(axis='y', labelsize=8.5)

        for bar in bars:
            yval = bar.get_height()
            offset = 70 if yval >= 0 else -180
            ax.annotate(f'${yval:,.1f}k',
                        xy=(bar.get_x() + bar.get_width() / 2, yval),
                        xytext=(0, offset if yval >= 0 else -12),
                        textcoords="offset points",
                        ha='center', va='bottom' if yval >= 0 else 'top',
                        fontsize=7.5, fontweight='bold', color='#1E293B')

        ax.set_ylim(-3200, 4700)
        plt.tight_layout()
        c1_path = os.path.join(self.charts_dir, 'chart1_waterfall.png')
        fig.savefig(c1_path)
        plt.close(fig)
        self.chart_paths['waterfall'] = c1_path

        # -------------------------------------------------------------
        # Chart 2: Revenue & Order Volume Trends (Slide 6)
        # -------------------------------------------------------------
        fig, ax1 = plt.subplots(figsize=(6.2, 3.4), dpi=300)
        years = ['2023', '2024', '2025']
        revenues = [896.6, 1076.6, 1400.4]
        orders = [3079, 3939, 4978]

        x = np.arange(len(years))
        width = 0.42

        bars = ax1.bar(x, revenues, width=width, color='#2563EB', alpha=0.9, label='Revenue ($k)', zorder=3)
        ax1.set_ylabel('Annual Revenue ($ Thousands)', color='#1E3A8A', fontsize=9, fontweight='bold')
        ax1.set_ylim(0, 1750)
        ax1.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)

        for bar in bars:
            yval = bar.get_height()
            ax1.annotate(f'${yval:,.1f}k',
                         xy=(bar.get_x() + bar.get_width() / 2, yval),
                         xytext=(0, 4), textcoords="offset points",
                         ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1E3A8A')

        ax2 = ax1.twinx()
        line = ax2.plot(x, orders, color='#D97706', marker='o', linewidth=2.4, markersize=6, label='Order Count', zorder=4)
        ax2.set_ylabel('Annual Order Count', color='#B45309', fontsize=9, fontweight='bold')
        ax2.set_ylim(0, 6000)

        for i, txt in enumerate(orders):
            ax2.annotate(f'{txt:,}', (x[i], orders[i]), textcoords="offset points", xytext=(0, 8),
                         ha='center', fontsize=8, fontweight='bold', color='#B45309')

        ax1.set_xticks(x)
        ax1.set_xticklabels(years, fontsize=9.5, fontweight='bold')
        ax1.set_title('Revenue & Order Volume YoY Trajectory (2023–2025)', fontsize=11, fontweight='bold', pad=10, color='#0F172A')
        plt.tight_layout()
        c2_path = os.path.join(self.charts_dir, 'chart2_revenue_orders.png')
        fig.savefig(c2_path)
        plt.close(fig)
        self.chart_paths['revenue_orders'] = c2_path

        # -------------------------------------------------------------
        # Chart 3: Revenue Growth vs Margin Compression (Slide 7)
        # -------------------------------------------------------------
        fig, ax1 = plt.subplots(figsize=(6.2, 3.4), dpi=300)
        years = ['2023', '2024', '2025']
        profits = [138.4, 152.6, 167.1]
        margins = [15.44, 14.17, 11.93]

        bars = ax1.bar(years, profits, width=0.42, color='#0D9488', alpha=0.85, label='Profit ($k)', zorder=3)
        ax1.set_ylabel('Contribution Profit ($ Thousands)', color='#0F766E', fontsize=9, fontweight='bold')
        ax1.set_ylim(0, 220)
        ax1.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)

        for bar in bars:
            yval = bar.get_height()
            ax1.annotate(f'${yval:,.1f}k',
                         xy=(bar.get_x() + bar.get_width() / 2, yval),
                         xytext=(0, 4), textcoords="offset points",
                         ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0F766E')

        ax2 = ax1.twinx()
        ax2.plot(years, margins, color='#DC2626', marker='s', linewidth=2.4, markersize=6, label='Margin %', zorder=4)
        ax2.set_ylabel('Weighted Profit Margin (%)', color='#B91C1C', fontsize=9, fontweight='bold')
        ax2.set_ylim(8, 18)

        for i, txt in enumerate(margins):
            ax2.annotate(f'{txt:.1f}%', (years[i], margins[i]), textcoords="offset points", xytext=(0, 7),
                         ha='center', fontsize=8.5, fontweight='bold', color='#B91C1C')

        ax1.set_title('Profit Growth vs. Margin Decoupling (-3.51 pp Decay)', fontsize=11, fontweight='bold', pad=10, color='#0F172A')
        plt.tight_layout()
        c3_path = os.path.join(self.charts_dir, 'chart3_margin_decay.png')
        fig.savefig(c3_path)
        plt.close(fig)
        self.chart_paths['margin_decay'] = c3_path

        # -------------------------------------------------------------
        # Chart 4: Margin by Discount Band & The Cliff (Slide 8)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=300)
        bands = ['0%', '1-10%', '11-20%', '21-30%', '>30%']
        margins_band = [28.74, 22.37, 11.79, -0.56, -22.55]
        bar_colors = ['#059669', '#10B981', '#3B82F6', '#EF4444', '#991B1B']

        bars = ax.bar(bands, margins_band, color=bar_colors, width=0.52, zorder=3)
        ax.axhline(0, color='#1E293B', linewidth=1.0)
        ax.axhline(15, color='#D97706', linewidth=1.2, linestyle='--', label='15% Policy Floor')
        ax.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)

        for bar in bars:
            yval = bar.get_height()
            offset = 4 if yval >= 0 else -14
            ax.annotate(f'{yval:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, yval),
                        xytext=(0, offset), textcoords="offset points",
                        ha='center', va='bottom' if yval >= 0 else 'top',
                        fontsize=8, fontweight='bold',
                        color='#1E293B' if yval >= 0 else '#991B1B')

        ax.set_title('Weighted Margin by Discount Band (The 20% Cliff)', fontsize=11, fontweight='bold', pad=10, color='#0F172A')
        ax.set_ylabel('Weighted Contribution Margin (%)', fontsize=9, color='#475569')
        ax.set_ylim(-28, 35)
        ax.legend(loc='upper right', fontsize=8, framealpha=0.9)
        plt.tight_layout()
        c4_path = os.path.join(self.charts_dir, 'chart4_discount_cliff.png')
        fig.savefig(c4_path)
        plt.close(fig)
        self.chart_paths['discount_cliff'] = c4_path

        # -------------------------------------------------------------
        # Chart 5: Channel Margin & Central Delay Anomaly (Slide 9)
        # -------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.2, 3.4), dpi=300)

        channels = ['Retail Store', 'Online', 'Marketplace']
        ch_margins = [21.22, 15.00, -2.55]
        ch_colors = ['#059669', '#2563EB', '#DC2626']

        bars1 = ax1.bar(channels, ch_margins, color=ch_colors, width=0.5, zorder=3)
        ax1.axhline(0, color='#64748B', linewidth=0.8)
        ax1.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
        ax1.set_title('Margin by Channel (%)', fontsize=9.5, fontweight='bold', color='#0F172A')
        ax1.set_ylim(-6, 26)
        ax1.tick_params(axis='x', rotation=15, labelsize=8)
        for bar in bars1:
            yval = bar.get_height()
            ax1.annotate(f'{yval:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, yval),
                         xytext=(0, 3 if yval >= 0 else -10), textcoords="offset points",
                         ha='center', fontsize=7.5, fontweight='bold', color='#1E293B')

        regions = ['West', 'North', 'South', 'East', 'Central']
        late_rates = [11.86, 18.68, 25.61, 29.71, 58.41]
        reg_colors = ['#3B82F6', '#3B82F6', '#F59E0B', '#EA580C', '#DC2626']

        bars2 = ax2.bar(regions, late_rates, color=reg_colors, width=0.55, zorder=3)
        ax2.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
        ax2.set_title('Late Delivery Rate by Region (%)', fontsize=9.5, fontweight='bold', color='#0F172A')
        ax2.set_ylim(0, 70)
        ax2.tick_params(axis='x', labelsize=8)
        for bar in bars2:
            yval = bar.get_height()
            ax2.annotate(f'{yval:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, yval),
                         xytext=(0, 3), textcoords="offset points",
                         ha='center', fontsize=7.5, fontweight='bold', color='#1E293B')

        plt.suptitle('Channel Drag & Central Regional Fulfillment Bottleneck', fontsize=11, fontweight='bold', color='#0F172A', y=0.98)
        plt.tight_layout()
        c5_path = os.path.join(self.charts_dir, 'chart5_channel_region.png')
        fig.savefig(c5_path)
        plt.close(fig)
        self.chart_paths['channel_region'] = c5_path

        # -------------------------------------------------------------
        # Chart 6: Delivery Timeliness vs Return Rate & Retention (Slide 10)
        # -------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.2, 3.4), dpi=300)

        groups = ['On-Time\n(<=5 Days)', 'Late\n(>5 Days)']
        return_rates = [4.78, 14.91]
        colors = ['#059669', '#DC2626']

        bars1 = ax1.bar(groups, return_rates, color=colors, width=0.48, zorder=3)
        ax1.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
        ax1.set_title('Return Rate by Delivery Status', fontsize=9.5, fontweight='bold', color='#0F172A')
        ax1.set_ylabel('Return Rate (%)', fontsize=8.5, color='#475569')
        ax1.set_ylim(0, 19)
        for bar in bars1:
            yval = bar.get_height()
            ax1.annotate(f'{yval:.1f}%\n(3.1x)', xy=(bar.get_x() + bar.get_width() / 2, yval),
                         xytext=(0, 4), textcoords="offset points",
                         ha='center', fontsize=8, fontweight='bold', color='#1E293B')

        cohorts = ['2023 -> 2024', '2024 -> 2025']
        retention = [54.39, 49.65]
        bars2 = ax2.bar(cohorts, retention, color=['#3B82F6', '#EF4444'], width=0.48, zorder=3)
        ax2.grid(axis='y', linestyle=':', alpha=0.5, zorder=0)
        ax2.set_title('Customer Cohort Retention Trend', fontsize=9.5, fontweight='bold', color='#0F172A')
        ax2.set_ylabel('Retention Rate (%)', fontsize=8.5, color='#475569')
        ax2.set_ylim(0, 65)
        for bar in bars2:
            yval = bar.get_height()
            ax2.annotate(f'{yval:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, yval),
                         xytext=(0, 4), textcoords="offset points",
                         ha='center', fontsize=8, fontweight='bold', color='#1E293B')

        plt.suptitle('Delivery Delay Correlation & Customer Retention Erosion', fontsize=11, fontweight='bold', color='#0F172A', y=0.98)
        plt.tight_layout()
        c6_path = os.path.join(self.charts_dir, 'chart6_returns_retention.png')
        fig.savefig(c6_path)
        plt.close(fig)
        self.chart_paths['returns_retention'] = c6_path

        # -------------------------------------------------------------
        # Chart 7: 36-Month Cumulative Cash Flow Trajectory (Slide 14)
        # -------------------------------------------------------------
        fig, ax = plt.subplots(figsize=(6.2, 3.4), dpi=300)
        base_df = self.cash_flow_df[self.cash_flow_df['scenario'] == 'Base'].sort_values('month')
        cons_df = self.cash_flow_df[self.cash_flow_df['scenario'] == 'Conservative'].sort_values('month')
        opt_df = self.cash_flow_df[self.cash_flow_df['scenario'] == 'Optimistic'].sort_values('month')

        months = base_df['month'].values
        cum_base = base_df['cumulative_net_cash_flow'].values / 1000.0
        cum_cons = cons_df['cumulative_net_cash_flow'].values / 1000.0
        cum_opt = opt_df['cumulative_net_cash_flow'].values / 1000.0

        ax.plot(months, cum_opt, label='Optimistic ($256k net, M5)', color='#059669', linewidth=2.0, linestyle=':')
        ax.plot(months, cum_base, label='Base Case ($201k net, M8)', color='#2563EB', linewidth=2.6)
        ax.plot(months, cum_cons, label='Conservative ($120k net, M12)', color='#EA580C', linewidth=2.0, linestyle='--')

        ax.axhline(0, color='#1E293B', linewidth=1.0)
        ax.axvline(8, color='#2563EB', linewidth=1.2, linestyle=':', label='Base Payback (M8)')
        ax.grid(True, linestyle=':', alpha=0.5)

        ax.set_title('36-Month Cumulative Net Cash Flow Trajectory ($k)', fontsize=11, fontweight='bold', pad=10, color='#0F172A')
        ax.set_xlabel('Project Month (1 to 36)', fontsize=9, color='#475569')
        ax.set_ylabel('Cumulative Net Cash ($ Thousands)', fontsize=9, color='#475569')
        ax.set_xlim(1, 36)
        ax.set_ylim(-45, 280)
        ax.legend(loc='lower right', fontsize=7.8, framealpha=0.95)
        plt.tight_layout()
        c7_path = os.path.join(self.charts_dir, 'chart7_cash_flow.png')
        fig.savefig(c7_path)
        plt.close(fig)
        self.chart_paths['cash_flow'] = c7_path

        print("All 7 analytical charts successfully generated!")

    # =========================================================================
    # PDF GENERATION (ReportLab, 960x540 Landscape)
    # =========================================================================
    def generate_pdf(self, pdf_path: str = "outputs/Executive_Decision_Report_Final.pdf"):
        """Generate pixel-perfect 15-slide PDF deliverable matching exact audited numbers."""
        c = canvas.Canvas(pdf_path, pagesize=(960, 540))
        W, H = 960, 540

        def draw_slide_base(category: str, title: str, subtitle: str, page_num: int):
            # Canvas background
            c.setFillColor(HexColor('#F8FAFC'))
            c.rect(0, 0, W, H, fill=1, stroke=0)

            # Header Banner
            c.setFillColor(HexColor('#0F2942'))
            c.rect(0, H - 76, W, 76, fill=1, stroke=0)

            # Category Pill Tag
            c.setFillColor(HexColor('#2563EB'))
            c.roundRect(40, H - 26, 240, 16, 4, fill=1, stroke=0)
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont('Helvetica-Bold', 8)
            c.drawString(48, H - 22, category.upper())

            # Title
            c.setFont('Helvetica-Bold', 17)
            c.drawString(40, H - 48, title)

            # Subtitle / Executive Takeaway
            c.setFillColor(HexColor('#94A3B8'))
            c.setFont('Helvetica', 9.5)
            c.drawString(40, H - 65, subtitle)

            # Footer
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.setLineWidth(0.8)
            c.line(40, 26, W - 40, 26)

            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 8)
            c.drawString(40, 14, "Simulated Omnichannel Retail Data (2023–2025) | Audited Stage 4 ROI Engine | Capstone Final Deliverable")
            c.drawRightString(W - 40, 14, f"Slide {page_num} of 15")

        def draw_card(x, y, w, h, bg_color='#FFFFFF', border_color='#E2E8F0'):
            c.setFillColor(HexColor(bg_color))
            c.setStrokeColor(HexColor(border_color))
            c.setLineWidth(1)
            c.roundRect(x, y, w, h, 6, fill=1, stroke=1)

        # -------------------------------------------------------------
        # SLIDE 1: Title Slide (Dark Theme)
        # -------------------------------------------------------------
        c.setFillColor(HexColor('#0B192C'))
        c.rect(0, 0, W, H, fill=1, stroke=0)

        # Decorative subtle accents
        c.setFillColor(HexColor('#1E3E62'))
        c.circle(W - 80, H - 80, 140, fill=1, stroke=0)
        c.setFillColor(HexColor('#0B192C'))
        c.circle(W - 80, H - 80, 130, fill=1, stroke=0)

        # Header Badge
        c.setFillColor(HexColor('#2563EB'))
        c.roundRect(60, H - 100, 360, 22, 4, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(72, H - 94, "DATA ANALYTICS & BUSINESS INTELLIGENCE CAPSTONE")

        # Main Title
        c.setFont('Helvetica-Bold', 32)
        c.drawString(60, H - 155, "Executive Decision Report:")
        c.setFillColor(HexColor('#38BDF8'))
        c.drawString(60, H - 195, "Retail Margin Turnaround Strategy")

        # Subtitle
        c.setFillColor(HexColor('#94A3B8'))
        c.setFont('Helvetica', 13)
        c.drawString(60, H - 235, "Three Sequenced Strategic Decisions to Lift Annual Profit by +$103k and Deliver $200.7k Net Cash Benefit")

        # Metadata Cards
        cards_y = 110
        card_w = 260
        card_h = 130

        # Card 1: Author
        draw_card(60, cards_y, card_w, card_h, bg_color='#1E293B', border_color='#334155')
        c.setFillColor(HexColor('#38BDF8'))
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(80, cards_y + 98, "AUTHOR & CONSULTANT")
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(80, cards_y + 74, "Gurusaiprasadreddy")
        c.setFillColor(HexColor('#94A3B8'))
        c.setFont('Helvetica', 9)
        c.drawString(80, cards_y + 54, "Senior Business Intelligence Consultant")
        c.drawString(80, cards_y + 38, "& Financial Analytics Lead")
        c.drawString(80, cards_y + 20, "RabTech Academy Capstone")

        # Card 2: Executive Stakeholders
        draw_card(350, cards_y, card_w, card_h, bg_color='#1E293B', border_color='#334155')
        c.setFillColor(HexColor('#38BDF8'))
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(370, cards_y + 98, "AUDIENCE & GOVERNANCE")
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(370, cards_y + 74, "Executive Leadership Team")
        c.setFillColor(HexColor('#94A3B8'))
        c.setFont('Helvetica', 9)
        c.drawString(370, cards_y + 54, "Chief Executive Officer & CFO")
        c.drawString(370, cards_y + 38, "VP Sales, VP Ops, VP E-Commerce")
        c.drawString(370, cards_y + 20, "Reporting Period: October 2026")

        # Card 3: Scope & Dataset
        draw_card(640, cards_y, card_w, card_h, bg_color='#1E293B', border_color='#334155')
        c.setFillColor(HexColor('#10B981'))
        c.setFont('Helvetica-Bold', 9.5)
        c.drawString(660, cards_y + 98, "DATASET & AUDIT STATUS")
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(660, cards_y + 74, "11,996 Orders (2023–2025)")
        c.setFillColor(HexColor('#94A3B8'))
        c.setFont('Helvetica', 9)
        c.drawString(660, cards_y + 54, "Scope: Omnichannel Retail ($3.37M Sales)")
        c.drawString(660, cards_y + 38, "Status: Audited Stage 4 Financial Engine")
        c.setFillColor(HexColor('#10B981'))
        c.drawString(660, cards_y + 20, "Consistency Audit Status: PASSED (75/75)")

        # Bottom disclosure
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica-Oblique', 8.5)
        c.drawString(60, 45, "Confidential Executive Deliverable | Simulated Dataset for BI Decision Analytics | All Financial Scenarios Validated")
        c.drawRightString(W - 60, 45, "Slide 1 of 15")
        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 2: Executive Decision Brief
        # -------------------------------------------------------------
        draw_slide_base("Executive Summary",
                        "Executive Decision Brief: Reversing Margin Decay",
                        "Revenue expanded +56% since 2023, but profit margin collapsed from 15.4% to 11.9%. Three sequenced turnaround decisions restore financial health.", 2)

        # 3 Column Cards
        col_w = 274
        col_h = 410
        col_y = 42

        # Column 1: Problem & Diagnosis
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#DC2626'))
        c.roundRect(40, col_y + col_h - 26, col_w, 26, 4, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 10)
        c.drawString(52, col_y + col_h - 18, "1. THE BUSINESS PROBLEM")

        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 11)
        c.drawString(52, col_y + col_h - 48, "Growth Is Unprofitable")
        c.setFont('Helvetica', 8.8)
        text_lines = [
            "• Revenue climbed +56.2% ($897k -> $1.40M),",
            "  but contribution profit rose only +20.7%.",
            "• Weighted margin collapsed -3.51 pp from",
            "  15.44% in 2023 down to 11.93% in 2025.",
            "",
            "Root Cause 1: Pricing Indiscipline",
            "• Discounts >20% generate -$40,094 in direct",
            "  annual losses across 1,605 transactions.",
            "",
            "Root Cause 2: Marketplace Fee Drag",
            "• Marketplace sales surged to 26% share but",
            "  yields -2.55% negative margin after 15% fees.",
            "",
            "Root Cause 3: Shipping Delay Crisis",
            "• Central region ships 58.4% of orders late,",
            "  tripling returns (14.9%) and cutting retention."
        ]
        yy = col_y + col_h - 66
        for line in text_lines:
            c.drawString(52, yy, line)
            yy -= 15

        # Column 2: The Three Strategic Decisions
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#2563EB'))
        c.roundRect(343, col_y + col_h - 26, col_w, 26, 4, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 10)
        c.drawString(355, col_y + col_h - 18, "2. THE THREE STRATEGIC DECISIONS")

        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 10)
        c.drawString(355, col_y + col_h - 48, "Decision 1: Automated Discount Guardrails")
        c.setFont('Helvetica', 8.8)
        c.drawString(355, col_y + col_h - 64, "• Hard cap discounts at 20%; 15% basket floor.")
        c.drawString(355, col_y + col_h - 78, "• Uplift: +$66,332/yr | Capex: $10k | M3 Payback.")

        c.setFont('Helvetica-Bold', 10)
        c.drawString(355, col_y + col_h - 106, "Decision 2: Marketplace Margin Repair")
        c.setFont('Helvetica', 8.8)
        c.drawString(355, col_y + col_h - 122, "• Renegotiate fee to 14% (-1 pp); cap discount 10%.")
        c.drawString(355, col_y + col_h - 136, "• Uplift: +$29,352/yr | Capex: $12k | M12 Payback.")

        c.setFont('Helvetica-Bold', 10)
        c.drawString(355, col_y + col_h - 164, "Decision 3: Delivery SLA & Retention")
        c.setFont('Helvetica', 8.8)
        c.drawString(355, col_y + col_h - 180, "• Central 3PL overhaul; reduce late to 15%.")
        c.drawString(355, col_y + col_h - 194, "• Uplift: +$7,314/yr | Capex: $12k | Strategic SLA.")

        # Sequencing Callout Box
        c.setFillColor(HexColor('#EFF6FF'))
        c.setStrokeColor(HexColor('#BFDBFE'))
        c.roundRect(353, col_y + 20, col_w - 20, 160, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(363, col_y + 160, "Sequenced Execution Logic:")
        c.setFont('Helvetica', 8.3)
        c.drawString(363, col_y + 142, "• Month 1–3: Rec 1 delivers fast cash surplus.")
        c.drawString(363, col_y + 126, "• Month 4–6: Rec 2 fixes third-party bleed.")
        c.drawString(363, col_y + 110, "• Month 7–12: Rec 3 stabilizes brand loyalty.")
        c.drawString(363, col_y + 92, "Zero Double-Counting Principle:")
        c.drawString(363, col_y + 76, "• Rec 1: Pricing governance on non-MP orders.")
        c.drawString(363, col_y + 60, "• Rec 2: MP fee reduction on non-discounted.")
        c.drawString(363, col_y + 44, "• Rec 3: Return reduction on late deliveries only.")

        # Column 3: Value & Disclosures
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#059669'))
        c.roundRect(646, col_y + col_h - 26, col_w, 26, 4, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 10)
        c.drawString(658, col_y + col_h - 18, "3. EXPECTED VALUE & DISCLOSURES")

        # Metric Badges
        metrics_box = [
            ("Annual Profit Uplift (Steady-State)", "+$102,997/yr", "#059669"),
            ("36-Month Net Cash Benefit", "+$200,723", "#059669"),
            ("Net Return on Investment (ROI)", "232.72%", "#2563EB"),
            ("Discounted NPV (@ 10% WACC)", "+$168,399", "#2563EB"),
            ("Portfolio Capital Payback", "Month 8", "#059669"),
        ]
        my = col_y + col_h - 52
        for lbl, val, colr in metrics_box:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(656, my - 24, col_w - 20, 32, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7.5)
            c.drawString(664, my - 3, lbl)
            c.setFillColor(HexColor(colr))
            c.setFont('Helvetica-Bold', 11)
            c.drawString(664, my - 18, val)
            my -= 38

        # Critical Caveat Box
        c.setFillColor(HexColor('#FEF2F2'))
        c.setStrokeColor(HexColor('#FECACA'))
        c.roundRect(656, col_y + 15, col_w - 20, 155, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#991B1B'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(664, col_y + 152, "CRITICAL EXECUTIVE DISCLOSURES:")
        c.setFont('Helvetica', 7.8)
        caveat_text = [
            "1. Rec 3 Standalone Deficit: -$18,795 over 36m.",
            "   Opex ($9.0k/yr) exceeds benefit ($7.3k/yr).",
            "   Justified as strategic SLA investment funded",
            "   by Rec 1 ($171k) & Rec 2 ($48k) cash surplus.",
            "2. Rec 1 Contagion Risk: 1,605 loss orders belong",
            "   to 825 buyers who ALSO generated $741k in",
            "   profitable sales. Use basket margin rules to",
            "   prevent customer churn contagion."
        ]
        cyy = col_y + 136
        for cline in caveat_text:
            c.drawString(664, cyy, cline)
            cyy -= 13

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 3: Business Context & Objectives
        # -------------------------------------------------------------
        draw_slide_base("Commercial Setting",
                        "Business Context & Strategic Objectives",
                        "Analyzing 11,996 transactions across three fulfillment channels, five geographic territories, and three product categories.", 3)

        # 3 Column Structure
        col_w = 274
        col_h = 410
        col_y = 42

        # Card 1: Channel Architecture
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, col_y + col_h - 30, "Omnichannel Retail Architecture")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(55, col_y + col_h - 46, "Operational mix across 3 commercial channels:")

        channels_info = [
            ("Direct Retail Store", "3,869 Orders | $1.16M Sales (34.4%)", "Profit: $245.9k | Weighted Margin: 21.22%",
             "Strongest margin profile; physical stores act as high-margin anchors with strong brand loyalty.", '#059669'),
            ("Online Direct (Web)", "5,467 Orders | $1.53M Sales (45.3%)", "Profit: $229.6k | Weighted Margin: 15.00%",
             "Primary volume driver; stable direct-to-consumer digital channel with solid unit profitability.", '#2563EB'),
            ("Third-Party Marketplace", "2,660 Orders | $684.1k Sales (20.3%)", "Profit: -$17.4k | Weighted Margin: -2.55%",
             "Fastest growing channel (+14 pp share) but losing money due to 15% platform fees & discounting.", '#DC2626')
        ]
        cy = col_y + col_h - 75
        for ch, sub1, sub2, desc, colr in channels_info:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(50, cy - 75, col_w - 20, 95, 4, fill=1, stroke=1)
            c.setFillColor(HexColor(colr))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(58, cy + 6, ch)
            c.setFillColor(HexColor('#1E293B'))
            c.setFont('Helvetica-Bold', 8.2)
            c.drawString(58, cy - 10, sub1)
            c.drawString(58, cy - 24, sub2)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7.5)
            c.drawString(58, cy - 40, desc[:42])
            c.drawString(58, cy - 52, desc[42:])
            cy -= 105

        # Card 2: Core Business Questions
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(358, col_y + col_h - 30, "Core Business Questions")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(358, col_y + col_h - 46, "Strategic investigation guiding executive action:")

        questions = [
            ("Q1: Revenue vs Profit Decoupling",
             "Why has rapid top-line growth (+56% over 3 years) produced margin compression (-3.5 pp)? What operational mechanisms caused dollar profit to lag volume?"),
            ("Q2: Loss Concentration & Subsidies",
             "Which discount bands, product categories, and sales channels are destroying capital? Where does cross-subsidization hide critical business risks?"),
            ("Q3: Delivery Quality & Customer Attrition",
             "Does shipping latency correlate with merchandise returns and customer churn? How much margin is lost through supply chain failure?"),
            ("Q4: Actionable Turnaround Roadmap",
             "What concrete, sequenced interventions can management execute within 12 months with audited positive ROI and minimal customer churn?")
        ]
        qy = col_y + col_h - 75
        for qtitle, qdesc in questions:
            c.setFillColor(HexColor('#EFF6FF'))
            c.setStrokeColor(HexColor('#BFDBFE'))
            c.roundRect(353, qy - 55, col_w - 20, 70, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#1E3A8A'))
            c.setFont('Helvetica-Bold', 9)
            c.drawString(361, qy + 2, qtitle)
            c.setFillColor(HexColor('#334155'))
            c.setFont('Helvetica', 7.8)
            words = qdesc.split()
            line1 = " ".join(words[:9])
            line2 = " ".join(words[9:18])
            line3 = " ".join(words[18:])
            c.drawString(361, qy - 14, line1)
            c.drawString(361, qy - 27, line2)
            c.drawString(361, qy - 40, line3)
            qy -= 80

        # Card 3: Strategic Imperatives
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(661, col_y + col_h - 30, "Strategic Imperatives & Scope")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(661, col_y + col_h - 46, "Guiding principles for the capstone engagement:")

        imperatives = [
            ("Shift from Volume to Profit", "Replace gross revenue targets with net contribution profit after channel fees, freight, and returns."),
            ("Stop Customer-Level Contagion", "Do not bluntly cancel orders; apply basket-level minimum margin rules to preserve profitable relationships."),
            ("Hold Third-Party Partners Accountable", "Renegotiate marketplace commission fees and 3PL carrier SLA contracts backed by penalty clauses."),
            ("Protect Repeat Customer Trust", "Repeat buyers generate 95% of orders. Service delivery quality is the primary driver of customer lifetime value.")
        ]
        iy = col_y + col_h - 75
        for ititle, idesc in imperatives:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(656, iy - 55, col_w - 20, 70, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#0F172A'))
            c.setFont('Helvetica-Bold', 9)
            c.drawString(664, iy + 2, ititle)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.8)
            words = idesc.split()
            line1 = " ".join(words[:9])
            line2 = " ".join(words[9:18])
            line3 = " ".join(words[18:])
            c.drawString(664, iy - 14, line1)
            c.drawString(664, iy - 27, line2)
            c.drawString(664, iy - 40, line3)
            iy -= 80

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 4: Data and Methodology
        # -------------------------------------------------------------
        draw_slide_base("Governance & Pipeline",
                        "Data Governance, Cleaning Pipeline & Analytics Methodology",
                        "A reproducible, 6-stage deterministic pipeline transforming 12,400 raw entries into 11,996 audited, reliable transaction records.", 4)

        col_w = 274
        col_h = 410
        col_y = 42

        # Card 1: Data Scope & Disclosure
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, col_y + col_h - 30, "Dataset Coverage & Scope")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(55, col_y + col_h - 46, "Operational parameters of the analysis:")

        scope_items = [
            ("Reporting Window", "3 Calendar Years (Jan 1, 2023 – Dec 31, 2025)"),
            ("Raw Transaction Volume", "12,400 initial transaction rows across 20 fields"),
            ("Clean Transaction Volume", "11,996 fully reconciled rows (zero missing cells)"),
            ("Geographic Scope", "5 US Regions: West, East, North, South, Central"),
            ("Merchandise Scope", "3 Categories: Furniture, Office Supplies, Technology"),
            ("Customer Base", "2,116 unique customers across B2C & B2B segments"),
        ]
        sy = col_y + col_h - 75
        for k, v in scope_items:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(50, sy - 28, col_w - 20, 36, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7.5)
            c.drawString(58, sy - 2, k)
            c.setFillColor(HexColor('#1E293B'))
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(58, sy - 17, v)
            sy -= 42

        # Simulated Data Disclosure
        c.setFillColor(HexColor('#FFFBEB'))
        c.setStrokeColor(HexColor('#FDE68A'))
        c.roundRect(50, col_y + 15, col_w - 20, 80, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#92400E'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(58, col_y + 80, "SIMULATED-DATA DISCLOSURE:")
        c.setFont('Helvetica', 7.5)
        c.drawString(58, col_y + 66, "• Dataset represents simulated omnichannel retail")
        c.drawString(58, col_y + 53, "  operations built to benchmark BI rigor.")
        c.drawString(58, col_y + 40, "• Observational data establishes strong statistical")
        c.drawString(58, col_y + 27, "  correlations, but does not prove causal certainty.")

        # Card 2: 6-Stage Cleaning Pipeline
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(358, col_y + col_h - 30, "6-Stage Cleaning Pipeline")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(358, col_y + col_h - 46, "100% deterministic, automated transformation:")

        stages_info = [
            ("Stage 1: Ingestion & Schema Typing", "Standardized date parsing and strict numeric type casting."),
            ("Stage 2: Exact Deduplication", "Identified and removed 400 exact duplicate order rows."),
            ("Stage 3: Categorical Standardization", "Consolidated 29 region variants to 5; 18 categories to 3."),
            ("Stage 4: Outlier Treatment", "Corrected 28 typographical quantity errors (up to 900) to median."),
            ("Stage 5: Hierarchy-Aware Imputation", "Mode imputation for missing customer regions and segments."),
            ("Stage 6: Automated Validation Gates", "12 automated test gates (11 Passed, 1 Info, 0 Failed).")
        ]
        py = col_y + col_h - 75
        for s_title, s_desc in stages_info:
            c.setFillColor(HexColor('#EFF6FF'))
            c.setStrokeColor(HexColor('#BFDBFE'))
            c.roundRect(353, py - 36, col_w - 20, 44, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#1E3A8A'))
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(361, py - 2, s_title)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.5)
            c.drawString(361, py - 18, s_desc[:44])
            c.drawString(361, py - 30, s_desc[44:])
            py -= 50

        # Card 3: Analytical & Statistical Methods
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(661, col_y + col_h - 30, "Analytical Methods & Models")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(661, col_y + col_h - 46, "Rigorous mathematical framework:")

        methods = [
            ("Volume-Weighted KPI Engine", "Avoided simple average margin distortion by weighting all margin calculations strictly by transaction revenue ($)."),
            ("Statistical Hypothesis Testing", "Executed two-sample Welch's t-tests (unequal variances) on discount margins, marketplace fee drag, and delivery returns."),
            ("Customer Retention Tracking", "Tracked annual customer cohort return behavior (54.4% -> 49.7%) to measure loyalty erosion."),
            ("Dynamic 36-Month Cash Flow Model", "Monthly cash flow engine incorporating implementation launch timing, ramp-up schedules, Capex/Opex, and 10% WACC discounting.")
        ]
        my = col_y + col_h - 75
        for m_title, m_desc in methods:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(656, my - 58, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#059669'))
            c.setFont('Helvetica-Bold', 8.8)
            c.drawString(664, my - 2, m_title)
            c.setFillColor(HexColor('#334155'))
            c.setFont('Helvetica', 7.8)
            words = m_desc.split()
            c.drawString(664, my - 16, " ".join(words[:8]))
            c.drawString(664, my - 29, " ".join(words[8:16]))
            c.drawString(664, my - 42, " ".join(words[16:]))
            my -= 76

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 5: Data Quality & Financial Reconciliation
        # -------------------------------------------------------------
        draw_slide_base("Data Quality & Audit",
                        "Data Quality & Financial Reconciliation Waterfall",
                        "Unadjusted raw data overstates revenue by $738.8k (+21.9%) and profit by $194.6k (+42.5%). Audited metrics prevent flawed capital decisions.", 5)

        # Left: Chart 1
        c.drawImage(self.chart_paths['waterfall'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Reconciliation Table & Findings
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Raw-to-Clean Financial Reconciliation")

        # Table Header
        ty = 395
        c.setFillColor(HexColor('#0F2942'))
        c.roundRect(505, ty, 405, 20, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(512, ty + 6, "Reconciliation Stage")
        c.drawRightString(665, ty + 6, "Revenue ($)")
        c.drawRightString(745, ty + 6, "Profit ($)")
        c.drawRightString(820, ty + 6, "Margin %")
        c.drawRightString(900, ty + 6, "Delta ($)")

        table_rows = [
            ("1. Raw Sales Data (All Records)", "$4,112,442", "$652,661", "15.87%", "Baseline", False),
            ("2. Exact Duplicates Removed (400)", "-$185,341", "-$36,702", "19.80%", "-$185.3k", False),
            ("3. Dropped Unrecoverable (4 rows)", "-$1,124", "-$289", "25.71%", "-$1.1k", False),
            ("4. Quantity Outliers Corrected (28)", "-$552,349", "-$157,612", "28.53%", "-$552.3k", False),
            ("5. Final Clean Dataset (11,996)", "$3,373,628", "$458,058", "13.58%", "-$738.8k", True),
            ("   - Year 2023 (3,079 orders)", "$896,588", "$138,398", "15.44%", "--", False),
            ("   - Year 2024 (3,939 orders)", "$1,076,644", "$152,572", "14.17%", "--", False),
            ("   - Year 2025 (4,978 orders)", "$1,400,397", "$167,088", "11.93%", "--", False),
        ]
        row_y = ty - 20
        for stage, rev, prof, mrg, delta, is_bold in table_rows:
            bg_col = '#F1F5F9' if is_bold else '#FFFFFF'
            c.setFillColor(HexColor(bg_col))
            c.rect(505, row_y - 2, 405, 18, fill=1, stroke=0)
            c.setFillColor(HexColor('#0F172A' if is_bold else '#334155'))
            c.setFont('Helvetica-Bold' if is_bold else 'Helvetica', 7.5)
            c.drawString(512, row_y + 3, stage)
            c.drawRightString(665, row_y + 3, rev)
            c.drawRightString(745, row_y + 3, prof)
            c.drawRightString(820, row_y + 3, mrg)
            c.drawRightString(900, row_y + 3, delta)
            row_y -= 19

        # Unresolved Exceptions Box
        c.setFillColor(HexColor('#EFF6FF'))
        c.setStrokeColor(HexColor('#BFDBFE'))
        c.roundRect(505, 55, 405, 140, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(515, 180, "AUDIT LOG: UNRESOLVED EDGE CASES & CAVEATS")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        caveat_lines = [
            "• Profit Rounding Deviations (607 records): Low severity (<$0.05). Caused by",
            "  floating-point rounding on discounted prices. Immaterial to decision model.",
            "• High-Value Sale Outliers (407 records): Legitimate B2B bulk orders (>IQR fence).",
            "  Retained after verifying authentic business customer IDs and valid unit costs.",
            "• Dropped Missing Rows (4 records): Dropped because both price and quantity were",
            "  missing simultaneously, making mathematical reconstruction impossible.",
            "• Commercial Impact: Decisions based on uncleaned data would misallocate capital",
            "  by assuming $194.6k in non-existent contribution profit."
        ]
        ey = 164
        for eline in caveat_lines:
            c.drawString(515, ey, eline)
            ey -= 13

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 6: Revenue and Growth Trends
        # -------------------------------------------------------------
        draw_slide_base("Top-Line Performance",
                        "Revenue & Order Volume Trajectory (2023–2025)",
                        "Annual sales climbed from $896.6k to $1.40M (+56.2%) driven by order volume expansion (+61.7%), while AOV held steady at ~$281.", 6)

        # Left: Chart 2
        c.drawImage(self.chart_paths['revenue_orders'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Findings Card
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Growth Dynamics & Volume Expansion")

        # Annual KPI Table
        ty = 395
        c.setFillColor(HexColor('#0F2942'))
        c.roundRect(505, ty, 405, 20, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(512, ty + 6, "Metric")
        c.drawRightString(630, ty + 6, "2023")
        c.drawRightString(720, ty + 6, "2024")
        c.drawRightString(810, ty + 6, "2025")
        c.drawRightString(900, ty + 6, "3-Yr Growth")

        kpi_rows = [
            ("Revenue ($)", "$896,588", "$1,076,644", "$1,400,397", "+56.2%"),
            ("Order Count", "3,079", "3,939", "4,978", "+61.7%"),
            ("Unique Customers", "524", "1,003", "1,376", "+162.6%"),
            ("Average Order Value (AOV)", "$291.19", "$273.33", "$281.32", "-3.4%"),
            ("Repeat Customer Share", "93.8%", "94.9%", "95.5%", "+1.7 pp"),
            ("Top 20% Customer Rev Share", "64.2%", "65.8%", "66.1%", "+1.9 pp"),
        ]
        row_y = ty - 20
        for metric, y1, y2, y3, grw in kpi_rows:
            c.setFillColor(HexColor('#FFFFFF'))
            c.rect(505, row_y - 2, 405, 18, fill=1, stroke=0)
            c.setFillColor(HexColor('#334155'))
            c.setFont('Helvetica', 7.5)
            c.drawString(512, row_y + 3, metric)
            c.drawRightString(630, row_y + 3, y1)
            c.drawRightString(720, row_y + 3, y2)
            c.drawRightString(810, row_y + 3, y3)
            c.setFillColor(HexColor('#059669'))
            c.setFont('Helvetica-Bold', 7.5)
            c.drawRightString(900, row_y + 3, grw)
            row_y -= 19

        # Executive Takeaway Card
        c.setFillColor(HexColor('#F8FAFC'))
        c.setStrokeColor(HexColor('#CBD5E1'))
        c.roundRect(505, 55, 405, 180, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#0F172A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 218, "STRATEGIC TAKEAWAYS ON TOP-LINE EXPANSION:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 8)
        takeaways = [
            "1. Volume-Driven Scale: Top-line expansion (+56.2%) has been propelled by rapid",
            "   transaction volume (+61.7%) rather than pricing power or basket inflation.",
            "2. Customer Base Tripling: Unique active customers expanded from 524 to 1,376.",
            "   However, customer acquisition was subsidized by promotional price cutting.",
            "3. High Customer Concentration: The top 20% of buyers generate 66.1% of total",
            "   revenue ($2.23M). Safeguarding these key relationships is paramount.",
            "4. The Operational Risk: Massive order volume has strained warehouse fulfillment",
            "   and shipping SLAs, planting the seeds for margin compression."
        ]
        toy = 200
        for tline in takeaways:
            c.drawString(515, toy, tline)
            toy -= 14

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 7: Profitability Diagnosis
        # -------------------------------------------------------------
        draw_slide_base("Margin Diagnosis",
                        "Profitability Diagnosis: The Growth vs. Margin Decoupling",
                        "While annual revenue grew +56.2%, dollar profit grew only +20.7%, resulting in a net -3.51 percentage point collapse in contribution margin.", 7)

        # Left: Chart 3
        c.drawImage(self.chart_paths['margin_decay'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Category Table & Margin Analysis
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Product Category Margin Asymmetry")

        # Category Table
        ty = 395
        c.setFillColor(HexColor('#0F2942'))
        c.roundRect(505, ty, 405, 20, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(512, ty + 6, "Product Category")
        c.drawRightString(640, ty + 6, "Revenue ($)")
        c.drawRightString(730, ty + 6, "Profit ($)")
        c.drawRightString(815, ty + 6, "Margin %")
        c.drawRightString(900, ty + 6, "Rev Share %")

        cat_rows = [
            ("Office Supplies", "$432,492", "$152,229", "35.20%", "12.82%", '#059669'),
            ("Furniture", "$1,293,350", "$157,456", "12.17%", "38.34%", '#D97706'),
            ("Technology", "$1,647,786", "$148,373", "9.00%", "48.84%", '#DC2626'),
            ("Total Portfolio", "$3,373,628", "$458,058", "13.58%", "100.0%", '#1E293B'),
        ]
        row_y = ty - 22
        for cat, rev, prof, mrg, rsh, colr in cat_rows:
            is_tot = (cat == "Total Portfolio")
            bg_col = '#F1F5F9' if is_tot else '#FFFFFF'
            c.setFillColor(HexColor(bg_col))
            c.rect(505, row_y - 2, 405, 20, fill=1, stroke=0)
            c.setFillColor(HexColor(colr))
            c.setFont('Helvetica-Bold' if is_tot else 'Helvetica', 8)
            c.drawString(512, row_y + 4, cat)
            c.drawRightString(640, row_y + 4, rev)
            c.drawRightString(730, row_y + 4, prof)
            c.drawRightString(815, row_y + 4, mrg)
            c.drawRightString(900, row_y + 4, rsh)
            row_y -= 22

        # Detailed Diagnostic Callout
        c.setFillColor(HexColor('#FEF2F2'))
        c.setStrokeColor(HexColor('#FECACA'))
        c.roundRect(505, 55, 405, 205, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#991B1B'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 242, "DIAGNOSTIC FINDINGS: DEEP MARGIN SUBSIDIZATION")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 8)
        diag_lines = [
            "1. Office Supplies Is the Profit Anchor: Earns 33.2% of total company profit",
            "   ($152.2k) on just 12.8% of revenue. Achieves stellar 35.2% contribution margin.",
            "2. Technology Margin Dilution: Generates nearly half of all sales ($1.65M, 48.8%),",
            "   but yields an anemic 9.0% margin. Heavy discounting and high vendor costs",
            "   severely erode profitability.",
            "3. Furniture Heavy Freight Burden: $1.29M in revenue (38.3%) delivers only 12.2%",
            "   margin due to heavy shipping weight and high marketplace commission fees.",
            "4. Core Executive Takeaway: Growth has been concentrated in low-margin categories",
            "   (Technology & Furniture) while the high-margin anchor (Office Supplies) was",
            "   under-promoted. Restoring margin requires portfolio re-balancing."
        ]
        dy = 224
        for dline in diag_lines:
            c.drawString(515, dy, dline)
            dy -= 14

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 8: Discount Economics & The Pricing Cliff
        # -------------------------------------------------------------
        draw_slide_base("Pricing Economics",
                        "Discount Economics: The 20% Discount Loss Cliff",
                        "Discounts above 20% destroy unit profitability: 1,605 orders generated -$40,094 in direct losses. Blunt cancellations risk customer contagion.", 8)

        # Left: Chart 4
        c.drawImage(self.chart_paths['discount_cliff'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Contagion Risk Card
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Discount Bands & The Contagion Risk")

        # Discount Table
        ty = 395
        c.setFillColor(HexColor('#0F2942'))
        c.roundRect(505, ty, 405, 20, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(512, ty + 6, "Discount Band")
        c.drawRightString(635, ty + 6, "Orders")
        c.drawRightString(725, ty + 6, "Profit ($)")
        c.drawRightString(815, ty + 6, "Margin %")
        c.drawRightString(900, ty + 6, "Loss Orders")

        disc_rows = [
            ("0% Full Price", "3,229", "+$290,054", "28.74%", "4 (0.1%)"),
            ("1–10% Discount", "2,325", "+$152,956", "22.37%", "19 (0.8%)"),
            ("11–20% Discount", "2,931", "+$97,177", "11.79%", "215 (7.3%)"),
            ("21–30% Discount", "1,950", "-$2,852", "-0.56%", "487 (25.0%)"),
            (">30% Deep Discount", "1,561", "-$79,277", "-22.55%", "854 (54.7%)"),
        ]
        row_y = ty - 19
        for band, ords, prof, mrg, loss in disc_rows:
            is_neg = "-" in prof
            c.setFillColor(HexColor('#FFFFFF'))
            c.rect(505, row_y - 2, 405, 17, fill=1, stroke=0)
            c.setFillColor(HexColor('#DC2626' if is_neg else '#334155'))
            c.setFont('Helvetica-Bold' if is_neg else 'Helvetica', 7.5)
            c.drawString(512, row_y + 3, band)
            c.drawRightString(635, row_y + 3, ords)
            c.drawRightString(725, row_y + 3, prof)
            c.drawRightString(815, row_y + 3, mrg)
            c.drawRightString(900, row_y + 3, loss)
            row_y -= 18

        # Contagion Risk Warning Box
        c.setFillColor(HexColor('#FFFBEB'))
        c.setStrokeColor(HexColor('#FDE68A'))
        c.roundRect(505, 55, 405, 205, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#92400E'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 242, "CRITICAL RISK: THE CUSTOMER CONTAGION DILEMMA")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        contagion_lines = [
            "• The Baseline Problem: In 2025 alone, 1,605 orders with >20% discount generated",
            "  -$40,094 in direct losses. Cutting these orders would appear to save $40k.",
            "• The Hidden Trap (Customer Contagion): These 1,605 loss-making orders were",
            "  placed by 825 unique customers who ALSO placed profitable orders (<=20% discount)",
            "  generating $741,419 in revenue and $152,140 in contribution profit!",
            "• The 26.3% Churn Breakeven: If bluntly canceling discounted orders causes more",
            "  than 26.3% of these customers to leave entirely, the company loses more profit",
            "  from their good orders than it saves from stopping the loss orders.",
            "• Governance Solution: Implement basket-level minimum margin rules (15%) and",
            "  discretionary VP escalation workflows rather than blunt order cancellations."
        ]
        cy = 224
        for cline in contagion_lines:
            c.drawString(515, cy, cline)
            cy -= 13

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 9: Channel and Regional Performance
        # -------------------------------------------------------------
        draw_slide_base("Channel & Regional Mix",
                        "Channel Economics & Regional Operational Bottlenecks",
                        "Marketplace revenue share expanded to 26% while losing -2.55% on every dollar sold. Central region logistics suffer a 58.4% late delivery rate.", 9)

        # Left: Chart 5
        c.drawImage(self.chart_paths['channel_region'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Analysis Card
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Channel Cannibalization & Regional Logistics")

        # Regional Table
        ty = 395
        c.setFillColor(HexColor('#0F2942'))
        c.roundRect(505, ty, 405, 20, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(512, ty + 6, "Region")
        c.drawRightString(630, ty + 6, "Orders")
        c.drawRightString(720, ty + 6, "Revenue ($)")
        c.drawRightString(810, ty + 6, "Late Orders")
        c.drawRightString(900, ty + 6, "Late Rate %")

        reg_rows = [
            ("West Region", "3,818", "$1,083,664", "453", "11.86%"),
            ("North Region", "3,132", "$838,042", "585", "18.68%"),
            ("South Region", "2,163", "$617,348", "554", "25.61%"),
            ("East Region", "1,902", "$536,192", "565", "29.71%"),
            ("Central Region", "981", "$298,382", "573", "58.41%"),
        ]
        row_y = ty - 19
        for reg, ords, rev, late, lrate in reg_rows:
            is_central = ("Central" in reg)
            c.setFillColor(HexColor('#FEF2F2' if is_central else '#FFFFFF'))
            c.rect(505, row_y - 2, 405, 17, fill=1, stroke=0)
            c.setFillColor(HexColor('#DC2626' if is_central else '#334155'))
            c.setFont('Helvetica-Bold' if is_central else 'Helvetica', 7.5)
            c.drawString(512, row_y + 3, reg)
            c.drawRightString(630, row_y + 3, ords)
            c.drawRightString(720, row_y + 3, rev)
            c.drawRightString(810, row_y + 3, late)
            c.drawRightString(900, row_y + 3, lrate)
            row_y -= 18

        # Detailed Diagnostic Callout
        c.setFillColor(HexColor('#F8FAFC'))
        c.setStrokeColor(HexColor('#CBD5E1'))
        c.roundRect(505, 55, 405, 205, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#0F172A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 242, "OPERATIONAL BOTTLENECK ANALYSIS:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        ch_lines = [
            "1. Marketplace Margin Drag (Hypothesis H2 Confirmed):",
            "   • Marketplace sales grew from 12.3% of mix (2023) to 26.2% (2025).",
            "   • Incurred -$17,437 in cumulative losses across 2,660 orders (-2.55% margin).",
            "   • The 13%–15% take-rate wipes out gross margins when combined with seller discounts.",
            "2. Central Regional Shipping Failure:",
            "   • Central region delivered 573 out of 981 orders late (58.41% late delivery rate).",
            "   • Carrier contract lacks performance SLA penalties; packages sit in regional hubs.",
            "3. Channel Cannibalization Risk:",
            "   • Customers who previously bought on Direct Store (21.2% margin) or Online (15.0%)",
            "     have migrated to Marketplace (-2.5%), cannibalizing high-margin profits."
        ]
        cy = 224
        for cline in ch_lines:
            c.drawString(515, cy, cline)
            cy -= 13

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 10: Customer, Delivery, and Returns
        # -------------------------------------------------------------
        draw_slide_base("Fulfillment & Retention",
                        "Delivery Timeliness, Return Rates & Retention Erosion",
                        "Late deliveries suffer a 14.9% return rate (3.1x on-time rate). Annual customer retention dropped from 54.4% to 49.7% (-4.7 pp).", 10)

        # Left: Chart 6
        c.drawImage(self.chart_paths['returns_retention'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Findings Card
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Statistical Evidence & Observational Caveats")

        # Hypothesis 3 Test Summary
        c.setFillColor(HexColor('#EFF6FF'))
        c.setStrokeColor(HexColor('#BFDBFE'))
        c.roundRect(505, 295, 405, 115, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 395, "HYPOTHESIS 3: SHIPPING DELAYS DRIVE MERCHANDISE RETURNS")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 8)
        h3_lines = [
            "• On-Time Deliveries (<=5 Days): 4.78% return rate across 9,266 shipments.",
            "• Late Deliveries (>5 Days): 14.91% return rate across 2,730 shipments (3.1x higher).",
            "• Welch's Two-Sample t-test: t = +14.13, p = 4.80e-44 (Statistically Significant).",
            "• Verdict: SUPPORTED. Delayed transit strongly associates with customer rejection.",
            "• Annual Financial Cost: $1,911.00 in avoidable return reverse logistics & restocking."
        ]
        hy = 378
        for hline in h3_lines:
            c.drawString(515, hy, hline)
            hy -= 14

        # Retention & Scientific Disclosure Box
        c.setFillColor(HexColor('#FFFBEB'))
        c.setStrokeColor(HexColor('#FDE68A'))
        c.roundRect(505, 55, 405, 230, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#92400E'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 268, "CUSTOMER RETENTION DYNAMICS & SCIENTIFIC CAVEATS")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        ret_lines = [
            "1. Retention Decay Across Cohorts:",
            "   • Active customer retention dropped from 54.39% (2023->2024) to 49.65% (2024->2025).",
            "   • Loss of repeat buyers is critical: 95.0% of all company orders originate from",
            "     repeat customers, generating 66.1% of total top-line revenue.",
            "2. Scientific Observational Disclosure:",
            "   • Association is not causation. While late delivery strongly correlates with returns,",
            "     return rates are also influenced by product complexity, apparel sizing, and buyer",
            "     remorse. Improving delivery speed mitigates but does not eliminate returns.",
            "3. Operational Opportunity:",
            "   • Recovering Central region delivery performance (<15% late) prevents customer",
            "     frustration, recapturing 4.5 percentage points of lost cohort retention.",
            "   • Base model captures +$5,402.52/yr in retained customer gross profit."
        ]
        ry = 250
        for rline in ret_lines:
            c.drawString(515, ry, rline)
            ry -= 13

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 11: Recommendation 1 — Discount Guardrails
        # -------------------------------------------------------------
        draw_slide_base("Recommendation 1",
                        "Recommendation 1: Automated Discount Guardrails",
                        "Cap standard checkout discounts at 20% and enforce a 15% minimum basket margin. Uplift: +$66,332/yr | Payback: Month 3.", 11)

        col_w = 274
        col_h = 410
        col_y = 42

        # Card 1: Core Action & Governance
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, col_y + col_h - 30, "Policy & System Controls")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(55, col_y + col_h - 46, "Automated checkout price architecture:")

        rec1_pillars = [
            ("20% Hard Ceiling at Checkout", "Configure e-commerce checkout and ERP order entry to reject single-item discounts exceeding 20%."),
            ("15% Basket Margin Floor", "Enforce total order contribution margin check. If basket margin falls below 15%, checkout flags exception."),
            ("Tiered Approval Workflow", "Discounts 15%–20% require Sales Director sign-off; discounts >20% require Regional VP approval."),
            ("Daily Margin Exception Audit", "Automated daily alert to CFO detailing all overridden orders and rep compliance rates.")
        ]
        ry = col_y + col_h - 75
        for ptitle, pdesc in rec1_pillars:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(50, ry - 55, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#0F172A'))
            c.setFont('Helvetica-Bold', 9)
            c.drawString(58, ry + 2, ptitle)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.8)
            words = pdesc.split()
            c.drawString(58, ry - 14, " ".join(words[:8]))
            c.drawString(58, ry - 27, " ".join(words[8:16]))
            c.drawString(58, ry - 40, " ".join(words[16:]))
            ry -= 76

        # Card 2: Audited Financial Case
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(358, col_y + col_h - 30, "Audited Financial Business Case")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(358, col_y + col_h - 46, "Base-Case 36-Month Model:")

        r1_metrics = [
            ("Annual Steady-State Profit Uplift", "+$66,331.86/yr", "#059669"),
            ("Annual Revenue Recovery Delta", "+$58,959.97/yr", "#2563EB"),
            ("Implementation Capex (One-Time)", "$10,000.00", "#1E293B"),
            ("Annual Recurring Opex", "$3,999.96/yr", "#1E293B"),
            ("36-Month Total Investment", "$21,999.88", "#1E293B"),
            ("36-Month Net Cash Benefit", "+$171,468.04", "#059669"),
            ("Net Return on Investment (ROI)", "779.40%", "#059669"),
            ("Breakeven Payback Timeline", "Month 3 (Rapid)", "#2563EB"),
        ]
        my = col_y + col_h - 75
        for lbl, val, colr in r1_metrics:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(353, my - 24, col_w - 20, 32, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7.5)
            c.drawString(361, my - 3, lbl)
            c.setFillColor(HexColor(colr))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(361, my - 18, val)
            my -= 38

        # Card 3: Execution & Contagion Mitigation
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(661, col_y + col_h - 30, "Implementation & Contagion Control")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(661, col_y + col_h - 46, "Safeguarding key customer accounts:")

        c.setFillColor(HexColor('#FEF2F2'))
        c.setStrokeColor(HexColor('#FECACA'))
        c.roundRect(656, col_y + col_h - 185, col_w - 20, 130, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#991B1B'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(664, col_y + col_h - 72, "PREVENTING CUSTOMER CHURN CONTAGION:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        mit_lines = [
            "• Threat: 825 buyers of >20% discounted goods",
            "  also deliver $741k in profitable purchases.",
            "• Action: Transition large buyers from transactional",
            "  discounts to structured annual volume rebates.",
            "• Account Management: Key account reps receive",
            "  margin quota bonuses rather than top-line",
            "  revenue commission to align incentives."
        ]
        myy = col_y + col_h - 90
        for mline in mit_lines:
            c.drawString(664, myy, mline)
            myy -= 13

        # Roadmap bullets
        c.setFillColor(HexColor('#EFF6FF'))
        c.setStrokeColor(HexColor('#BFDBFE'))
        c.roundRect(656, col_y + 15, col_w - 20, 195, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(664, col_y + 195, "QUICK-WIN IMPLEMENTATION PLAN:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        rplan = [
            "• Month 1: ERP pricing logic configuration &",
            "  staging environment integration testing ($5k).",
            "• Month 2: Sales rep enablement & compensation",
            "  plan realignment to contribution profit ($5k).",
            "• Month 3: Go-live on direct online & retail stores.",
            "  Cash payback achieved within 90 days.",
            "• Owner: VP Sales & Chief Commercial Officer.",
            "• KPI: % orders >20% discount (Target: <3.0%)."
        ]
        rpy = col_y + 178
        for rline in rplan:
            c.drawString(664, rpy, rline)
            rpy -= 14

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 12: Recommendation 2 — Marketplace Margin Repair
        # -------------------------------------------------------------
        draw_slide_base("Recommendation 2",
                        "Recommendation 2: Marketplace Margin Repair",
                        "Renegotiate platform fees by 1.0 pp, impose a 10% channel discount cap, and prune unprofitable SKUs. Uplift: +$29,352/yr | Payback: Month 12.", 12)

        col_w = 274
        col_h = 410
        col_y = 42

        # Card 1: Three Pillars
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, col_y + col_h - 30, "Three-Pillar Turnaround")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(55, col_y + col_h - 46, "Restoring marketplace unit economics:")

        mp_pillars = [
            ("Pillar 1: 1.0 pp Fee Cut (15% -> 14%)", "Leverage annual platform volume ($684k) to negotiate a 1.0 percentage point reduction in marketplace take-rate."),
            ("Pillar 2: 10% Channel Discount Cap", "Impose a strict 10% maximum promotional ceiling on all third-party listings to absorb platform fee drag."),
            ("Pillar 3: Unprofitable SKU Pruning", "Delist bulky Furniture & low-margin Tech accessories with gross margins below 25% from marketplace channels."),
            ("Pillar 4: Direct Channel Redirection", "Insert branded product registration cards into marketplace shipments offering $10 off first direct web store order.")
        ]
        my = col_y + col_h - 75
        for ptitle, pdesc in mp_pillars:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(50, my - 55, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#0F172A'))
            c.setFont('Helvetica-Bold', 9)
            c.drawString(58, my + 2, ptitle)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.8)
            words = pdesc.split()
            c.drawString(58, my - 14, " ".join(words[:8]))
            c.drawString(58, my - 27, " ".join(words[8:16]))
            c.drawString(58, my - 40, " ".join(words[16:]))
            my -= 76

        # Card 2: Financial Case
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(358, col_y + col_h - 30, "Audited Financial Business Case")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(358, col_y + col_h - 46, "Base-Case 36-Month Model:")

        r2_metrics = [
            ("Annual Steady-State Profit Uplift", "+$29,352.04/yr", "#059669"),
            ("Annual Revenue Recovery Delta", "+$20,869.23/yr", "#2563EB"),
            ("Implementation Capex (One-Time)", "$12,000.00", "#1E293B"),
            ("Annual Recurring Opex", "$6,000.00/yr", "#1E293B"),
            ("36-Month Total Investment", "$29,000.00", "#1E293B"),
            ("36-Month Net Cash Benefit", "+$48,049.10", "#059669"),
            ("Net Return on Investment (ROI)", "165.69%", "#059669"),
            ("Breakeven Payback Timeline", "Month 12", "#2563EB"),
        ]
        my = col_y + col_h - 75
        for lbl, val, colr in r2_metrics:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(353, my - 24, col_w - 20, 32, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7.5)
            c.drawString(361, my - 3, lbl)
            c.setFillColor(HexColor(colr))
            c.setFont('Helvetica-Bold', 10)
            c.drawString(361, my - 18, val)
            my -= 38

        # Card 3: Execution Governance & Risk
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(661, col_y + col_h - 30, "Execution Governance & Risks")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(661, col_y + col_h - 46, "Contract negotiation and listing governance:")

        c.setFillColor(HexColor('#EFF6FF'))
        c.setStrokeColor(HexColor('#BFDBFE'))
        c.roundRect(656, col_y + col_h - 185, col_w - 20, 130, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(664, col_y + col_h - 72, "NEGOTIATION STRATEGY & LEVERAGE:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        neg_lines = [
            "• Leverage Seller Rank: Position company as top-tier",
            "  merchant delivering $684k in gross platform sales.",
            "• Advertising Commitment: Reallocate 0.5% of saved",
            "  fees into marketplace sponsored brand ads.",
            "• Fallback Plan: If platform refuses fee concession,",
            "  prune catalog to high-margin SKUs only; sensitivity",
            "  shows +$189k net benefit even at 0.0 pp fee cut."
        ]
        nyy = col_y + col_h - 90
        for nline in neg_lines:
            c.drawString(664, nyy, nline)
            nyy -= 13

        # Timeline
        c.setFillColor(HexColor('#F8FAFC'))
        c.setStrokeColor(HexColor('#E2E8F0'))
        c.roundRect(656, col_y + 15, col_w - 20, 195, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#0F172A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(664, col_y + 195, "ROLLOUT TIMELINE & OWNERSHIP:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        mplan = [
            "• Month 4: Initiate platform contract negotiations;",
            "  audit catalog unit contribution margins.",
            "• Month 5: Deploy channel management software ($12k);",
            "  enforce 10% maximum promotional ceiling.",
            "• Month 6: Delist 45 negative-margin SKUs.",
            "• Month 12: Breakeven reached; steady-state +$29k/yr.",
            "• Owner: VP E-Commerce & Marketplace Operations.",
            "• Target KPI: Marketplace margin > +4.0% (from -2.55%)."
        ]
        mpy = col_y + 178
        for mline in mplan:
            c.drawString(664, mpy, mline)
            mpy -= 14

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 13: Recommendation 3 — Delivery SLA and Retention
        # -------------------------------------------------------------
        draw_slide_base("Recommendation 3",
                        "Recommendation 3: Delivery SLA & Customer Retention Overhaul",
                        "Overhaul Central region 3PL logistics to reduce late deliveries from 58% to 15%. Standalone deficit: -$18.8k; strategic brand investment.", 13)

        col_w = 274
        col_h = 410
        col_y = 42

        # Card 1: Logistics Overhaul
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, col_y + col_h - 30, "Logistics & Carrier Plan")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(55, col_y + col_h - 46, "Central fulfillment recovery program:")

        sla_pillars = [
            ("Central Carrier Re-Contracting", "Terminate exclusive single-carrier 3PL contract in Central region; onboard secondary regional freight partner."),
            ("Strict SLA Penalty Enforcement", "Establish contractual delivery guarantees: 95% on-time threshold with freight credit rebates on late shipments."),
            ("Fulfillment Hub Re-Routing", "Re-route Central order volume through Dallas and Chicago distribution hubs, cutting transit time by 2.2 days."),
            ("Proactive Recovery Outreach", "Deploy automated SMS notifications and immediate $15 customer credits when shipping delays exceed 48 hours.")
        ]
        sy = col_y + col_h - 75
        for ptitle, pdesc in sla_pillars:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(50, sy - 55, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#0F172A'))
            c.setFont('Helvetica-Bold', 9)
            c.drawString(58, sy + 2, ptitle)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.8)
            words = pdesc.split()
            c.drawString(58, sy - 14, " ".join(words[:8]))
            c.drawString(58, sy - 27, " ".join(words[8:16]))
            c.drawString(58, sy - 40, " ".join(words[16:]))
            sy -= 76

        # Card 2: Audited Financials & Deficit Disclosure
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(358, col_y + col_h - 30, "Financials & Standalone Deficit")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(358, col_y + col_h - 46, "Transparent disclosure of standalone economics:")

        r3_metrics = [
            ("Annual Return Cost Reduction", "+$1,911.00/yr", "#059669"),
            ("Annual Customer Retention Profit", "+$5,402.52/yr", "#059669"),
            ("Total Annual Benefit Run-Rate", "+$7,313.52/yr", "#059669"),
            ("Annual Recurring Opex", "$9,000.00/yr", "#DC2626"),
            ("Net Annual Run-Rate Delta", "-$1,686.48/yr (Deficit)", "#DC2626"),
            ("Implementation Capex (One-Time)", "$12,000.00", "#1E293B"),
            ("36-Month Total Investment", "$35,250.00", "#1E293B"),
            ("36-Month Net Cash Benefit", "-$18,794.58 (Deficit)", "#DC2626"),
            ("Net Return on Investment (ROI)", "-53.32%", "#DC2626"),
            ("Standalone Payback Timeline", "Never (>36 Months)", "#DC2626"),
        ]
        my = col_y + col_h - 68
        for lbl, val, colr in r3_metrics:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(353, my - 20, col_w - 20, 26, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7.2)
            c.drawString(361, my - 3, lbl)
            c.setFillColor(HexColor(colr))
            c.setFont('Helvetica-Bold', 8.5)
            c.drawRightString(353 + col_w - 28, my - 15, val)
            my -= 31

        # Card 3: Strategic Justification & Options
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(661, col_y + col_h - 30, "Strategic Justification & Decisions")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(661, col_y + col_h - 46, "Leadership options for Recommendation 3:")

        c.setFillColor(HexColor('#FEF2F2'))
        c.setStrokeColor(HexColor('#FECACA'))
        c.roundRect(656, col_y + col_h - 175, col_w - 20, 120, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#991B1B'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(664, col_y + col_h - 70, "WHY OPEX EXCEEDS DIRECT BENEFIT:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        why_lines = [
            "• Logistics opex ($750/mo = $9k/yr) covers enterprise",
            "  carrier integration software and dedicated SLA audits.",
            "• Direct benefits ($7.3k/yr) only capture return freight",
            "  and modest modeled repeat retention (+4.5 pp).",
            "• Break-even requires each retained buyer to spend",
            "  $1,438/yr (above historical repeat average $1,292)."
        ]
        wyy = col_y + col_h - 86
        for wline in why_lines:
            c.drawString(664, wyy, wline)
            wyy -= 13

        # Executive Decision Options
        c.setFillColor(HexColor('#EFF6FF'))
        c.setStrokeColor(HexColor('#BFDBFE'))
        c.roundRect(656, col_y + 15, col_w - 20, 205, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(664, col_y + 205, "THREE EXECUTIVE DECISION OPTIONS:")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        doptions = [
            "Option A: Cost Redesign (Target Breakeven)",
            "• Re-scope carrier software integrations to compress",
            "  annual opex from $9.0k to $5.0k/yr, reaching breakeven.",
            "",
            "Option B: 6-Month Pilot Validation",
            "• Run pilot in Central region to validate if retention lift",
            "  exceeds modeled +4.5 pp before full system rollout.",
            "",
            "Option C: Strategic Brand Approval (Recommended)",
            "• Approve as a necessary brand & SLA investment.",
            "• Funded by massive cash surplus from Rec 1 ($171k) &",
            "  Rec 2 ($48k). Combined portfolio nets +$200.7k cash."
        ]
        doy = col_y + 190
        for dline in doptions:
            c.drawString(664, doy, dline)
            doy -= 12.5

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 14: Financial Business Case & Scenario Analysis
        # -------------------------------------------------------------
        draw_slide_base("Portfolio Financial Model",
                        "Financial Business Case: Multi-Scenario ROI & Sensitivity",
                        "Audited 36-month portfolio delivers $200,723 net cash benefit (232.7% ROI, Month 8 payback). Positive across all sensitivity stress tests.", 14)

        # Left: Chart 7
        c.drawImage(self.chart_paths['cash_flow'], 40, 50, width=440, height=395, preserveAspectRatio=True)

        # Right: Reconciled Table & Sensitivity Summary
        draw_card(495, 45, 425, 405)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(510, 425, "Audited Financial Scenarios & Sensitivity")

        # Scenario Table
        ty = 395
        c.setFillColor(HexColor('#0F2942'))
        c.roundRect(505, ty, 405, 20, 3, fill=1, stroke=0)
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont('Helvetica-Bold', 8)
        c.drawString(512, ty + 6, "Financial Metric")
        c.drawRightString(635, ty + 6, "Conservative")
        c.drawRightString(725, ty + 6, "Base (Rec.)")
        c.drawRightString(815, ty + 6, "Optimistic")
        c.drawRightString(900, ty + 6, "Variance")

        scen_rows = [
            ("Annual Steady-State Uplift", "$82,454/yr", "$102,997/yr", "$121,792/yr", "+/-20%"),
            ("One-Time Capex", "$40,800", "$34,000", "$30,600", "-10% to +20%"),
            ("Annual Recurring Opex", "$22,800/yr", "$19,000/yr", "$17,100/yr", "-10% to +20%"),
            ("36-Month Total Cost", "$99,700", "$86,250", "$77,625", "--"),
            ("36-Month Net Cash Benefit", "$119,555", "$200,723", "$256,068", "+$81k spread"),
            ("Net Return on Investment (ROI)", "119.91%", "232.72%", "329.88%", "+112.8 pp"),
            ("Discounted NPV (@ 10% WACC)", "$97,798", "$168,399", "$215,709", "+$70.6k spread"),
            ("Combined Portfolio Payback", "Month 12", "Month 8", "Month 5", "-3 to +4 mos"),
        ]
        row_y = ty - 19
        for metric, cons, base, opt, var in scen_rows:
            is_net = ("Net Cash Benefit" in metric or "ROI" in metric)
            bg_col = '#F1F5F9' if is_net else '#FFFFFF'
            c.setFillColor(HexColor(bg_col))
            c.rect(505, row_y - 2, 405, 17, fill=1, stroke=0)
            c.setFillColor(HexColor('#059669' if is_net else '#1E293B'))
            c.setFont('Helvetica-Bold' if is_net else 'Helvetica', 7.5)
            c.drawString(512, row_y + 3, metric)
            c.drawRightString(635, row_y + 3, cons)
            c.drawRightString(725, row_y + 3, base)
            c.drawRightString(815, row_y + 3, opt)
            c.setFillColor(HexColor('#64748B'))
            c.setFont('Helvetica', 7)
            c.drawRightString(900, row_y + 3, var)
            row_y -= 18

        # Sensitivity Matrix Box
        c.setFillColor(HexColor('#F8FAFC'))
        c.setStrokeColor(HexColor('#CBD5E1'))
        c.roundRect(505, 55, 405, 140, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#0F172A'))
        c.setFont('Helvetica-Bold', 9)
        c.drawString(515, 180, "SENSITIVITY ANALYSIS SUMMARY (7 RISK DIMENSIONS TESTED):")
        c.setFillColor(HexColor('#334155'))
        c.setFont('Helvetica', 7.8)
        sens_lines = [
            "• Cost Overrun (+20% Capex & Opex): Net cash drops to $183.5k; ROI remains 177.3%;",
            "  payback extends by only 1 month (Month 9). Model is highly cost-resilient.",
            "• Implementation Delay (+2 Months): Net cash drops to $186.7k; payback Month 10.",
            "• Marketplace Fee Stalled (0.0 pp fee cut): Rec 2 still yields +$189.5k net cash via",
            "  discount controls and SKU pruning; payback remains Month 8.",
            "• Rec 1 Customer Attrition: Model remains profitable up to 45% order volume loss.",
            "• Conclusion: 100% of tested sensitivity bounds yield positive NPV (Min: $150.6k)."
        ]
        sy = 164
        for sline in sens_lines:
            c.drawString(515, sy, sline)
            sy -= 13

        c.showPage()

        # -------------------------------------------------------------
        # SLIDE 15: Implementation Roadmap, Governance & Decisions
        # -------------------------------------------------------------
        draw_slide_base("Turnaround Execution",
                        "Implementation Roadmap, Governance & Executive Decision",
                        "A 12-month phased turnaround plan with clear ownership, milestone gates, and four explicit leadership decisions required today.", 15)

        col_w = 274
        col_h = 410
        col_y = 42

        # Card 1: 12-Month Phased Rollout
        draw_card(40, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(55, col_y + col_h - 30, "12-Month Phased Rollout")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(55, col_y + col_h - 46, "Sequenced turnaround roadmap:")

        phases = [
            ("Q1 (Months 1–3): Quick Wins & Cash Inflow",
             "• Deploy Rec 1 discount guardrails (20% cap) & ERP rules.",
             "• Realize immediate cash surplus; Rec 1 pays back in Month 3.",
             "• Initiate Central region 3PL freight audit & contract review."),
            ("Q2 (Months 4–6): Marketplace Alignment",
             "• Complete Marketplace commission fee negotiations (-1 pp).",
             "• Implement 10% marketplace discount cap & prune 45 SKUs.",
             "• Onboard secondary 3PL carrier in Central region for SLA pilot."),
            ("Q3 (Months 7–9): System Rollout & Breakeven",
             "• Integrate automated delivery tracking and customer credits.",
             "• Cutover Central freight routing to new logistics hubs.",
             "• Entire combined portfolio achieves full breakeven in Month 8."),
            ("Q4 (Months 10–12): Steady-State Optimization",
             "• Achieve full annual steady-state run-rate (+$103k/yr).",
             "• Conduct independent Stage 6 annual BI audit & KPI review.",
             "• Institutionalize governance dashboard across commercial units.")
        ]
        py = col_y + col_h - 75
        for ptitle, b1, b2, b3 in phases:
            c.setFillColor(HexColor('#F8FAFC'))
            c.setStrokeColor(HexColor('#E2E8F0'))
            c.roundRect(50, py - 55, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#1E3A8A'))
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(58, py + 2, ptitle)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.5)
            c.drawString(58, py - 14, b1)
            c.drawString(58, py - 27, b2)
            c.drawString(58, py - 40, b3)
            py -= 76

        # Card 2: Executive Ownership Matrix
        draw_card(343, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(358, col_y + col_h - 30, "Governance & Accountabilities")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(358, col_y + col_h - 46, "Role ownership and target KPIs:")

        roles = [
            ("VP Sales & Chief Commercial Officer", "Owner: Recommendation 1 (Discount Guardrails)",
             "• Enforce 15% minimum basket margin and 20% cap.",
             "• Align sales compensation with contribution margin dollars.",
             "• KPI: % orders >20% discount (Target: <3.0%)."),
            ("VP E-Commerce & Marketplace Lead", "Owner: Recommendation 2 (Marketplace Repair)",
             "• Lead 1.0 pp fee negotiation with Amazon/Walmart.",
             "• Delist negative-margin SKUs & redirect search traffic.",
             "• KPI: Marketplace channel margin > +4.0% (from -2.55%)."),
            ("VP Supply Chain & Chief Operating Officer", "Owner: Recommendation 3 (Delivery SLA Overhaul)",
             "• Restructure Central region 3PL partner contracts.",
             "• Enforce contractual delivery penalties & automated SMS.",
             "• KPI: Central late delivery rate < 15.0% (from 58.4%)."),
            ("Chief Financial Officer & Controller", "Financial Governance & Cash Flow Tracking",
             "• Monthly variance tracking against audited Stage 4 model.",
             "• Quarterly sign-off on capex milestones & capital recovery.",
             "• Portfolio KPI: Net cash benefit > $200k over 36 months.")
        ]
        ry = col_y + col_h - 75
        for rtitle, rsub, b1, b2, b3 in roles:
            c.setFillColor(HexColor('#EFF6FF'))
            c.setStrokeColor(HexColor('#BFDBFE'))
            c.roundRect(353, ry - 55, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#0F172A'))
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(361, ry + 2, rtitle)
            c.setFillColor(HexColor('#2563EB'))
            c.setFont('Helvetica-Bold', 7.5)
            c.drawString(361, ry - 11, rsub)
            c.setFillColor(HexColor('#475569'))
            c.setFont('Helvetica', 7.2)
            c.drawString(361, ry - 24, b1)
            c.drawString(361, ry - 36, b2)
            c.drawString(361, ry - 48, b3)
            ry -= 76

        # Card 3: Explicit Decisions Requested Today
        draw_card(646, col_y, col_w, col_h)
        c.setFillColor(HexColor('#1E293B'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(661, col_y + col_h - 30, "Executive Decisions Required Today")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 8.8)
        c.drawString(661, col_y + col_h - 46, "Four formal motions for leadership approval:")

        decisions = [
            ("Decision 1: Approve $34k Initial Capex",
             "Authorize immediate allocation of $34,000 one-time implementation capex ($10k Rec 1, $12k Rec 2, $12k Rec 3) to initiate software and contract work."),
            ("Decision 2: Mandate 20% Discount Ceiling",
             "Formally approve commercial policy mandating the 20% checkout ceiling and 15% basket-level margin threshold effective Month 1."),
            ("Decision 3: Authorize Marketplace Contract Overhaul",
             "Direct commercial counsel and e-commerce teams to open formal fee negotiations and delist low-margin marketplace listings."),
            ("Decision 4: Endorse Rec 3 SLA Strategic Investment",
             "Explicitly endorse Recommendation 3 Central logistics overhaul as a strategic service-quality mandate funded by portfolio surplus.")
        ]
        dy = col_y + col_h - 75
        for dtitle, ddesc in decisions:
            c.setFillColor(HexColor('#FEF2F2'))
            c.setStrokeColor(HexColor('#FECACA'))
            c.roundRect(656, dy - 55, col_w - 20, 68, 4, fill=1, stroke=1)
            c.setFillColor(HexColor('#991B1B'))
            c.setFont('Helvetica-Bold', 8.5)
            c.drawString(664, dy + 2, dtitle)
            c.setFillColor(HexColor('#334155'))
            c.setFont('Helvetica', 7.6)
            words = ddesc.split()
            c.drawString(664, dy - 14, " ".join(words[:8]))
            c.drawString(664, dy - 27, " ".join(words[8:16]))
            c.drawString(664, dy - 40, " ".join(words[16:]))
            dy -= 76

        # Executive Sign-Off Box
        c.setFillColor(HexColor('#F8FAFC'))
        c.setStrokeColor(HexColor('#CBD5E1'))
        c.roundRect(656, col_y + 15, col_w - 20, 60, 4, fill=1, stroke=1)
        c.setFillColor(HexColor('#0F172A'))
        c.setFont('Helvetica-Bold', 8.5)
        c.drawString(664, col_y + 60, "EXECUTIVE SIGN-OFF & MANDATE:")
        c.setFillColor(HexColor('#64748B'))
        c.setFont('Helvetica', 7.5)
        c.drawString(664, col_y + 45, "Approved by: _______________________ (CEO)")
        c.drawString(664, col_y + 30, "Approved by: _______________________ (CFO)")

        c.showPage()
        c.save()
        print(f"PDF successfully generated at: {pdf_path}")

    # =========================================================================
    # PPTX GENERATION (python-pptx, 13.333 x 7.5 in, 16:9 widescreen)
    # =========================================================================
    def generate_pptx(self, pptx_path: str = "outputs/Executive_Decision_Report_Final.pptx"):
        """Generate high-fidelity 16:9 PowerPoint deliverable with native shapes, text, tables, and charts."""
        prs = pptx.Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        blank_slide_layout = prs.slide_layouts[6]

        def add_slide_header(slide, category: str, title: str, subtitle: str, page_num: int):
            # Top Banner
            banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
            banner.fill.solid()
            banner.fill.fore_color.rgb = RGBColor(15, 41, 66)
            banner.line.color.rgb = RGBColor(15, 41, 66)

            # Category Pill
            pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.12), Inches(3.2), Inches(0.24))
            pill.fill.solid()
            pill.fill.fore_color.rgb = RGBColor(37, 99, 235)
            pill.line.color.rgb = RGBColor(37, 99, 235)
            tf = pill.text_frame
            tf.text = category.upper()
            p = tf.paragraphs[0]
            p.font.size = Pt(8.5)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)

            # Title
            tb_title = slide.shapes.add_textbox(Inches(0.6), Inches(0.36), Inches(12), Inches(0.45))
            tf_title = tb_title.text_frame
            p_t = tf_title.paragraphs[0]
            p_t.text = title
            p_t.font.size = Pt(17)
            p_t.font.bold = True
            p_t.font.color.rgb = RGBColor(255, 255, 255)

            # Subtitle
            tb_sub = slide.shapes.add_textbox(Inches(0.6), Inches(0.78), Inches(12), Inches(0.35))
            tf_sub = tb_sub.text_frame
            p_s = tf_sub.paragraphs[0]
            p_s.text = subtitle
            p_s.font.size = Pt(9.5)
            p_s.font.color.rgb = RGBColor(148, 163, 184)

            # Footer
            footer_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(7.05), Inches(12.133), Inches(0.015))
            footer_line.fill.solid()
            footer_line.fill.fore_color.rgb = RGBColor(226, 232, 240)
            footer_line.line.color.rgb = RGBColor(226, 232, 240)

            tb_f = slide.shapes.add_textbox(Inches(0.6), Inches(7.1), Inches(8), Inches(0.3))
            tf_f = tb_f.text_frame
            p_f = tf_f.paragraphs[0]
            p_f.text = "Simulated Omnichannel Retail Data (2023–2025) | Audited Stage 4 ROI Engine | Capstone Deliverable"
            p_f.font.size = Pt(8)
            p_f.font.color.rgb = RGBColor(100, 116, 139)

            tb_num = slide.shapes.add_textbox(Inches(10.5), Inches(7.1), Inches(2.2), Inches(0.3))
            tf_num = tb_num.text_frame
            p_n = tf_num.paragraphs[0]
            p_n.text = f"Slide {page_num} of 15"
            p_n.font.size = Pt(8)
            p_n.font.color.rgb = RGBColor(100, 116, 139)
            p_n.alignment = PP_ALIGN.RIGHT

        def add_card(slide, x, y, w, h, bg_color=RGBColor(255, 255, 255), border_color=RGBColor(226, 232, 240)):
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
            card.fill.solid()
            card.fill.fore_color.rgb = bg_color
            card.line.color.rgb = border_color
            card.line.width = Pt(1)
            return card

        # Slide Outline list for generation
        slides_info = [
            (1, "Title Slide"),
            (2, "Executive Decision Brief"),
            (3, "Business Context & Objectives"),
            (4, "Data & Methodology"),
            (5, "Data Quality & Financial Reconciliation"),
            (6, "Revenue & Growth Trends"),
            (7, "Profitability Diagnosis"),
            (8, "Discount Economics"),
            (9, "Channel & Regional Performance"),
            (10, "Customer, Delivery, & Returns"),
            (11, "Recommendation 1 — Discount Guardrails"),
            (12, "Recommendation 2 — Marketplace Margin Repair"),
            (13, "Recommendation 3 — Delivery SLA & Retention"),
            (14, "Financial Business Case"),
            (15, "Implementation Roadmap & Executive Decision"),
        ]

        # -------------------------------------------------------------
        # Slide 1: Title Slide (PPTX)
        # -------------------------------------------------------------
        s1 = prs.slides.add_slide(blank_slide_layout)
        bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg1.fill.solid()
        bg1.fill.fore_color.rgb = RGBColor(11, 25, 44)
        bg1.line.color.rgb = RGBColor(11, 25, 44)

        tb = s1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.5), Inches(2.2))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = "DATA ANALYTICS & BUSINESS INTELLIGENCE CAPSTONE"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = RGBColor(56, 189, 248)

        p2 = tf.add_paragraph()
        p2.text = "Executive Decision Report:"
        p2.font.size = Pt(36)
        p2.font.bold = True
        p2.font.color.rgb = RGBColor(255, 255, 255)

        p3 = tf.add_paragraph()
        p3.text = "Retail Margin Turnaround Strategy"
        p3.font.size = Pt(36)
        p3.font.bold = True
        p3.font.color.rgb = RGBColor(56, 189, 248)

        p4 = tf.add_paragraph()
        p4.text = "Three Sequenced Strategic Decisions to Lift Annual Profit by +$103k and Deliver $200.7k 36-Month Net Cash Benefit"
        p4.font.size = Pt(15)
        p4.font.color.rgb = RGBColor(148, 163, 184)

        # 3 Meta Cards
        c1 = add_card(s1, 0.8, 4.2, 3.6, 2.3, RGBColor(30, 41, 59), RGBColor(51, 65, 85))
        tf1 = c1.text_frame
        tf1.text = "AUTHOR & CONSULTANT\n\nGurusaiprasadreddy\nSenior BI Consultant & Analytics Lead\nRabTech Academy Capstone"
        for i, p in enumerate(tf1.paragraphs):
            p.font.color.rgb = RGBColor(255, 255, 255) if i == 2 else RGBColor(148, 163, 184)
            p.font.size = Pt(13) if i == 2 else Pt(9.5)
            p.font.bold = (i in [0, 2])

        c2 = add_card(s1, 4.8, 4.2, 3.6, 2.3, RGBColor(30, 41, 59), RGBColor(51, 65, 85))
        tf2 = c2.text_frame
        tf2.text = "AUDIENCE & GOVERNANCE\n\nExecutive Leadership Team\nChief Executive Officer & CFO\nReporting Period: October 2026"
        for i, p in enumerate(tf2.paragraphs):
            p.font.color.rgb = RGBColor(255, 255, 255) if i == 2 else RGBColor(148, 163, 184)
            p.font.size = Pt(13) if i == 2 else Pt(9.5)
            p.font.bold = (i in [0, 2])

        c3 = add_card(s1, 8.8, 4.2, 3.6, 2.3, RGBColor(30, 41, 59), RGBColor(51, 65, 85))
        tf3 = c3.text_frame
        tf3.text = "DATASET & AUDIT STATUS\n\n11,996 Clean Orders\nScope: Omnichannel Retail ($3.37M Sales)\nAudit Status: PASSED (75/75 Tests)"
        for i, p in enumerate(tf3.paragraphs):
            p.font.color.rgb = RGBColor(16, 185, 129) if i == 4 else (RGBColor(255, 255, 255) if i == 2 else RGBColor(148, 163, 184))
            p.font.size = Pt(13) if i == 2 else Pt(9.5)
            p.font.bold = (i in [0, 2, 4])

        # -------------------------------------------------------------
        # Slides 2 to 15 (PPTX)
        # -------------------------------------------------------------
        deck_configs = [
            (2, "Executive Summary", "Executive Decision Brief: Reversing Margin Decay",
             "Revenue grew +56% since 2023, but profit margin collapsed from 15.4% to 11.9%. Three sequenced decisions recover +$103k/yr.",
             None, "three_cards_brief"),
            (3, "Commercial Setting", "Business Context & Strategic Objectives",
             "Analyzing 11,996 transactions across three fulfillment channels, five geographic territories, and three product categories.",
             None, "three_cards_context"),
            (4, "Governance & Pipeline", "Data Governance, Cleaning Pipeline & Analytics Methodology",
             "A reproducible, 6-stage deterministic pipeline transforming 12,400 raw entries into 11,996 audited, reliable transaction records.",
             None, "three_cards_methods"),
            (5, "Data Quality & Audit", "Data Quality & Financial Reconciliation Waterfall",
             "Unadjusted raw data overstates revenue by $738.8k (+21.9%) and profit by $194.6k (+42.5%). Audited metrics prevent flawed capital decisions.",
             'waterfall', "chart_table_s5"),
            (6, "Top-Line Performance", "Revenue & Order Volume Trajectory (2023–2025)",
             "Annual sales climbed from $896.6k to $1.40M (+56.2%) driven by order volume expansion (+61.7%), while AOV held steady at ~$281.",
             'revenue_orders', "chart_table_s6"),
            (7, "Margin Diagnosis", "Profitability Diagnosis: The Growth vs. Margin Decoupling",
             "While annual revenue grew +56.2%, dollar profit grew only +20.7%, resulting in a net -3.51 percentage point collapse in contribution margin.",
             'margin_decay', "chart_table_s7"),
            (8, "Pricing Economics", "Discount Economics: The 20% Discount Loss Cliff",
             "Discounts above 20% destroy unit profitability: 1,605 orders generated -$40,094 in direct losses. Blunt cancellations risk customer contagion.",
             'discount_cliff', "chart_table_s8"),
            (9, "Channel & Regional Mix", "Channel Economics & Regional Operational Bottlenecks",
             "Marketplace revenue share expanded to 26% while losing -2.55% on every dollar sold. Central region logistics suffer a 58.4% late delivery rate.",
             'channel_region', "chart_table_s9"),
            (10, "Fulfillment & Retention", "Delivery Timeliness, Return Rates & Retention Erosion",
             "Late deliveries suffer a 14.9% return rate (3.1x on-time rate). Annual customer retention dropped from 54.4% to 49.7% (-4.7 pp).",
             'returns_retention', "chart_table_s10"),
            (11, "Recommendation 1", "Recommendation 1: Automated Discount Guardrails",
             "Cap standard checkout discounts at 20% and enforce a 15% minimum basket margin. Uplift: +$66,332/yr | Payback: Month 3.",
             None, "three_cards_r1"),
            (12, "Recommendation 2", "Recommendation 2: Marketplace Margin Repair",
             "Renegotiate platform fees by 1.0 pp, impose a 10% channel discount cap, and prune unprofitable SKUs. Uplift: +$29,352/yr | Payback: Month 12.",
             None, "three_cards_r2"),
            (13, "Recommendation 3", "Recommendation 3: Delivery SLA & Customer Retention Overhaul",
             "Overhaul Central region 3PL logistics to reduce late deliveries from 58% to 15%. Standalone deficit: -$18.8k; strategic brand investment.",
             None, "three_cards_r3"),
            (14, "Portfolio Financial Model", "Financial Business Case: Multi-Scenario ROI & Sensitivity",
             "Audited 36-month portfolio delivers $200,723 net cash benefit (232.7% ROI, Month 8 payback). Positive across all sensitivity stress tests.",
             'cash_flow', "chart_table_s14"),
            (15, "Turnaround Execution", "Implementation Roadmap, Governance & Executive Decision",
             "A 12-month phased turnaround plan with clear ownership, milestone gates, and four explicit leadership decisions required today.",
             None, "three_cards_r15"),
        ]

        for pnum, cat, title, sub, chart_key, layout_type in deck_configs:
            slide = prs.slides.add_slide(blank_slide_layout)
            add_slide_header(slide, cat, title, sub, pnum)

            if chart_key and chart_key in self.chart_paths:
                # Standard Split Layout (Chart on left, cards/table on right)
                slide.shapes.add_picture(self.chart_paths[chart_key], Inches(0.6), Inches(1.35), width=Inches(5.8))
                right_card = add_card(slide, 6.6, 1.35, 6.133, 5.5)
                tf_r = right_card.text_frame
                tf_r.word_wrap = True

                if layout_type == "chart_table_s5":
                    tf_r.text = "Financial Reconciliation Summary\n\n• Raw Sales: $4,112,442 (12,400 rows, $652k profit)\n• Exact Duplicates Removed: -400 rows (-$185,341 rev, -$36,702 profit)\n• Dropped Unrecoverable: -4 rows (-$1,124 rev, -$289 profit)\n• Quantity Outliers Corrected: -28 rows (-$552,349 rev, -$157,612 profit)\n• Final Clean Sales: $3,373,628 (11,996 rows, $458,058 profit)\n\nAudit Caveats:\n• 607 low-severity profit rounding deviations (<$0.05 penny rounding).\n• 407 high-value legitimate B2B bulk orders retained above IQR fence.\n• Raw data overstates revenue by $738.8k and profit by $194.6k."
                elif layout_type == "chart_table_s6":
                    tf_r.text = "Top-Line Growth Dynamics (2023–2025)\n\n• 2023: $896,588 Sales | 3,079 Orders | 524 Customers | AOV $291.19\n• 2024: $1,076,644 Sales (+20.1%) | 3,939 Orders | 1,003 Customers | AOV $273.33\n• 2025: $1,400,397 Sales (+30.1%) | 4,978 Orders | 1,376 Customers | AOV $281.32\n\nKey Strategic Insights:\n• Overall 3-year revenue growth: +56.2%; order volume growth: +61.7%.\n• Stable Average Order Value (~$281) proves growth is volume-driven.\n• Top 20% of customers generate 66.1% of revenue ($2.23M).\n• Customer base nearly tripled (+162.6%), subsidized by aggressive price discounts."
                elif layout_type == "chart_table_s7":
                    tf_r.text = "Product Category Margin Asymmetry\n\n• Office Supplies: $432,492 Sales (12.8%) | $152,229 Profit | 35.20% Margin\n• Furniture: $1,293,350 Sales (38.3%) | $157,456 Profit | 12.17% Margin\n• Technology: $1,647,786 Sales (48.8%) | $148,373 Profit | 9.00% Margin\n• Total Portfolio: $3,373,628 Sales | $458,058 Profit | 13.58% Margin\n\nDiagnostic Takeaway:\n• Growth was concentrated in Technology (48.8% sales) and Furniture (38.3%),\n  which carry weak gross margins and high freight/marketplace fees.\n• Office Supplies earns one third of company profit on just 13% of revenue.\n• While revenue expanded +56%, margin collapsed by -3.51 percentage points."
                elif layout_type == "chart_table_s8":
                    tf_r.text = "The 20% Discount Cliff & Contagion Risk\n\nMargin Trajectory by Discount Band:\n• 0% Discount: 28.74% Margin | 4 Loss Orders (0.1%)\n• 1–10% Discount: 22.37% Margin | 19 Loss Orders (0.8%)\n• 11–20% Discount: 11.79% Margin | 215 Loss Orders (7.3%)\n• 21–30% Discount: -0.56% Margin | 487 Loss Orders (25.0%)\n• >30% Discount: -22.55% Margin | 854 Loss Orders (54.7%)\n\nCritical Contagion Disclosure:\n• 1,605 orders >20% discount generated -$40,094 in direct losses.\n• These orders belong to 825 customers who ALSO generated $741,419\n  in sales and $152,140 in profit on profitable orders (<=20% discount).\n• Blunt cancellations risk triggering customer attrition. Basket margin\n  rules and escalation workflows preserve relationship lifetime value."
                elif layout_type == "chart_table_s9":
                    tf_r.text = "Channel Economics & Central Logistics Failure\n\nChannel Economics:\n• Retail Store: $1.16M Sales (34.4%) | $245.9k Profit | 21.22% Margin\n• Online Store: $1.53M Sales (45.4%) | $229.6k Profit | 15.00% Margin\n• Marketplace: $684.1k Sales (20.3%) | -$17.4k Profit | -2.55% Margin\n• Marketplace mix expanded from 12.3% to 26.2%, cannibalizing profits.\n\nRegional Fulfillment Bottleneck:\n• West (11.9% late) and North (18.7% late) perform reliably.\n• Central region delivered 573 of 981 orders late (58.41% late delivery rate).\n• Carrier contracts lack SLA penalties, causing massive delivery backlogs."
                elif layout_type == "chart_table_s10":
                    tf_r.text = "Delivery Delays, Returns, & Customer Retention\n\nStatistical Hypothesis 3 Results:\n• On-time deliveries (<=5 days): 4.78% return rate across 9,266 orders.\n• Late deliveries (>5 days): 14.91% return rate across 2,730 orders (3.1x higher).\n• Welch's t-test: t = 14.13, p = 4.80e-44 (statistically significant).\n\nCustomer Retention Erosion:\n• Annual cohort retention dropped from 54.39% to 49.65% (-4.7 pp).\n• 95.0% of orders come from repeat buyers; losing loyalty destroys LTV.\n\nObservational Caveat:\n• Historical association does not prove counterfactual causation. While late\n  deliveries correlate with returns, returns also depend on category sizing\n  and buyer expectations."
                elif layout_type == "chart_table_s14":
                    tf_r.text = "Audited Multi-Scenario Financial Case\n\nPortfolio Performance Matrix:\n• Conservative: +$82.5k/yr Uplift | $99.7k Total Cost | +$119,555 Net Cash | 119.9% ROI | Payback M12 | NPV $97,798\n• Base Case: +$103.0k/yr Uplift | $86.2k Total Cost | +$200,723 Net Cash | 232.7% ROI | Payback M8 | NPV $168,399\n• Optimistic: +$121.8k/yr Uplift | $77.6k Total Cost | +$256,068 Net Cash | 329.9% ROI | Payback M5 | NPV $215,709\n\nSensitivity Robustness (7 Dimensions):\n• Cost Overrun (+20% Capex/Opex): Net cash remains $183.5k; ROI 177.3%.\n• Implementation Delay (+2 Mos): Net cash remains $186.7k; payback M10.\n• Marketplace Fee Cut Stalled (0.0 pp): Net cash remains $189.5k; payback M8.\n• 100% of tested sensitivity scenarios produce strongly positive NPV."

            else:
                # 3-Card Layout for Strategy, Context, and Recommendations
                c1 = add_card(slide, 0.6, 1.35, 3.8, 5.5)
                c2 = add_card(slide, 4.766, 1.35, 3.8, 5.5)
                c3 = add_card(slide, 8.933, 1.35, 3.8, 5.5)

                tf1, tf2, tf3 = c1.text_frame, c2.text_frame, c3.text_frame
                tf1.word_wrap = tf2.word_wrap = tf3.word_wrap = True

                if layout_type == "three_cards_brief":
                    tf1.text = "1. THE BUSINESS PROBLEM\n\n• Revenue climbed +56.2% ($897k -> $1.40M),\n  but profit rose only +20.7%.\n• Weighted margin dropped -3.51 pp\n  (15.44% in 2023 down to 11.93% in 2025).\n• Discounts >20% generate -$40,094 losses.\n• Marketplace channel fee (15%) causes -2.55%\n  negative margin on $684k sales.\n• Central region shipping delays (58.4% late)\n  triple returns (14.9%) and erode retention."
                    tf2.text = "2. THREE STRATEGIC DECISIONS\n\nDecision 1: Discount Guardrails\n• Hard cap at 20%; 15% basket margin floor.\n• Uplift: +$66,332/yr | Capex: $10k | M3 Payback.\n\nDecision 2: Marketplace Margin Repair\n• Renegotiate fee to 14% (-1 pp); cap discount 10%.\n• Uplift: +$29,352/yr | Capex: $12k | M12 Payback.\n\nDecision 3: Delivery SLA & Retention\n• Central 3PL overhaul; reduce late to 15%.\n• Uplift: +$7,314/yr | Capex: $12k | Brand SLA."
                    tf3.text = "3. BASE FINANCIALS & RISKS\n\nAudited Base Case Summary:\n• Annual Uplift: +$102,997/yr (+61.6% profit)\n• 36-Month Total Cost: $86,250\n• 36-Month Net Cash: +$200,723\n• Net ROI: 232.72% | 10% NPV: $168,399\n• Portfolio Payback: Month 8\n\nCritical Risk Disclosures:\n• Rec 3 Standalone Deficit: -$18,795 over 36m.\n  Funded by Rec 1 & Rec 2 portfolio surplus.\n• Rec 1 Contagion Risk: 825 buyers also placed\n  $741k in profitable orders. Use basket rules."

                elif layout_type == "three_cards_context":
                    tf1.text = "Omnichannel Architecture\n\n• Retail Store: 3,869 Orders | $1.16M Sales (34.4%)\n  Profit: $245.9k | Margin: 21.22%\n  Physical anchors with strong customer attachment.\n\n• Online Web Store: 5,467 Orders | $1.53M Sales (45.4%)\n  Profit: $229.6k | Margin: 15.00%\n  Primary digital volume driver with healthy unit profit.\n\n• Marketplace: 2,660 Orders | $684.1k Sales (20.3%)\n  Profit: -$17.4k | Margin: -2.55%\n  Fastest growing channel but deeply unprofitable."
                    tf2.text = "Core Business Questions\n\n• Q1: Decoupling Mechanism\n  Why did top-line growth (+56%) fail to flow to\n  bottom-line earnings (+21%)?\n\n• Q2: Loss Concentration\n  Which discount bands, regions, and channels\n  destroy capital through cross-subsidization?\n\n• Q3: Fulfillment & Churn\n  How much margin is lost through late delivery\n  returns and customer retention decay?\n\n• Q4: Costed Turnaround\n  What sequenced actions deliver positive ROI?"
                    tf3.text = "Strategic Imperatives\n\n• Volume to Value Focus\n  Shift corporate KPIs from top-line revenue to net\n  contribution profit after all channel fees and freight.\n\n• Prevent Churn Contagion\n  Do not bluntly cancel orders; apply basket-level\n  margin governance to protect multi-order buyers.\n\n• Partner Accountability\n  Renegotiate marketplace fees and 3PL contracts\n  with strict performance penalty clauses.\n\n• Retention Protection\n  Repeat buyers drive 95% of orders. Service delivery\n  quality is essential for customer lifetime value."

                elif layout_type == "three_cards_methods":
                    tf1.text = "Dataset Coverage & Scope\n\n• Reporting Period: 2023-01-01 to 2025-12-31\n• Raw Transactions: 12,400 rows across 20 fields\n• Clean Transactions: 11,996 fully validated rows\n• Coverage: 5 US regions, 3 product categories\n• Customer Base: 2,116 unique accounts\n\nSimulated-Data Disclosure:\n• The dataset represents simulated omnichannel\n  retail operations designed for BI stress testing.\n• Observational data establishes statistical correlation\n  rather than clinical counterfactual causation."
                    tf2.text = "6-Stage Cleaning Pipeline\n\n• Stage 1: Ingestion & Schema Typing\n  Standardized date parsing & numeric type casting.\n• Stage 2: Exact Deduplication\n  Purged 400 identical order rows.\n• Stage 3: Categorical Standardization\n  Reduced region variants from 29 to 5.\n• Stage 4: Outlier Treatment\n  Corrected 28 extreme quantity keying errors to median.\n• Stage 5: Hierarchy-Aware Imputation\n  Customer-mode imputation for missing regions.\n• Stage 6: Automated Validation Gates\n  12 automated test gates (11 passed, 1 info note)."
                    tf3.text = "Analytical Methods\n\n• Volume-Weighted KPI Engine\n  Avoided simple average margin distortion by\n  weighting all margins strictly by transaction dollars.\n\n• Hypothesis Testing Framework\n  Conducted two-sample Welch's t-tests on discount\n  margins, marketplace drag, and delivery returns.\n\n• Cohort Retention Tracking\n  Tracked annual customer repeat rates (54.4% -> 49.7%).\n\n• Dynamic 36-Month Cash Flow Model\n  Monthly cash flow engine incorporating launch timing,\n  ramp-up curves, Capex/Opex, and 10% WACC discounting."

                elif layout_type == "three_cards_r1":
                    tf1.text = "Policy & System Architecture\n\n• 20% Hard Ceiling at Checkout\n  Configure e-commerce checkout and ERP order entry\n  to reject single-item discounts exceeding 20%.\n\n• 15% Basket Margin Floor\n  Enforce total order contribution margin check.\n  Orders falling below 15% margin trigger escalation.\n\n• Tiered Commercial Escalation\n  Discounts 15%–20% require Sales Director approval;\n  discounts >20% require Regional VP sign-off.\n\n• Daily Margin Exception Audit\n  Automated daily audit to CFO detailing rep compliance."
                    tf2.text = "Audited Financial Business Case\n\nBase-Case 36-Month Projections:\n• Annual Steady-State Uplift: +$66,331.86/yr\n• Annual Revenue Delta: +$58,959.97/yr\n• Implementation Capex: $10,000.00\n• Annual Recurring Opex: $3,999.96/yr\n• 36-Month Total Cost: $21,999.88\n• 36-Month Net Cash Benefit: +$171,468.04\n• Net ROI: 779.40%\n• Breakeven Payback: Month 3 (Immediate)\n\nFast Cash Generation:\n• Rec 1 self-funds the entire turnaround portfolio."
                    tf3.text = "Contagion Mitigation & Roadmap\n\nPreventing Customer Churn Contagion:\n• 825 buyers of >20% discounted goods also deliver\n  $741k in profitable purchases.\n• Transition large buyers from transactional discounts\n  to structured annual volume rebates.\n• Realine sales incentives to contribution profit dollars.\n\nImplementation Roadmap:\n• Month 1: ERP pricing logic configuration ($5k).\n• Month 2: Sales team enablement & training ($5k).\n• Month 3: Go-live on direct online & retail stores.\n• Owner: VP Sales & Chief Commercial Officer."

                elif layout_type == "three_cards_r2":
                    tf1.text = "Three-Pillar Margin Recovery\n\n• Pillar 1: 1.0 pp Fee Cut (15% -> 14%)\n  Leverage annual platform volume ($684k) to\n  negotiate a 1.0 pp reduction in platform take-rate.\n\n• Pillar 2: 10% Channel Discount Cap\n  Impose a strict 10% maximum promotional ceiling\n  on all marketplace listings to protect margins.\n\n• Pillar 3: Catalog Rationalization\n  Delist low-margin, bulky Furniture and Tech\n  accessories with gross margins below 25%.\n\n• Pillar 4: Direct Channel Redirection\n  Insert branded packaging cards offering $10 welcome\n  vouchers for direct online web store purchases."
                    tf2.text = "Audited Financial Business Case\n\nBase-Case 36-Month Projections:\n• Annual Steady-State Uplift: +$29,352.04/yr\n• Annual Revenue Delta: +$20,869.23/yr\n• Implementation Capex: $12,000.00\n• Annual Recurring Opex: $6,000.00/yr\n• 36-Month Total Cost: $29,000.00\n• 36-Month Net Cash Benefit: +$48,049.10\n• Net ROI: 165.69%\n• Breakeven Payback: Month 12\n\nMarketplace Contribution:\n• Transforms channel from -$17.4k loss to +$12k profit."
                    tf3.text = "Negotiation Governance & Risks\n\nNegotiation Strategy & Leverage:\n• Position company as high-volume tier-1 seller.\n• Offer catalog exclusivity and co-op ad spend.\n• Fallback sensitivity: Even if fee cut is 0.0 pp,\n  discount controls and SKU pruning net +$189.5k.\n\nImplementation Roadmap:\n• Month 4: Open platform fee negotiations.\n• Month 5: Channel listing automation setup ($12k).\n• Month 6: Enforce 10% cap and prune 45 SKUs.\n• Month 12: Payback reached; full run-rate.\n• Owner: VP E-Commerce & Marketplace Lead."

                elif layout_type == "three_cards_r3":
                    tf1.text = "Logistics Overhaul Plan\n\n• Central Carrier Re-Contracting\n  Terminate underperforming exclusive 3PL contract;\n  onboard secondary regional carrier in Central.\n\n• Strict SLA Penalty Guarantees\n  Contractually enforce 95% on-time delivery with\n  freight credit penalties on late orders.\n\n• Hub Re-Routing\n  Re-route shipments through Dallas/Chicago hubs,\n  cutting Central transit time by 2.2 days.\n\n• Proactive Customer Outreach\n  Automated delivery tracking SMS and proactive $15\n  gift credits for delayed packages."
                    tf2.text = "Audited Financials & Deficit\n\nStandalone Economics (Base Case):\n• Annual Return Cost Savings: +$1,911.00/yr\n• Annual Retention Profit: +$5,402.52/yr\n• Total Annual Benefit: +$7,313.52/yr\n• Annual Recurring Opex: $9,000.00/yr\n• Net Annual Run-Rate: -$1,686.48/yr (Deficit)\n• Implementation Capex: $12,000.00\n• 36-Month Total Cost: $35,250.00\n• 36-Month Net Cash: -$18,794.58 (Deficit)\n• Net ROI: -53.32%\n• Standalone Payback: Never (>36 Months)\n\nTransparent disclosure of operating drag."
                    tf3.text = "Strategic Justification & Options\n\nExecutive Decision Options:\n• Option A: Cost Redesign\n  Re-scope carrier software integrations to compress\n  opex from $9.0k to $5.0k/yr, reaching breakeven.\n\n• Option B: 6-Month Pilot Validation\n  Run pilot in Central to validate whether retention\n  uplift exceeds modeled +4.5 pp before full rollout.\n\n• Option C: Strategic Brand Approval (Rec.)\n  Approve as essential brand & SLA investment.\n  Funded by portfolio surplus from Rec 1 ($171k) and\n  Rec 2 ($48k). Combined portfolio nets +$200.7k cash.\n• Owner: VP Supply Chain & COO."

                elif layout_type == "three_cards_r15":
                    tf1.text = "12-Month Phased Rollout\n\n• Q1 (Months 1–3): Quick Wins & Cash Inflow\n  Deploy Rec 1 discount guardrails (20% cap).\n  Cash payback achieved in Month 3.\n  Initiate Central 3PL carrier audit.\n\n• Q2 (Months 4–6): Marketplace Alignment\n  Renegotiate marketplace fees (-1 pp).\n  Implement 10% discount cap & prune 45 SKUs.\n  Launch Central SLA carrier pilot.\n\n• Q3 (Months 7–9): System Rollout\n  Deploy automated delivery tracking and alerts.\n  Combined portfolio reaches breakeven in Month 8.\n\n• Q4 (Months 10–12): Steady-State Optimization\n  Achieve full steady-state uplift (+$103k/yr)."
                    tf2.text = "Executive Ownership Matrix\n\n• Rec 1 Lead: VP Sales & Chief Commercial Officer\n  Enforce 15% basket margin; sales quota alignment.\n  Target: % orders >20% discount < 3.0%.\n\n• Rec 2 Lead: VP E-Commerce & Marketplace\n  Lead fee negotiations and catalog delistings.\n  Target: Marketplace margin > +4.0%.\n\n• Rec 3 Lead: VP Supply Chain & COO\n  Logistics contracts, warehouse SLAs, transit alerts.\n  Target: Central late delivery rate < 15.0%.\n\n• Financial Governance: CFO & Controller\n  Monthly variance reviews against Stage 4 budget."
                    tf3.text = "Decisions Requested Today\n\n1. Approve $34k Initial Capex Allocation\n   Authorize immediate $34,000 funding across the\n   three initiatives to begin software and carrier work.\n\n2. Mandate 20% Discount Ceiling Policy\n   Approve commercial policy enforcing 20% cap and\n   15% basket minimum margin effective Month 1.\n\n3. Authorize Marketplace Fee Negotiations\n   Direct commercial team to open contract talks and\n   enforce 10% listing discount ceiling.\n\n4. Endorse Rec 3 SLA Strategic Investment\n   Approve Central logistics overhaul as a strategic\n   mandate funded by portfolio cash surplus."

                # Set formatting on text frames
                for tf_x in [tf1, tf2, tf3]:
                    for para in tf_x.paragraphs:
                        para.font.size = Pt(8.5)
                        para.font.color.rgb = RGBColor(30, 41, 59)

        prs.save(pptx_path)
        print(f"PPTX successfully generated at: {pptx_path}")

    def run_all(self):
        """Execute full presentation generation and verification pipeline."""
        print("Starting Stage 5 Presentation Generation...")
        self.generate_all_charts()

        pdf_path = os.path.join(self.output_dir, "Executive_Decision_Report_Final.pdf")
        pptx_path = os.path.join(self.output_dir, "Executive_Decision_Report_Final.pptx")

        self.generate_pdf(pdf_path)
        self.generate_pptx(pptx_path)

        # Verification
        pdf_size = os.path.getsize(pdf_path)
        pptx_size = os.path.getsize(pptx_path)
        pdf_sha = compute_sha256(pdf_path)
        pptx_sha = compute_sha256(pptx_path)

        print("\n--- DELIVERABLES GENERATED SUCCESSFULLY ---")
        print(f"PDF Deliverable:  {pdf_path} | Size: {pdf_size:,} bytes | SHA256: {pdf_sha}")
        print(f"PPTX Deliverable: {pptx_path} | Size: {pptx_size:,} bytes | SHA256: {pptx_sha}")

        return {
            "pdf_path": pdf_path,
            "pdf_size": pdf_size,
            "pdf_sha256": pdf_sha,
            "pptx_path": pptx_path,
            "pptx_size": pptx_size,
            "pptx_sha256": pptx_sha
        }


if __name__ == "__main__":
    generator = PresentationGenerator()
    results = generator.run_all()
