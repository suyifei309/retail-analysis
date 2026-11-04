"""下载 UCI Online Retail II 数据集并转换为 parquet。

用法:
    python src/get_data.py

产出:
    data/raw/online_retail_II.zip        原始压缩包（保留，可复现）
    data/raw/*.xlsx                      解压出的原始表（只读不改）
    data/raw/online_retail_II.parquet    合并两个年度 sheet 后的轻量格式，后续秒读
"""
from pathlib import Path
import zipfile

import pandas as pd
import requests

URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
CHUNK = 1 << 20  # 1MB


def download() -> None:
    zip_path = RAW / "online_retail_II.zip"
    if zip_path.exists():
        print(f"[跳过] {zip_path.name} 已存在（{zip_path.stat().st_size / 1e6:.1f} MB）")
        return
    print(f"下载 {URL} ...")
    with requests.get(URL, timeout=300, stream=True) as r:
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(CHUNK):
                f.write(chunk)
    print(f"已下载 {zip_path.stat().st_size / 1e6:.1f} MB")


def extract_xlsx() -> Path:
    xlsx_list = list(RAW.glob("*.xlsx"))
    if xlsx_list:
        return xlsx_list[0]
    with zipfile.ZipFile(RAW / "online_retail_II.zip") as z:
        z.extractall(RAW)
    xlsx_list = list(RAW.glob("*.xlsx"))
    if not xlsx_list:
        raise FileNotFoundError("压缩包里没找到 xlsx，请检查 " + str(RAW))
    return xlsx_list[0]


def to_parquet(xlsx: Path) -> pd.DataFrame:
    out = RAW / "online_retail_II.parquet"
    if out.exists():
        print(f"[跳过] {out.name} 已存在")
        return pd.read_parquet(out)
    print(f"读取 {xlsx.name}（两个年度 sheet，约 1-3 分钟）...")
    sheets = pd.read_excel(xlsx, sheet_name=None)
    print(f"共 {len(sheets)} 个 sheet: {list(sheets)}")
    df = pd.concat(sheets.values(), ignore_index=True)
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    # Excel 读进来的文本列是 object 混型（如 Invoice 混有 int 单号与 'C' 开头退货单号、
    # Description 混有纯数字描述），无法直接写 parquet，统一转 string 类型
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].astype("string")
    df.to_parquet(out, index=False)
    print(f"已保存 {out.name}")
    return df


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    download()
    df = to_parquet(extract_xlsx())
    print("\n===== 数据概览 =====")
    print(f"行数: {len(df):,}，列数: {df.shape[1]}")
    print(f"列名: {list(df.columns)}")
    print(f"InvoiceDate 范围: {df['InvoiceDate'].min()} ~ {df['InvoiceDate'].max()}")
    missing = df.isna().mean().mul(100).round(1)
    missing = missing[missing > 0]
    print("缺失率(%):")
    print(missing.to_string() if len(missing) else "  无缺失")
    print(f"Country 数量: {df['Country'].nunique()}")


if __name__ == "__main__":
    main()
