import requests
import streamlit as st
from datetime import date, timedelta

import altair as alt
import pandas as pd

API_URL = "https://api.frankfurter.dev/v1/latest"

SUPPORTED_CURRENCIES = {
    "USD": "US Dollar",
    "THB": "Thai Baht",
    "CNY": "Chinese Yuan",
    "EUR": "Euro",
    "JPY": "Japanese Yen",
    "KRW": "South Korean Won",
    "GBP": "British Pound",
    "AUD": "Australian Dollar",
    "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",
    "CAD": "Canadian Dollar",
    "BRL": "Brazilian Real",
    "ARS": "Argentine Peso",
}

FLAG_EMOJI = {
    "USD": "🇺🇸",
    "THB": "🇹🇭",
    "CNY": "🇨🇳",
    "EUR": "🇪🇺",
    "JPY": "🇯🇵",
    "KRW": "🇰🇷",
    "GBP": "🇬🇧",
    "AUD": "🇦🇺",
    "SGD": "🇸🇬",
    "HKD": "🇭🇰",
    "CAD": "🇨🇦",
    "BRL": "🇧🇷",
    "ARS": "🇦🇷",
}


def fetch_rates(base: str) -> dict:
    params = {"from": base, "to": ",".join(SUPPORTED_CURRENCIES.keys())}
    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("rates", {})


