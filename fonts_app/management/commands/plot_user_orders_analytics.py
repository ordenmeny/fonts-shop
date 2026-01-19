from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

from fonts_app.models import OrderItem, LicenseType


def _top_n_with_other(series: pd.Series, top_n: int) -> pd.Series:
    series = series.sort_values(ascending=False)
    if len(series) <= top_n:
        return series
    head = series.iloc[:top_n]
    other_sum = series.iloc[top_n:].sum()
    head.loc["Other"] = other_sum
    return head


class Command(BaseCommand):
    help = "Build matplotlib charts for user orders analytics (fonts licenses)."

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, required=True)
        parser.add_argument("--out-dir", type=str, default="analytics_plots")
        parser.add_argument("--top-n", type=int, default=12)

    def handle(self, *args: Any, **options: Any):
        user_id: int = options["user_id"]
        out_dir = Path(options["out_dir"]).resolve()
        top_n: int = options["top_n"]

        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as exc:
            raise CommandError(f"User with id={user_id} not found") from exc

        qs = (
            OrderItem.objects.select_related(
                "order",
                "font_face_with_price__face__font",
                "font_face_with_price__face__style",
            )
            .filter(order__user=user, font_face_with_price__isnull=False)
            .values(
                "order__created_at",
                "font_face_with_price__license_type",
                "font_face_with_price__price",
                "font_face_with_price__face__font__name",
                "font_face_with_price__face__style__name",
            )
        )

        df = pd.DataFrame.from_records(qs)

        if df.empty:
            self.stdout.write(self.style.WARNING("No data. Nothing to plot."))
            return

        license_map = dict(LicenseType.choices)

        df["created_at"] = pd.to_datetime(df["order__created_at"], utc=True, errors="coerce")
        df["license_type_label"] = df["font_face_with_price__license_type"].map(license_map).astype(str)
        df["price"] = df["font_face_with_price__price"].astype(float)
        df["font_name"] = df["font_face_with_price__face__font__name"].astype(str)
        df["style_name"] = df["font_face_with_price__face__style__name"].astype(str)

        by_font = df.groupby("font_name").size()
        by_license = df.groupby("license_type_label").size()
        by_style = df.groupby("style_name").size()

        revenue_total = float(df["price"].sum())

        df["month"] = df["created_at"].dt.to_period("M").astype(str)
        by_month = df.groupby("month").size().sort_index()
        revenue_by_month = df.groupby("month")["price"].sum().sort_index()

        by_font_top = _top_n_with_other(by_font, top_n)
        by_style_top = _top_n_with_other(by_style, top_n)
        by_license_top = by_license.sort_values(ascending=False)

        out_dir.mkdir(parents=True, exist_ok=True)

        now = timezone.now().strftime("%Y%m%d_%H%M%S")
        prefix = f"user_{user_id}_{now}"

        plt.close("all")

        # 1) Bar: by font
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        ax.bar(by_font_top.index.tolist(), by_font_top.values.tolist())
        ax.set_title("Licenses count by font")
        ax.set_xlabel("Font")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45, labelsize=9)
        fig.tight_layout()
        p1 = out_dir / f"{prefix}_by_font.png"
        fig.savefig(p1, dpi=160)

        # 2) Pie: by license type
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        ax.pie(
            by_license_top.values.tolist(),
            labels=by_license_top.index.tolist(),
            autopct="%1.1f%%",
            startangle=90,
        )
        ax.set_title("Licenses count by license type")
        fig.tight_layout()
        p2 = out_dir / f"{prefix}_by_license.png"
        fig.savefig(p2, dpi=160)

        # 3) Bar: by style
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        ax.bar(by_style_top.index.tolist(), by_style_top.values.tolist())
        ax.set_title("Licenses count by style")
        ax.set_xlabel("Style")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45, labelsize=9)
        fig.tight_layout()
        p3 = out_dir / f"{prefix}_by_style.png"
        fig.savefig(p3, dpi=160)

        # 4) Line: licenses by month
        fig = plt.figure(figsize=(12, 5))
        ax = fig.add_subplot(111)
        ax.plot(by_month.index.tolist(), by_month.values.tolist(), marker="o")
        ax.set_title("Licenses count by month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45, labelsize=9)
        fig.tight_layout()
        p4 = out_dir / f"{prefix}_by_month.png"
        fig.savefig(p4, dpi=160)

        # 5) Line: revenue by month
        fig = plt.figure(figsize=(12, 5))
        ax = fig.add_subplot(111)
        ax.plot(revenue_by_month.index.tolist(), revenue_by_month.values.tolist(), marker="o")
        ax.set_title("Revenue by month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue")
        ax.tick_params(axis="x", rotation=45, labelsize=9)
        fig.tight_layout()
        p5 = out_dir / f"{prefix}_revenue_by_month.png"
        fig.savefig(p5, dpi=160)

        self.stdout.write(self.style.SUCCESS("Charts saved:"))
        self.stdout.write(f"  total_items: {len(df)}")
        self.stdout.write(f"  revenue_total: {round(revenue_total, 2)}")
        self.stdout.write(f"  {p1}")
        self.stdout.write(f"  {p2}")
        self.stdout.write(f"  {p3}")
        self.stdout.write(f"  {p4}")
        self.stdout.write(f"  {p5}")