def fetch_timeseries(base: str, target: str) -> dict:
    """获取最近 7 天的时间序列汇率数据（用于小型走势图）。"""
    if base == target:
        return {}

    end = date.today()
    start = end - timedelta(days=7)

    params = {
        "from": base,
        "to": target,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    resp = requests.get(
        "https://api.frankfurter.dev/v1/timeseries", params=params, timeout=10
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("rates", {})


def main() -> None:
    st.set_page_config(
        page_title="AI FX Converter",
        page_icon="💱",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # --- 自定义现代金融科技 UI / Custom Fintech UI ---
    st.markdown(
        """
        <style>
        body {
            background: radial-gradient(circle at top, #FFF7ED 0, #FFEDD5 60%) fixed;
            color: #1F2937;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .main {
            padding-top: 3rem;
        }
        .fx-card {
            border-radius: 24px;
            background: #FFFFFF;
            border: 1px solid rgba(15,23,42,0.06);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.10);
            padding: 32px 28px;
            max-width: 720px;
            margin: 0 auto;
        }
        .fx-title {
            font-size: 28px;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #F97316;
            line-height: 1.6;
        }
        .fx-subtitle {
            font-size: 13px;
            color: #6B7280;
            line-height: 1.6;
        }
        .fx-amount-input input {
            background: #F9FAFB !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 0 !important;
            border-bottom: 2px solid #E5E7EB !important;
            box-shadow: none !important;
            font-size: 26px !important;
            font-weight: 600 !important;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        }
        .fx-amount-input input:focus {
            border: 1px solid #FDBA74 !important;
            border-bottom: 2px solid #F97316 !important;
            box-shadow: 0 0 0 1px rgba(249,115,22,0.35) !important;
            outline: none !important;
        }
        .fx-badge {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 4px 10px;
            border: 1px solid rgba(249,115,22,0.35);
            background: rgba(255,247,237,0.9);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #92400E;
        }
        .fx-badge-dot {
            width: 6px;
            height: 6px;
            border-radius: 999px;
            margin-right: 6px;
            background: linear-gradient(90deg,#FDBA74,#F97316);
        }
        .fx-gradient-text {
            background: linear-gradient(90deg,#FDBA74,#F97316);
            -webkit-background-clip: text;
            color: transparent;
        }
        /* Light card look for metrics & containers */
        div[data-testid="stMetric"], div[data-testid="stContainer"] {
            border-radius: 15px;
            border: 1px solid rgba(15,23,42,0.05);
            background: linear-gradient(135deg, #FFFFFF, #FFFAF3);
            box-shadow: 0 10px 25px -5px rgba(15,23,42,0.08);
        }
        div[data-testid="stMetric"] {
            padding: 8px 12px;
        }
        /* Swap button: white circular with orange border */
        button[kind="secondary"] {
            border-radius: 999px !important;
            border: 1px solid #F97316 !important;
            background: #FFFFFF !important;
            color: #F97316 !important;
            box-shadow: 0 8px 20px -6px rgba(249,115,22,0.35);
            padding: 6px 14px !important;
        }
        button[kind="secondary"]:hover {
            background: #F97316 !important;
            color: #FFFFFF !important;
            box-shadow: 0 10px 24px -6px rgba(249,115,22,0.55);
        }
        button[kind="secondary"] span {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 13px;
        }
        /* Sidebar & scrollbar for light theme */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg,#FFF7ED,#FFEDD5);
            border-right: 1px solid rgba(15,23,42,0.06);
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #FFFBEB;
        }
        ::-webkit-scrollbar-thumb {
            background: #FDBA74;
            border-radius: 999px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #F97316;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="fx-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:24px;">
            <div>
              <div class="fx-badge">
                <span class="fx-badge-dot"></span>
                💱 Agentic Ops · FX
              </div>
              <div style="margin-top:12px;" class="fx-title">
                <span class="fx-gradient-text">Global FX Converter</span> · 全球货币转换器
              </div>
              <div style="margin-top:6px;" class="fx-subtitle">
                A modern glassmorphism FX converter powered by the Frankfurter API.<br/>
                基于 Frankfurter 实时外汇数据的现代化、玻璃拟态货币转换体验。
              </div>
            </div>
            <div style="text-align:right;font-size:11px;color:#9ca3af;">
              <div style="margin-bottom:2px;">EN / 中文 UI</div>
              <div style="color:#6b7280;">System status: Online · 系统状态：在线</div>
            </div>
          </div>
        """,
        unsafe_allow_html=True,
    )

    # 初始化会话中的币种状态 / Initialize currency state
    if "base_code" not in st.session_state:
        st.session_state["base_code"] = "USD"
    if "target_code" not in st.session_state:
        st.session_state["target_code"] = "THB"

    # --- Main interaction / 主交互区域 ---
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("**Amount / 输入金额**")
        with st.container():
            st.markdown('<div class="fx-amount-input">', unsafe_allow_html=True)
            amount = st.number_input(
                "",
                min_value=0.0,
                value=100.0,
                step=1.0,
                key="amount_input",
            )
            st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("**Currencies / 选择币种**")
        options = list(SUPPORTED_CURRENCIES.keys())

        base_index = options.index(st.session_state["base_code"])
        target_index = options.index(st.session_state["target_code"])

        def format_currency(code: str) -> str:
            flag = FLAG_EMOJI.get(code, "🏳️")
            name = SUPPORTED_CURRENCIES.get(code, code)
            return f"{flag} {code} · {name}"

        base = st.selectbox(
            "来源货币",
            options=options,
            format_func=format_currency,
            index=base_index,
            label_visibility="collapsed",
        )
        target = st.selectbox(
            "目标货币",
            options=options,
            format_func=format_currency,
            index=target_index,
            label_visibility="collapsed",
        )

        # 更新会话中的币种选择
        st.session_state["base_code"] = base
        st.session_state["target_code"] = target

        st.write("")
        if st.button("⇄ Swap / 对调币种", key="swap_button"):
            st.session_state["base_code"], st.session_state["target_code"] = (
                st.session_state["target_code"],
                st.session_state["base_code"],
            )
            st.rerun()

    # 使用会话状态中的最新币种参与计算
    base = st.session_state["base_code"]
    target = st.session_state["target_code"]

    st.markdown("---")

    result_str = ""
    detail_str = ""
    rate_value: float | None = None
    history_data: dict = {}

    try:
        if amount > 0 and base and target:
            with st.status(
                "Fetching latest FX data… / 正在获取最新汇率…",
                expanded=False,
            ) as status:
                rates = fetch_rates(base)
                rate = rates.get(target)
                if rate is not None:
                    converted = amount * rate
                    result_str = f"{amount:,.2f} {base} ≈ {converted:,.2f} {target}"
                    detail_str = (
                        f"1 {base} ≈ {rate:.4f} {target} FX rate / 汇率"
                    )
                    rate_value = float(rate)
                    history_data = fetch_timeseries(base, target)
                    status.update(
                        label="FX data updated / 汇率数据已更新",
                        state="complete",
                        expanded=False,
                    )
                    st.toast("FX data updated / 汇率数据已更新", icon="💹")
                else:
                    detail_str = (
                        "Unable to fetch this currency pair, please try again later. / "
                        "未能获取该货币对的汇率，请稍后再试。"
                    )
                    status.update(
                        label="FX pair not available / 该货币对暂无数据",
                        state="error",
                        expanded=False,
                    )
    except Exception as exc:  # pragma: no cover - 简单错误展示
        detail_str = f"请求汇率失败：{exc}"

    st.markdown("#### Conversion Result · 转换结果")
    if result_str:
        st.markdown(
            f"""
            <div style="font-size:22px;font-weight:600;margin-bottom:4px;" class="fx-gradient-text">
              {result_str}
            </div>
            <div style="font-size:12px;color:#9ca3af;">
              {detail_str}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:13px;color:#9ca3af;">Please enter an amount and select currencies to convert. / 请输入金额并选择要转换的币种。</div>',
            unsafe_allow_html=True,
        )

    # 关键指标卡片 / Key FX metrics
    if rate_value is not None and result_str:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("FX rate / 汇率", f"{rate_value:.4f}")
        with m2:
            inv = 1.0 / rate_value if rate_value else 0.0
            st.metric("Inverse / 逆向", f"{inv:.4f}" if inv else "—")
        with m3:
            st.metric("Updated / 更新时间", date.today().isoformat())

    # 7 日汇率走势图 / 7‑day FX trend
    if history_data and rate_value is not None:
        st.markdown("##### 7‑day FX trend · 7 日汇率走势")
        rows: list[dict] = []
        for d, v in history_data.items():
            rows.append({"date": d, "rate": v.get(target)})
        if rows:
            df = pd.DataFrame(rows).dropna(subset=["rate"]).sort_values("date")
            if not df.empty:
                chart = (
                    alt.Chart(df)
                    .mark_area(
                        line={"color": "#F97316"},
                        color="rgba(249,115,22,0.20)",
                    )
                    .encode(
                        x=alt.X("date:T", title="Date"),
                        y=alt.Y("rate:Q", title=f"{base} → {target}"),
                    )
                )
                st.altair_chart(chart, use_container_width=True)

    st.markdown(
        """
        <div style="margin-top:24px;padding-top:12px;border-top:1px dashed rgba(148,163,184,0.5);font-size:11px;color:#6b7280;">
          Data source / 汇率数据来源: <span style="color:#e5e7eb;">https://api.frankfurter.dev/v1/latest</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

